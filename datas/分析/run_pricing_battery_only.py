#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Battery-only retrofit pricing & ROI calculator (Residential)
- Uses M1 filtered dataset to estimate typical PV size by state
- Parses parameters from datas/分析/参数清单.md
- Builds state-level packages for 9.6/13.5/20 kWh batteries (AC耦合假设)
- Computes price_base, battery rebate, price_net, annual savings uplift (SC 0.3->0.7), payback

Run from project root:
  python3 datas/分析/run_pricing_battery_only.py

Outputs under datas/分析/output/:
  - battery_only_packages_by_state.csv
  - battery_only_pricing_summary.md
"""
from __future__ import annotations
import re
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATAS_DIR = PROJECT_ROOT / "datas"
ANALYSIS_DIR = DATAS_DIR / "分析"
OUTPUT_DIR = ANALYSIS_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

M1_FILE = OUTPUT_DIR / "residential_m1_filtered.csv"
PARAM_MD = ANALYSIS_DIR / "参数清单.md"

# ---------- utils to parse markdown tables ----------

def _read_param_lines() -> list[str]:
    return PARAM_MD.read_text(encoding="utf-8").splitlines()


def _parse_table(lines: list[str], start_marker: str) -> list[list[str]]:
    start_idx = None
    for i, ln in enumerate(lines):
        if start_marker in ln:
            start_idx = i
            break
    if start_idx is None:
        return []
    i = start_idx
    while i < len(lines) and not lines[i].lstrip().startswith('|'):
        i += 1
    table = []
    while i < len(lines):
        ln = lines[i].strip()
        if not ln.startswith('|'):
            break
        table.append([cell.strip() for cell in ln.strip('|').split('|')])
        i += 1
    if len(table) >= 2:
        body = []
        for row in table[2:]:
            if all(c == '' for c in row):
                continue
            body.append(row)
        return body
    return []


def _to_float(x: str) -> float | None:
    try:
        return float(x)
    except Exception:
        import re
        m = re.search(r"([0-9]+\.?[0-9]*)", str(x))
        return float(m.group(1)) if m else None


def parse_battery_rebates(lines: list[str]) -> dict[str, dict]:
    rows = _parse_table(lines, "## 2. 电池补贴映射")
    policies = {}
    for r in rows:
        if len(r) < 9:
            continue
        state = r[0].strip()
        start_month = r[1].strip()
        end_month = r[2].strip() if r[2].strip() else None
        min_kwh = _to_float(r[3]) or 0.0
        pricing_type = r[4].strip()
        amount_or_rate = r[5].strip()
        cap_amount = _to_float(r[6]) if r[6].strip() else None
        rate = None
        fixed = None
        if pricing_type == "固定":
            fixed = _to_float(amount_or_rate) or 0.0
        elif pricing_type == "按kWh":
            rate = _to_float(amount_or_rate) or 0.0
        else:
            fixed = _to_float(amount_or_rate) or 0.0
        policies[state] = {
            "start": start_month,
            "end": end_month,
            "min_kwh": float(min_kwh),
            "pricing_type": pricing_type,
            "rate": float(rate) if rate is not None else None,
            "fixed": float(fixed) if fixed is not None else None,
            "cap": float(cap_amount) if cap_amount is not None else None,
        }
    return policies


def parse_rates(lines: list[str]) -> dict[str, dict]:
    rows = _parse_table(lines, "## 3. 电价与上网电价")
    rates = {}
    for r in rows:
        if len(r) < 6:
            continue
        state = r[0].strip()
        quarter = r[1].strip()
        buy = _to_float(r[2])
        sell = _to_float(r[3])
        if buy is None or sell is None:
            continue
        rates[(state, quarter)] = {"buy": float(buy), "sell": float(sell)}
    return rates


def parse_yields(lines: list[str]) -> dict[str, float]:
    rows = _parse_table(lines, "## 7. 年发电量假设")
    d = {}
    for r in rows:
        if len(r) < 2:
            continue
        state = r[0].strip()
        val = _to_float(r[1])
        if val is None:
            continue
        d[state] = float(val)
    return d


def parse_batt_only_costs(lines: list[str]) -> dict[str, float]:
    txt = "\n".join(lines)
    defaults = {
        "battery_unit_cost_per_kwh_new": 900.0,
        "battery_only_install_base_cost": 1200.0,
        "battery_only_install_per_kwh": 80.0,
        "profit_margin_rate_battery_only": 0.15,
    }
    for k in list(defaults.keys()):
        m = re.search(rf"{k}\s*=\s*([0-9]+\.?[0-9]*)", txt)
        if m:
            defaults[k] = float(m.group(1))
    return defaults

# ---------- core calcs ----------

def battery_only_price_and_rebate(state: str, month: str, batt_kwh: float, costs: dict, policies: dict) -> tuple[float, float, float]:
    cost_batt = batt_kwh * costs["battery_unit_cost_per_kwh_new"]
    install = costs["battery_only_install_base_cost"] + batt_kwh * costs["battery_only_install_per_kwh"]
    price_base = (cost_batt + install) * (1.0 + costs["profit_margin_rate_battery_only"]) 
    # rebate
    p = policies.get(state)
    rebate = 0.0
    if p and batt_kwh >= (p.get("min_kwh") or 0):
        if p.get("pricing_type") == "按kWh" and p.get("rate") is not None:
            rebate = batt_kwh * float(p["rate"])
            cap = p.get("cap")
            if cap is not None:
                rebate = min(rebate, float(cap))
        else:
            rebate = float(p.get("fixed") or 0.0)
    price_net = price_base - rebate
    return price_base, rebate, price_net


def annual_savings_uplift(pv_dc_kw: float, ypk: float, rates: dict, state: str, sc0=0.3, sc1=0.7) -> float:
    gen = pv_dc_kw * ypk
    quarter = "2025-Q3"
    rs = rates.get((state, quarter)) or {"buy": 0.30, "sell": 0.07}
    self0 = gen * sc0
    exp0 = max(0.0, gen - self0)
    self1 = gen * sc1
    exp1 = max(0.0, gen - self1)
    bill0 = self0 * rs["buy"] + exp0 * rs["sell"]
    bill1 = self1 * rs["buy"] + exp1 * rs["sell"]
    return bill1 - bill0

# ---------- main ----------

def main() -> None:
    print("[BatteryOnly] Loading M1 filtered dataset...")
    df = pd.read_csv(M1_FILE, dtype=str, low_memory=False)
    df.columns = [c.strip().lower() for c in df.columns]
    for c in ["pv_dc_kw"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    print("[BatteryOnly] Parsing parameters...")
    lines = _read_param_lines()
    rebates = parse_battery_rebates(lines)
    rates = parse_rates(lines)
    yields = parse_yields(lines)
    costs = parse_batt_only_costs(lines)

    print("[BatteryOnly] Computing typical PV DC by state (median of Residential)...")
    pv_median_by_state = df.groupby("state")["pv_dc_kw"].median().dropna().to_dict()

    packages = [
        ("A' 入门", 9.6),
        ("B' 均衡", 13.5),
        ("C' 高配", 20.0),
    ]

    rows = []
    for st, pv_dc_med in pv_median_by_state.items():
        ypk = yields.get(st, 1400.0)
        for name, batt_kwh in packages:
            price_base, rebate, price_net = battery_only_price_and_rebate(st, "2025-08", batt_kwh, costs, rebates)
            uplift = annual_savings_uplift(pv_dc_med, ypk, rates, st)
            payback = price_net / uplift if uplift > 0 else np.nan
            rows.append({
                "state": st,
                "pv_dc_median_kw": pv_dc_med,
                "package": name,
                "battery_kwh": batt_kwh,
                "price_base": price_base,
                "battery_rebate": rebate,
                "price_net": price_net,
                "annual_savings_uplift": uplift,
                "payback_years_net": payback,
            })

    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUTPUT_DIR / "battery_only_packages_by_state.csv", index=False)

    # summary
    lines_out = []
    lines_out.append("# Battery-only（加装储能）定价与ROI（经验参数版）\n")
    lines_out.append("- 覆盖州：" + ", ".join(sorted(pv_median_by_state.keys())))
    lines_out.append("- 套餐：A' 9.6kWh、B' 13.5kWh、C' 20kWh；SC从0.3→0.7 的年度节省增量计入\n")
    lines_out.append("## 样例（Top-5州按回本期排序的条目）\n")
    demo = out_df.sort_values("payback_years_net").groupby("state").head(1).head(5)
    for _, r in demo.iterrows():
        lines_out.append(
            f"- {r['state']}: {r['package']} 净价≈{r['price_net']:.0f} AUD, 年节省增量≈{r['annual_savings_uplift']:.0f} AUD, 回本≈{r['payback_years_net']:.1f} 年"
        )
    (OUTPUT_DIR / "battery_only_pricing_summary.md").write_text("\n".join(lines_out) + "\n", encoding="utf-8")

    print("[BatteryOnly] Done. Outputs saved:")
    for p in [
        OUTPUT_DIR / "battery_only_packages_by_state.csv",
        OUTPUT_DIR / "battery_only_pricing_summary.md",
    ]:
        print(" -", p.relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    main()
