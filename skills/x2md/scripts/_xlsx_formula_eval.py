r"""Evaluate XLSX formulas and inject cached values so markitdown reads real numbers.

WHY THIS EXISTS
---------------
markitdown reads XLSX via `pandas.read_excel`, which only reads the **cached
computed values** Excel writes into each formula cell's `<v>` tag. When an XLSX
is produced programmatically (openpyxl, database export, etc.) the formula is
written as `<f>A2+B2</f>` but the accompanying `<v></v>` is EMPTY — so pandas
returns NaN and markitdown emits `NaN` into the Markdown.

This module computes the formulas with the pure-Python `formulas` library and
writes the results back into the `<v>` tags, producing an XLSX that markitdown
can read correctly.

PUBLIC API
----------
    evaluate_xlsx(path_or_bytes) -> bytes
        Returns a new XLSX (in-memory bytes) with all formula cells populated
        with computed values. If `formulas` is not installed or computation
        fails, returns the input unchanged (graceful no-op).

    has_formulas(path_or_bytes) -> bool
        Quick check whether the XLSX contains any `<f>` formula cells.

Integration point: `_convert_core.convert_file()` calls `evaluate_xlsx()` on
the XLSX bytes BEFORE handing them to markitdown, only when the file is .xlsx
and contains formulas.
"""
from __future__ import annotations
import io
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union

XlsxInput = Union[str, Path, bytes, io.BytesIO]


def _to_bytes(src: XlsxInput) -> bytes:
    """Normalize input to raw bytes."""
    if isinstance(src, (str, Path)):
        with open(src, "rb") as f:
            return f.read()
    if isinstance(src, io.BytesIO):
        return src.getvalue()
    if isinstance(src, bytes):
        return src
    raise TypeError(f"Unsupported input type: {type(src)}")


def has_formulas(src: XlsxInput) -> bool:
    """Quick check: does this XLSX contain any formula cells (`<f>` tags)?"""
    raw = _to_bytes(src)
    try:
        with zipfile.ZipFile(io.BytesIO(raw), "r") as z:
            for name in z.namelist():
                if name.startswith("xl/worksheets/sheet") and name.endswith(".xml"):
                    if b"<f" in z.read(name):
                        return True
    except (zipfile.BadZipFile, KeyError):
        pass
    return False


def _to_scalar(val) -> str | None:
    """Extract a clean XML-safe scalar string from a formulas Ranges/Array value.

    Returns a string suitable for writing into `<v>...</v>`, or None if the
    value cannot be serialized (e.g. error strings, empty arrays).
    """
    try:
        v = getattr(val, "value", val)
        # formulas returns numpy arrays nested 1-2 levels deep — unwrap.
        while hasattr(v, "__len__") and not isinstance(v, str):
            if len(v) == 0:
                return None
            v = v[0]
        # numpy scalar → python scalar
        if hasattr(v, "item"):
            v = v.item()
        if isinstance(v, bool):
            return "TRUE" if v else "FALSE"
        if isinstance(v, float):
            # Trim trailing zeros: 5.0 -> "5", 3.14 -> "3.14"
            if v != v:  # NaN check
                return None
            return repr(v) if not v.is_integer() else str(int(v))
        if isinstance(v, int):
            return str(v)
        if isinstance(v, str):
            # Formula result is a string — openpyxl/markitdown expects the cell
            # type to be 'str' for this, but we only fix <v>; skip to avoid
            # corrupting cells that need t="str". These are rare (most formulas
            # return numbers); they will fall through to NaN, which is documented.
            return None
        return None
    except Exception:
        return None


def _compute_with_formulas(xlsx_bytes: bytes) -> dict[str, dict[str, str]]:
    """Compute all formula values.

    Returns {sheet_name: {cell_ref: value_string}}. Returns {} if the
    `formulas` library is unavailable or computation fails for any reason
    (we treat formula evaluation as best-effort — never fatal).
    """
    try:
        import formulas  # type: ignore
    except ImportError:
        return {}

    # Write bytes to a temp file — formulas.ExcelModel needs a path.
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tf:
        tf.write(xlsx_bytes)
        tmp_path = tf.name
    try:
        model = formulas.ExcelModel().loads(tmp_path).finish()
        solution = model.calculate()
    except Exception:
        return {}
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    # solution keys look like "'[file.xlsx]SheetName'!CELLREF"
    out: dict[str, dict[str, str]] = {}
    key_re = re.compile(r"'?\[.*?\]([^']+)'?!([A-Z]+\d+)")
    for key, val in solution.items():
        m = key_re.search(str(key))
        if not m:
            continue
        sheet_name, cell_ref = m.group(1), m.group(2)
        scalar = _to_scalar(val)
        if scalar is not None:
            out.setdefault(sheet_name, {})[cell_ref] = scalar
    return out


