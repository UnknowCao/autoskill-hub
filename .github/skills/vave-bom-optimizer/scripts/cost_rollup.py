#!/usr/bin/env python3
"""
Cost Rollup Calculator for VAVE BOM Optimization

Computes multi-level BOM cost including scrap factor, direct labor,
manufacturing overhead, logistics, and indirect costs.

Usage:
    python cost_rollup.py bom.csv --annual-volume 100000 --output rollup.csv

Input BOM CSV columns (header required):
    part_number, description, qty_per_unit, unit_cost, scrap_rate,
    strategic_importance(low/med/high), category

    Optional columns:
        vendor, lead_time_weeks, single_source(yes/no)

Output:
    rollup.csv         - per-line rollup with extended cost
    rollup_summary.txt - total cost + ABC breakdown
"""

import argparse
import csv
import sys
from pathlib import Path


# Industry benchmarks (electronic assembly)
DEFAULT_LABOR_RATE_PER_HOUR = 25.0       # USD, loaded (incl. 30-40% benefits)
DEFAULT_CYCLE_TIME_HOURS = 0.05          # per unit (3 min for medium PCBA)
DEFAULT_OVERHEAD_MULTIPLIER = 3.0        # 2-4x of direct labor
DEFAULT_LOGISTICS_PCT = 0.05             # 5% of material cost
DEFAULT_INDIRECT_PCT = 0.03              # 3% of material cost


def parse_bom(csv_path: Path) -> list[dict]:
    """Parse BOM CSV into list of part dicts."""
    if not csv_path.exists():
        raise FileNotFoundError(f"BOM file not found: {csv_path}")

    parts = []
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"part_number", "qty_per_unit", "unit_cost"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"BOM CSV missing required columns: {missing}")
        for row in reader:
            try:
                qty = float(row["qty_per_unit"])
                cost = float(row["unit_cost"])
                scrap = float(row.get("scrap_rate", "0") or 0)
            except ValueError as e:
                raise ValueError(
                    f"Row {row['part_number']}: invalid numeric value - {e}"
                ) from e
            parts.append({
                "part_number": row["part_number"].strip(),
                "description": row.get("description", "").strip(),
                "qty_per_unit": qty,
                "unit_cost": cost,
                "scrap_rate": scrap,
                "strategic": (row.get("strategic_importance", "med") or "med").strip().lower(),
                "category": row.get("category", "").strip(),
                "vendor": row.get("vendor", "").strip(),
                "lead_time_weeks": row.get("lead_time_weeks", "").strip(),
                "single_source": (row.get("single_source", "no") or "no").strip().lower(),
            })
    return parts


def compute_line_cost(part: dict) -> dict:
    """Compute per-line cost including scrap factor."""
    qty = part["qty_per_unit"]
    scrap = part["scrap_rate"]
    # Scrap: demand / (1 - scrap_rate). If scrap=0, effective_qty = qty.
    effective_qty = qty / (1 - scrap) if scrap < 1 else qty
    base_cost = qty * part["unit_cost"]
    scrap_cost = (effective_qty - qty) * part["unit_cost"]
    extended = base_cost + scrap_cost
    return {
        **part,
        "effective_qty": round(effective_qty, 6),
        "base_cost": round(base_cost, 4),
        "scrap_cost": round(scrap_cost, 4),
        "extended_cost": round(extended, 4),
    }


def abc_classify(parts: list[dict]) -> list[dict]:
    """Classify parts by Pareto (cost cumulative)."""
    sorted_parts = sorted(parts, key=lambda p: p["extended_cost"], reverse=True)
    total = sum(p["extended_cost"] for p in sorted_parts)
    if total == 0:
        return [{**p, "abc": "C", "cum_pct": 0} for p in sorted_parts]

    cumulative = 0
    result = []
    for p in sorted_parts:
        cumulative += p["extended_cost"]
        cum_pct = cumulative / total * 100
        if cum_pct <= 80:
            abc = "A"
        elif cum_pct <= 95:
            abc = "B"
        else:
            abc = "C"
        result.append({**p, "abc": abc, "cum_pct": round(cum_pct, 2)})
    return result


def compute_rollup(
    parts: list[dict],
    annual_volume: int,
    labor_rate: float = DEFAULT_LABOR_RATE_PER_HOUR,
    cycle_time: float = DEFAULT_CYCLE_TIME_HOURS,
    overhead_mult: float = DEFAULT_OVERHEAD_MULTIPLIER,
    logistics_pct: float = DEFAULT_LOGISTICS_PCT,
    indirect_pct: float = DEFAULT_INDIRECT_PCT,
) -> dict:
    """Compute full BOM rollup."""
    lines = [compute_line_cost(p) for p in parts]
    lines = abc_classify(lines)

    material_total = sum(l["extended_cost"] for l in lines)
    direct_labor = cycle_time * labor_rate
    overhead = direct_labor * overhead_mult
    logistics = material_total * logistics_pct
    indirect = material_total * indirect_pct

    total = material_total + direct_labor + overhead + logistics + indirect

    # ABC breakdown
    a_cost = sum(l["extended_cost"] for l in lines if l["abc"] == "A")
    b_cost = sum(l["extended_cost"] for l in lines if l["abc"] == "B")
    c_cost = sum(l["extended_cost"] for l in lines if l["abc"] == "C")
    a_count = sum(1 for l in lines if l["abc"] == "A")
    b_count = sum(1 for l in lines if l["abc"] == "B")
    c_count = sum(1 for l in lines if l["abc"] == "C")

    return {
        "lines": lines,
        "summary": {
            "material_total": round(material_total, 4),
            "direct_labor": round(direct_labor, 4),
            "overhead": round(overhead, 4),
            "logistics": round(logistics, 4),
            "indirect": round(indirect, 4),
            "total_per_unit": round(total, 4),
            "annual_volume": annual_volume,
            "annual_total": round(total * annual_volume, 2),
            "abc_breakdown": {
                "A": {"count": a_count, "cost": round(a_cost, 4),
                      "cost_pct": round(a_cost / material_total * 100, 2) if material_total else 0},
                "B": {"count": b_count, "cost": round(b_cost, 4),
                      "cost_pct": round(b_cost / material_total * 100, 2) if material_total else 0},
                "C": {"count": c_count, "cost": round(c_cost, 4),
                      "cost_pct": round(c_cost / material_total * 100, 2) if material_total else 0},
            },
            "total_parts": len(lines),
        },
    }


