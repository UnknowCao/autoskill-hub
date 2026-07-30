r"""Table structure issue detection (two-stage pipeline).

Stage 1 (this script): detect malformed markdown tables by comparing mammoth's
HTML output (ground-truth, preserves rowspan/colspan) against markitdown's md
output. Emit a STRUCTURED ERROR REPORT so the AI (stage 2) can locate the exact
lines to fix and reference the correct HTML structure.

Each reported error contains three pieces of information the AI needs:
  - CAUSE:          why the md is wrong (human-readable)
  - MD_LOCATION:    exact line range in the .md file (1-based, absolute)
                    + list of affected row indices within the table
  - HTML_REFERENCE: the full ground-truth <table>...</table> block + the
                    table's 1-based index in the mammoth HTML

Usage:
    from _table_detect import detect_table_issues, format_error_report

    issues = detect_table_issues(mammoth_html, md_text)
    report = format_error_report(issues, md_path="output.md")
    if issues:
        sys.exit(1)   # signal the AI driver that fixes are needed
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field


@dataclass
class TableIssue:
    """A detected table structure issue with precise location info."""

    table_index: int
    """0-based index of the table among all tables in the document."""

    issue_type: str
    """One of: vertical_merge, nested_table."""

    severity: str
    """P1 (semantic loss), P2 (structure loss only)."""

    cause: str
    """Human-readable root cause — WHY the md is wrong."""

    fixable: bool
    """Whether AI can attempt to fix this (True for vertical_merge, False for nested)."""

    # --- MD-side location (where the AI must edit) ---
    md_table_index: int = 0
    """1-based index of the table in the .md file (for human reference)."""

    md_start_line: int = 0
    """Absolute 1-based line number in the .md file where the table begins."""

    md_end_line: int = 0
    """Absolute 1-based line number in the .md file where the table ends."""

    md_affected_rows: list[int] = field(default_factory=list)
    """1-based row indices within the md table that are misaligned/missing data."""

    expected_md_cols: int = 0
    """Number of columns the md table SHOULD have (per HTML ground truth)."""

    actual_md_cols_per_row: list[int] = field(default_factory=list)
    """Current column count per row in the md table (incl. header + separator)."""

    # --- HTML-side reference (the ground truth the AI must reproduce) ---
    html_table_index: int = 0
    """1-based index of the corresponding table in mammoth HTML."""

    html_full_table: str = ""
    """The full <table>...</table> block from mammoth (untruncated)."""

    md_full_table: str = ""
    """The full md table block (untruncated, for side-by-side comparison)."""


def _extract_tables_from_html(html: str) -> list[str]:
    """Extract <table>...</table> blocks from HTML."""
    return re.findall(r"<table>.*?</table>", html, re.DOTALL)


def _extract_tables_from_md_with_lines(md_text: str) -> list[tuple[str, int, int]]:
    """Extract markdown table blocks with their absolute line ranges.

    Returns list of (table_text, start_line_1based, end_line_1based).
    A table is a contiguous block of pipe-separated lines.
    """
    tables = []
    current_lines: list[str] = []
    start_line = 0
    in_table = False
    for lineno, line in enumerate(md_text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("|"):
            if not in_table:
                start_line = lineno
                in_table = True
            current_lines.append(line)
        elif in_table:
            tables.append(("\n".join(current_lines), start_line, lineno - 1))
            current_lines = []
            in_table = False
    if in_table and current_lines:
        tables.append(("\n".join(current_lines), start_line,
                       len(md_text.splitlines())))
    return tables


def _count_md_cols_per_row(table: str) -> list[int]:
    """Count columns per row in a markdown table (incl. header + separator)."""
    cols = []
    for line in table.splitlines():
        s = line.strip()
        if s.startswith("|"):
            cols.append(s.strip("|").count("|") + 1)
    return cols


def _has_rowspan(html_table: str) -> bool:
    return "rowspan" in html_table


def _has_nested_table(html_table: str) -> bool:
    # Count <table> tags; >1 means nested
    return html_table.count("<table>") > 1


def _count_html_rows(html_table: str) -> int:
    return len(re.findall(r"<tr>", html_table))


def _count_html_cols(html_table: str) -> int:
    """Count columns from the first <tr> (accounting for colspan/rowspan)."""
    first_tr = re.search(r"<tr>(.*?)</tr>", html_table, re.DOTALL)
    if not first_tr:
        return 0
    # Expand colspan in the header row to get the true column count.
    cols = 0
    for m in re.finditer(r"<td[^>]*colspan=[\"']?(\d+)[\"']?[^>]*>", first_tr.group(1)):
        cols += int(m.group(1))
    plain_tds = len(re.findall(r"<td(?![^>]*colspan)", first_tr.group(1)))
    return cols + plain_tds if (cols or plain_tds) else len(re.findall(r"<td", first_tr.group(1)))


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def detect_table_issues(mammoth_html: str, md_text: str) -> list[TableIssue]:
    """Detect table structure issues by comparing HTML and md.

    Returns a list of TableIssue with precise line-range locations, ready for
    AI consumption via format_error_report().
    """
    html_tables = _extract_tables_from_html(mammoth_html)
    md_tables_meta = _extract_tables_from_md_with_lines(md_text)
    issues: list[TableIssue] = []

    n = min(len(html_tables), len(md_tables_meta))
    for i in range(n):
        ht = html_tables[i]
        mt_text, mt_start, mt_end = md_tables_meta[i]

        # D6: nested table collapse
        if _has_nested_table(ht):
            issues.append(TableIssue(
                table_index=i,
                issue_type="nested_table",
                severity="P2",
                cause=(
                    f"Table {i+1} contains a nested <table> (outer + inner). "
                    "Markdown tables cannot express nesting; the inner table "
                    "has been flattened into a garbled single row by markitdown."
                ),
                fixable=False,
                md_table_index=i + 1,
                md_start_line=mt_start,
                md_end_line=mt_end,
                html_table_index=i + 1,
                html_full_table=ht,
                md_full_table=mt_text,
            ))
            continue  # nested tables: structure already destroyed, skip other checks

        # D2: vertical merge column misalignment
        if _has_rowspan(ht):
            html_rows = _count_html_rows(ht)
            html_cols = _count_html_cols(ht)
            md_cols_per_row = _count_md_cols_per_row(mt_text)
            # Data rows = all rows except header(0) and separator(1)
            data_row_indices = [idx for idx in range(len(md_cols_per_row))
                                if idx not in (0, 1)]
            misaligned_rows = [idx for idx in data_row_indices
                               if md_cols_per_row[idx] < html_cols]

            if misaligned_rows and html_cols > 0:
                issues.append(TableIssue(
                    table_index=i,
                    issue_type="vertical_merge",
                    severity="P1",
                    cause=(
                        f"Table {i+1} uses rowspan (vertical cell merge) in HTML. "
                        f"markitdown dropped the rowspan placeholder cells, so the "
                        f"affected data rows have only "
                        f"{min(md_cols_per_row[idx] for idx in misaligned_rows)} "
                        f"column(s) instead of the expected {html_cols}, causing "
                        f"data values to shift LEFT into the wrong columns. "
                        f"Restore the missing cells so each row has {html_cols} columns."
                    ),
                    fixable=True,
                    md_table_index=i + 1,
                    md_start_line=mt_start,
                    md_end_line=mt_end,
                    md_affected_rows=[r + 1 for r in misaligned_rows],
                    expected_md_cols=html_cols,
                    actual_md_cols_per_row=md_cols_per_row,
                    html_table_index=i + 1,
                    html_full_table=ht,
                    md_full_table=mt_text,
                ))

    return issues


# ---------------------------------------------------------------------------
# Structured error report (for AI consumption)
# ---------------------------------------------------------------------------

def format_error_report(issues: list[TableIssue], md_path: str = "") -> str:
    """Format detected issues as a STRUCTURED error report for the AI to act on.

    Each error block contains exactly three sections:
      CAUSE          — why the md is wrong
      MD_LOCATION    — exact line range + affected rows in the .md file
      HTML_REFERENCE — ground-truth <table> block to reproduce

    Returns an empty string if there are no issues (caller should treat empty
    string as success).
    """
    if not issues:
        return ""

    path_hint = f" `{md_path}`" if md_path else ""
    lines = [
        f"# Table Structure Errors in{path_hint}",
        "",
        f"The following {len(issues)} table(s) were corrupted during conversion.",
        "For each error: read CAUSE to understand, MD_LOCATION to find the lines",
        "to edit, and HTML_REFERENCE to reproduce the correct structure.",
        "",
    ]
    for issue in issues:
        lines.append(f"## Error {issue.table_index + 1}: "
                     f"[{issue.severity}] {issue.issue_type} "
                     f"(md table #{issue.md_table_index})")
        lines.append("")

        # CAUSE
        lines.append("**CAUSE:**")
        lines.append(issue.cause)
        lines.append("")

        # MD_LOCATION
        lines.append("**MD_LOCATION:**")
        lines.append(f"- md file: `{md_path}`" if md_path else "- md file: (in-memory)")
        lines.append(f"- table starts at line {issue.md_start_line}, "
                     f"ends at line {issue.md_end_line}")
        lines.append(f"- expected columns per row: {issue.expected_md_cols}")
        if issue.actual_md_cols_per_row:
            per_row = ", ".join(
                f"row{i+1}={c}" for i, c in enumerate(issue.actual_md_cols_per_row)
            )
            lines.append(f"- actual columns per row: {per_row}")
        if issue.md_affected_rows:
            rows = ", ".join(str(r) for r in issue.md_affected_rows)
            lines.append(f"- affected data rows (need fixing): {rows}")
        lines.append("")

        # HTML_REFERENCE
        lines.append(f"**HTML_REFERENCE** (table #{issue.html_table_index} in "
                     f"mammoth output — ground truth):")
        lines.append("```html")
        lines.append(issue.html_full_table)
        lines.append("```")
        lines.append("")

        # Current md (for side-by-side)
        lines.append("**CURRENT_MD** (what's wrong now):")
        lines.append("```markdown")
        lines.append(issue.md_full_table)
        lines.append("```")
        lines.append("")

        lines.append(f"Fixable by AI: {'YES' if issue.fixable else 'NO (LLM-describe: write a natural-language description in the md BODY, see SKILL AUTO-FIX POLICY)'}")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# Backward-compatible alias (older code may import this name).
def format_issues_for_ai(issues: list[TableIssue], md_path: str = "") -> str:
    """Deprecated alias for format_error_report()."""
    return format_error_report(issues, md_path)