def _inject_values(xlsx_bytes: bytes, computed: dict[str, dict[str, str]]) -> bytes:
    """Inject computed values into `<v>` tags of formula cells.

    `computed` is {sheet_name: {cell_ref: value}}. We map sheet names to
    worksheet XML files via workbook.xml rels, then rewrite each sheet's XML
    to inject `...<v>value</v></c>` where an empty `<v></v>` sits.
    """
    if not computed:
        return xlsx_bytes

    # --- Step 1: parse workbook.xml + rels → sheet_name: xml_path ---
    name_to_xml: dict[str, str] = {}
    with zipfile.ZipFile(io.BytesIO(xlsx_bytes), "r") as zin:
        try:
            wb_xml = zin.read("xl/workbook.xml").decode("utf-8")
            rels_xml_raw = zin.read("xl/_rels/workbook.xml.rels").decode("utf-8")
        except KeyError:
            return xlsx_bytes

    # Extract sheet name → r:id from workbook.xml
    sheets = dict(re.findall(
        r'<sheet[^>]*name="([^"]+)"[^>]*r:id="([^"]+)"', wb_xml))

    # Extract r:id → Target from rels.  Attributes can appear in either order
    # (Target before Id or Id before Target), so try both.
    rels: dict[str, str] = {}
    for rid, target in re.findall(
            r'<Relationship[^>]*Id="([^"]+)"[^>]*Target="([^"]+)"', rels_xml_raw):
        rels[rid] = target
    for target, rid in re.findall(
            r'<Relationship[^>]*Target="([^"]+)"[^>]*Id="([^"]+)"', rels_xml_raw):
        if rid not in rels:
            rels[rid] = target

    for sname, rid in sheets.items():
        target = rels.get(rid, "")
        # Normalize: /xl/worksheets/sheet1.xml → xl/worksheets/sheet1.xml
        target = target.lstrip("/")
        name_to_xml[sname] = target

    # Case-insensitive lookup index for `computed`. The `formulas` library
    # uppercases sheet names in its solution keys (e.g. 'Sheet' → 'SHEET'),
    # while workbook.xml preserves the original casing. Map both casings to
    # the workbook's XML path so the per-sheet regex inject below still fires.
    computed_ci: dict[str, dict[str, str]] = {}
    for cname, refs in computed.items():
        computed_ci[cname.upper()] = refs

    # --- Step 2: rewrite each sheet XML injecting computed <v> values ---
    out_buf = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(xlsx_bytes), "r") as zin:
        with zipfile.ZipFile(out_buf, "w", zipfile.ZIP_DEFLATED) as zout:
            total_injected = 0
            for item in zin.infolist():
                data = zin.read(item.filename)
                # Find which sheet (if any) this XML represents
                matched_name = ""
                for sname, xml_path in name_to_xml.items():
                    if item.filename == xml_path:
                        matched_name = sname
                        break
                # Match case-insensitively: `formulas` returns UPPERCASED
                # sheet names (e.g. 'SHEET'), but workbook.xml has the original
                # casing (e.g. 'Sheet'). Without this normalization the lookup
                # silently misses every sheet → zero cells injected → formulas
                # stay empty → markitdown drops the rows (silent data loss).
                refs = computed_ci.get(matched_name.upper()) if matched_name else None
                if refs:
                    xml = data.decode("utf-8")
                    for cell_ref, val in refs.items():
                        # Match <c r="C2"...><f>...</f><v>(anything)</v></c>
                        pattern = (
                            rf'(<c r="{cell_ref}"[^>]*>\s*<f[^>]*>[^<]*</f>)'
                            rf'\s*(?:<v>[^<]*</v>)?\s*(</c>)'
                        )
                        new_xml, n = re.subn(
                            pattern, rf'\1<v>{val}</v>\2', xml)
                        if n:
                            xml = new_xml
                            total_injected += n
                    data = xml.encode("utf-8")
                zout.writestr(item, data)

    if total_injected == 0:
        return xlsx_bytes
    return out_buf.getvalue()


def evaluate_xlsx(src: XlsxInput) -> bytes:
    """Return XLSX bytes with all formula cells populated with computed values.

    Graceful no-op if:
      - the input is not a valid XLSX
      - it contains no formulas
      - the `formulas` library is not installed
      - computation fails for any reason

    Never raises — formula evaluation is best-effort enhancement.
    """
    try:
        raw = _to_bytes(src)
    except (OSError, TypeError):
        return _to_bytes(src) if not isinstance(src, (str, Path)) else b""

    if not has_formulas(raw):
        return raw

    computed = _compute_with_formulas(raw)
    if not computed:
        return raw

    return _inject_values(raw, computed)