def write_rollup_csv(rollup: dict, out_path: Path) -> None:
    """Write per-line rollup to CSV."""
    fields = [
        "part_number", "description", "qty_per_unit", "unit_cost", "scrap_rate",
        "effective_qty", "base_cost", "scrap_cost", "extended_cost",
        "abc", "cum_pct", "strategic", "category", "vendor",
        "lead_time_weeks", "single_source",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for line in rollup["lines"]:
            w.writerow({k: line.get(k, "") for k in fields})


def write_summary(rollup: dict, out_path: Path) -> None:
    """Write human-readable summary."""
    s = rollup["summary"]
    abc = s["abc_breakdown"]
    lines = [
        "=" * 60,
        "BOM Cost Rollup Summary",
        "=" * 60,
        "",
        f"Annual Volume:        {s['annual_volume']:>12,}",
        f"Total Parts:          {s['total_parts']:>12}",
        "",
        "Per-Unit Cost Breakdown:",
        f"  Material (BOM):     ${s['material_total']:>10.4f}",
        f"  Direct Labor:       ${s['direct_labor']:>10.4f}",
        f"  Overhead ({DEFAULT_OVERHEAD_MULTIPLIER}x):   ${s['overhead']:>10.4f}",
        f"  Logistics ({int(DEFAULT_LOGISTICS_PCT*100)}%):    ${s['logistics']:>10.4f}",
        f"  Indirect ({int(DEFAULT_INDIRECT_PCT*100)}%):      ${s['indirect']:>10.4f}",
        f"  ------------------------------",
        f"  TOTAL / UNIT:       ${s['total_per_unit']:>10.4f}",
        "",
        f"Annual Total Cost:    ${s['annual_total']:>12,.2f}",
        "",
        "ABC / Pareto Breakdown:",
        f"  A (top 80% cost):   {abc['A']['count']:>4} parts  "
        f"${abc['A']['cost']:>10.4f}  ({abc['A']['cost_pct']:.2f}%)",
        f"  B (80-95%):         {abc['B']['count']:>4} parts  "
        f"${abc['B']['cost']:>10.4f}  ({abc['B']['cost_pct']:.2f}%)",
        f"  C (>95%):           {abc['C']['count']:>4} parts  "
        f"${abc['C']['cost']:>10.4f}  ({abc['C']['cost_pct']:.2f}%)",
        "",
        "VAVE Priority:",
        f"  -> Start with class A ({abc['A']['count']} parts, "
        f"{abc['A']['cost_pct']:.1f}% of BOM cost)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="VAVE BOM Cost Rollup calculator")
    ap.add_argument("bom_csv", help="Path to BOM CSV file")
    ap.add_argument("--annual-volume", type=int, required=True,
                    help="Annual production volume")
    ap.add_argument("--labor-rate", type=float, default=DEFAULT_LABOR_RATE_PER_HOUR,
                    help=f"Loaded labor rate USD/hr (default {DEFAULT_LABOR_RATE_PER_HOUR})")
    ap.add_argument("--cycle-time", type=float, default=DEFAULT_CYCLE_TIME_HOURS,
                    help=f"Cycle time hours/unit (default {DEFAULT_CYCLE_TIME_HOURS})")
    ap.add_argument("--overhead-mult", type=float, default=DEFAULT_OVERHEAD_MULTIPLIER,
                    help=f"Overhead multiplier (default {DEFAULT_OVERHEAD_MULTIPLIER})")
    ap.add_argument("--output-dir", default=".",
                    help="Output directory (default current)")
    args = ap.parse_args()

    parts = parse_bom(Path(args.bom_csv))
    rollup = compute_rollup(
        parts,
        annual_volume=args.annual_volume,
        labor_rate=args.labor_rate,
        cycle_time=args.cycle_time,
        overhead_mult=args.overhead_mult,
    )

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_out = out_dir / "rollup.csv"
    summary_out = out_dir / "rollup_summary.txt"

    write_rollup_csv(rollup, csv_out)
    write_summary(rollup, summary_out)

    print(f"[OK] Rollup CSV:     {csv_out}")
    print(f"[OK] Summary:        {summary_out}")
    s = rollup["summary"]
    print(f"\nTotal/unit: ${s['total_per_unit']:.4f}  "
          f"Annual: ${s['annual_total']:,.2f}  "
          f"Class A: {s['abc_breakdown']['A']['count']} parts / "
          f"{s['abc_breakdown']['A']['cost_pct']:.1f}% cost")
    return 0


if __name__ == "__main__":
    sys.exit(main())