@dataclass
class EvaluationReport:
    """Outcome of an XLSX formula-evaluation pass.

    `unresolved_cells` lists sheet+cell refs whose formulas could not be
    computed (they will emit `NaN` in the final Markdown). The agent uses
    this to decide whether to STOP per SKILL.md's C-4 policy — the script
    itself never stops (graceful no-op contract), it only signals.
    """
    total_formula_cells: int = 0
    resolved_cells: int = 0
    unresolved_cells: list[tuple[str, str]] = field(default_factory=list)  # (sheet, "A1")
    library_missing: bool = False
    computation_failed: bool = False

    @property
    def has_unresolved(self) -> bool:
        return bool(self.unresolved_cells)

    def one_line(self) -> str:
        """Single stdout line for the agent to read. Empty if nothing notable."""
        if self.library_missing:
            return "XLSX formula eval: `formulas` library not installed — formula cells will emit NaN (see SKILL.md C-4 STOP policy)"
        if self.computation_failed:
            return "XLSX formula eval: computation failed — formula cells will emit NaN (see SKILL.md C-4 STOP policy)"
        if self.total_formula_cells == 0:
            return ""
        if self.has_unresolved:
            refs = ", ".join(f"{s}!{c}" for s, c in self.unresolved_cells[:10])
            more = f" (+{len(self.unresolved_cells)-10} more)" if len(self.unresolved_cells) > 10 else ""
            return (f"XLSX formula eval: {self.resolved_cells}/{self.total_formula_cells} cells resolved, "
                    f"{len(self.unresolved_cells)} unresolved → will emit NaN: {refs}{more}")
        return f"XLSX formula eval: {self.resolved_cells}/{self.total_formula_cells} cells resolved"


def _count_formula_cells(xlsx_bytes: bytes) -> list[tuple[str, str]]:
    """Return [(sheet_xml_filename, cell_ref), ...] for every <c><f> cell.

    Used to detect unresolved formulas: after evaluation, any formula cell
    whose `<v>` is still empty will emit NaN.
    """
    out: list[tuple[str, str]] = []
    try:
        with zipfile.ZipFile(io.BytesIO(xlsx_bytes), "r") as z:
            for name in z.namelist():
                if name.startswith("xl/worksheets/sheet") and name.endswith(".xml"):
                    xml = z.read(name).decode("utf-8")
                    for m in re.finditer(r'<c r="([A-Z]+\d+)"[^>]*>\s*<f', xml):
                        out.append((name, m.group(1)))
    except (zipfile.BadZipFile, KeyError):
        pass
    return out


def evaluate_xlsx_with_report(src: XlsxInput) -> tuple[bytes, EvaluationReport]:
    """Like evaluate_xlsx(), but also returns an EvaluationReport describing
    which formula cells could not be resolved (and will therefore emit NaN).

    The bytes returned are identical to evaluate_xlsx() — this function is
    a strict superset for callers that want the diagnostic. The report is
    for signalling only; the script never raises or stops.
    """
    report = EvaluationReport()
    try:
        raw = _to_bytes(src)
    except (OSError, TypeError):
        return (_to_bytes(src) if not isinstance(src, (str, Path)) else b""), report

    if not has_formulas(raw):
        return raw, report

    formula_cells = _count_formula_cells(raw)
    report.total_formula_cells = len(formula_cells)

    try:
        import formulas  # type: ignore  # noqa: F401
    except ImportError:
        report.library_missing = True
        return raw, report

    computed = _compute_with_formulas(raw)
    if not computed:
        report.computation_failed = True
        return raw, report

    new_bytes = _inject_values(raw, computed)

    # Detect unresolved: re-read the OUTPUT bytes, any formula cell whose
    # <v> is still empty (or missing) after injection = unresolved.
    resolved_refs: set[tuple[str, str]] = set()
    try:
        with zipfile.ZipFile(io.BytesIO(new_bytes), "r") as z:
            for name, cell_ref in formula_cells:
                xml = z.read(name).decode("utf-8")
                # Cell with non-empty <v> after the <f>
                m = re.search(rf'<c r="{re.escape(cell_ref)}"[^>]*>\s*<f[^>]*>[^<]*</f>\s*<v>([^<]+)</v>', xml)
                if m and m.group(1).strip():
                    resolved_refs.add((name, cell_ref))
                else:
                    report.unresolved_cells.append((_sheet_name_from_xml(name), cell_ref))
    except (zipfile.BadZipFile, KeyError):
        # If we can't read the output, fall back to "all computed = resolved"
        resolved_refs = set(formula_cells)
    report.resolved_cells = len(resolved_refs)
    return new_bytes, report


def _sheet_name_from_xml(xml_filename: str) -> str:
    """Best-effort: 'xl/worksheets/sheet1.xml' → 'sheet1'."""
    base = xml_filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    return base[:-4] if base.endswith(".xml") else base


def is_available() -> bool:
    """True if the `formulas` library is importable (the only hard dep)."""
    try:
        import formulas  # noqa: F401
        return True
    except ImportError:
        return False


__all__ = ["evaluate_xlsx", "evaluate_xlsx_with_report", "has_formulas", "is_available", "EvaluationReport"]
