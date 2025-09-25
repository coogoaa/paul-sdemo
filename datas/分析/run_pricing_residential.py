#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Residential pricing & ROI calculator
- Loads M1 filtered dataset (residential_m1_filtered.csv)
- Parses parameters from datas/分析/参数清单.md (experience defaults)
- Computes price_base, STC/battery rebates, price_net, annual savings, payback (net)
- Generates standardized package recommendations by state (A/B/C)

Run from project root:
  python3 datas/分析/run_pricing_residential.py

Outputs under datas/分析/output/:
  - residential_pricing_detailed.csv
  - residential_packages_by_state.csv
  - residential_pricing_summary.md
"""
from __future__ import annotations
import re
from pathlib import Path
import math
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATAS_DIR = PROJECT_ROOT / "datas"
ANALYSIS_DIR = DATAS_DIR / "分析"
OUTPUT_DIR = ANALYSIS_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

M1_FILE = OUTPUT_DIR / "residential_m1_filtered.csv"
PARAM_MD = ANALYSIS_DIR / "参数清单.md"

# -----------------------------
# Markdown param parsers (lightweight)
# -----------------------------

def _read_param_lines() -> list[str]:
    text = PARAM_MD.read_text(encoding="utf-8")
    return text.splitlines()


def _parse_table(lines: list[str], start_marker: str) -> list[list[str]]:
    """Parse a markdown table located after a title marker line contains start_marker.
    Returns rows (list of list of cell strings).
    """
    # Find section
    start_idx = None
    for i, ln in enumerate(lines):
        if start_marker in ln:
            start_idx = i
            break
    if start_idx is None:
        return []
    # Find first table header line after start_idx with leading '|'
    i = start_idx
    while i < len(lines) and not lines[i].lstrip().startswith('|'):
        i += 1
    # Collect table lines until a blank line or not starting with '|'
    table = []
    while i < len(lines):
        ln = lines[i].strip()
        if not ln.startswith('|'):
            break
        # skip separator row like |---|---|
        table.append([cell.strip() for cell in ln.strip('|').split('|')])
        i += 1
    # Remove header and separator rows
    if len(table) >= 2:
        # drop header and possible separator
        body = []
        for row in table[2:]:
            # ignore ellipsis rows or empty
            if all(c == '' for c in row):
                continue
            body.append(row)
        return body
    return []


def parse_stc_prices(lines: list[str]) -> dict[str, float]:
    rows = _parse_table(lines, "## 1. STC 价格区间")
    d = {}
    for r in rows:
        if len(r) < 2:
            continue
        month = r[0].strip()
        price_str = r[1].strip()
        try:
            price = float(price_str)
        except Exception:
            continue
        d[month] = price
    return d


def _to_float(x: str) -> float | None:
    try:
        return float(x)
    except Exception:
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
        amount_or_rate = r[5].strip()  # e.g., '250/kWh' or '1200'
        cap_amount = _to_float(r[6]) if r[6].strip() else None
        # other fields ignored for now
        rate = None
        fixed = None
        if pricing_type == "固定":
            fixed = _to_float(amount_or_rate) or 0.0
        elif pricing_type == "按kWh":
            rate = _to_float(amount_or_rate) or 0.0
        else:
            # Treat others as fixed for now if numeric given
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


def parse_costs(lines: list[str]) -> dict[str, float]:
    txt = "\n".join(lines)
    # code block values
    defaults = {
        "panel_per_kw_cost_dc": 700.0,
        "inverter_unit_cost_per_kw": 180.0,
        "battery_unit_cost_per_kwh_new": 900.0,
        "install_base_cost": 1500.0,
        "install_cost_per_kw": 350.0,
        "profit_margin_rate": 0.15,
    }
    for k in list(defaults.keys()):
        m = re.search(rf"{k}\s*=\s*([0-9]+\.?[0-9]*)", txt)
        if m:
            defaults[k] = float(m.group(1))
    return defaults

# -----------------------------
# Core calculators
# -----------------------------

ROOF_COEF = {"Tile": 1.05, "Colorbond": 1.00}


def stc_value_for_row(row: pd.Series, stc_prices: dict[str, float], fallback_price: float = 35.0, fallback_per_kw: float = 12.0) -> tuple[float, float, float]:
    month = str(row.get("install_month", "")).strip()
    stc_price = stc_prices.get(month, fallback_price)
    stc_count = row.get("stc_count")
    try:
        stc_count = float(stc_count)
    except Exception:
        stc_count = np.nan
    if not np.isfinite(stc_count):
        pv_dc = row.get("pv_dc_kw")
        try:
            pv_dc = float(pv_dc)
        except Exception:
            pv_dc = 0.0
        stc_count = pv_dc * fallback_per_kw
    return stc_count, stc_price, stc_count * stc_price


def battery_rebate_for_row(row: pd.Series, policies: dict[str, dict]) -> float:
    state = str(row.get("state", "")).strip()
    month = str(row.get("install_month", "")).strip()
    batt = row.get("battery_kwh")
    try:
        batt = float(batt)
    except Exception:
        batt = 0.0
    if state not in policies or batt <= 0:
        return 0.0
    p = policies[state]
    # check effective period
    if p["start"] and month and month < p["start"]:
        return 0.0
    if p["end"] and month and month > p["end"]:
        return 0.0
    if batt < (p.get("min_kwh") or 0.0):
        return 0.0
    # compute amount
    if p.get("pricing_type") == "按kWh" and p.get("rate") is not None:
        amt = batt * float(p["rate"])
        cap = p.get("cap")
        if cap is not None:
            amt = min(amt, cap)
        return float(amt)
    fixed = p.get("fixed")
    return float(fixed or 0.0)


def cost_and_price(row: pd.Series, costs: dict[str, float]) -> tuple[float, float]:
    pv_dc = float(row.get("pv_dc_kw") or 0.0)
    pv_ac = float(row.get("pv_ac_kw") or 0.0)
    battery = float(row.get("battery_kwh") or 0.0)
    roof = str(row.get("roof") or "").strip().title()
    roof_coef = ROOF_COEF.get(roof, 1.03)

    cost_panels = pv_dc * costs["panel_per_kw_cost_dc"] * roof_coef
    cost_inverter = pv_ac * costs["inverter_unit_cost_per_kw"]
    cost_battery = battery * costs["battery_unit_cost_per_kwh_new"]
    cost_install = costs["install_base_cost"] + pv_dc * costs["install_cost_per_kw"]
    cost_install *= roof_coef

    total_cost = cost_panels + cost_inverter + cost_battery + cost_install
    price_base = total_cost * (1.0 + costs["profit_margin_rate"])
    return total_cost, price_base


def annual_generation(row: pd.Series, yields: dict[str, float]) -> float:
    state = str(row.get("state", "")).strip()
    pv_dc = float(row.get("pv_dc_kw") or 0.0)
    ypk = yields.get(state)
    if not ypk:
        ypk = 1400.0
    return pv_dc * ypk


def annual_savings(row: pd.Series, buy_sell: dict[tuple[str, str], dict]) -> float:
    state = str(row.get("state", "")).strip()
    quarter = "2025-Q3"  # default for now
    rates = buy_sell.get((state, quarter)) or {"buy": 0.30, "sell": 0.07}
    gen = float(row.get("annual_generation_kwh") or 0.0)
    has_batt = float(row.get("battery_kwh") or 0.0) > 0
    # simple SC assumption
    sc = 0.7 if has_batt else 0.3
    self_kwh = gen * sc
    export_kwh = max(0.0, gen - self_kwh)
    return self_kwh * rates["buy"] + export_kwh * rates["sell"]


# -----------------------------
# Sizing helpers (铺满屋顶 & 大电池合理推荐)
# -----------------------------

def compute_state_roof_dc(df: pd.DataFrame, percentile: float = 0.9, cap_kw: float = 15.0) -> dict[str, float]:
    """Use M1 filtered rows to estimate '满屋顶' DC by state as P90 of big_roof_flag==1 pv_dc_kw.
    Cap to a safe residential upper bound (default 15kW) for three相可行的范围。
    """
    d = {}
    if "pv_dc_kw" not in df.columns or "state" not in df.columns:
        return d
    df_num = df.copy()
    df_num["pv_dc_kw"] = pd.to_numeric(df_num["pv_dc_kw"], errors="coerce")
    if "big_roof_flag" in df_num.columns:
        df_num = df_num[df_num["big_roof_flag"].fillna(0) == 1]
    for st, g in df_num.groupby("state"):
        if g["pv_dc_kw"].dropna().empty:
            continue
        p90 = float(np.nanpercentile(g["pv_dc_kw"].values, percentile * 100))
        d[str(st)] = float(min(max(p90, 13.2), cap_kw))  # 至少不低于 13.2kW，最多 15kW
    return d


def select_inverter_ac(pv_dc: float, target_ratio: float = 1.25) -> float:
    """Choose a realistic inverter AC size given a target DC/AC ratio.
    Allowed set: {5, 6, 8, 10, 12, 15} kW (示例)。
    """
    allowed = np.array([5.0, 6.0, 8.0, 10.0, 12.0, 15.0])
    ac = pv_dc / target_ratio if target_ratio > 0 else pv_dc
    return float(allowed[np.argmin(np.abs(allowed - ac))])


def snap_to_tier(x: float, tiers = (10.0, 13.5, 20.0, 22.4, 25.6, 30.0)) -> float:
    for t in tiers:
        if x <= t:
            return float(t)
    return float(tiers[-1])


def recommend_battery_for_dc(pv_dc: float, state: str, yields: dict[str, float], baseline_sc=0.3, target_sc=0.7, DoD=0.9, RTE=0.9,
                             max_tier: float = 25.6) -> float:
    ypk = yields.get(state, 1400.0)
    annual_gen = pv_dc * ypk
    daily_shift = (annual_gen / 365.0) * max(0.0, target_sc - baseline_sc)
    nominal = daily_shift / max(1e-6, DoD * RTE)
    reco = snap_to_tier(nominal)
    return float(min(reco, max_tier))


# -----------------------------
# Main
# -----------------------------

def main() -> None:
    print("[Pricing] Loading M1 filtered residential dataset...")
    df = pd.read_csv(M1_FILE, dtype=str, low_memory=False)
    df.columns = [c.strip().lower() for c in df.columns]

    # cast numeric
    for c in ["pv_dc_kw", "pv_ac_kw", "dc_ac_ratio", "battery_kwh", "stc_count"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    print("[Pricing] Parsing parameters from 参数清单.md ...")
    lines = _read_param_lines()
    stc_prices = parse_stc_prices(lines)
    rebates = parse_battery_rebates(lines)
    rates = parse_rates(lines)
    yields = parse_yields(lines)
    costs = parse_costs(lines)

    print("[Pricing] Computing pricing, rebates and ROI for residential rows...")
    rows = []
    for _, r in df.iterrows():
        stc_cnt, stc_price, stc_val = stc_value_for_row(r, stc_prices)
        total_cost, price_base = cost_and_price(r, costs)
        batt_rebate = battery_rebate_for_row(r, rebates)
        price_net = price_base - stc_val - batt_rebate
        gen = annual_generation(r, yields)
        sav = annual_savings({**r.to_dict(), "annual_generation_kwh": gen}, rates)
        payback = float(price_net) / sav if sav and sav > 0 else np.nan
        rows.append({
            "pvd_id": r.get("pvd_id"),
            "state": r.get("state"),
            "install_month": r.get("install_month"),
            "pv_dc_kw": r.get("pv_dc_kw"),
            "pv_ac_kw": r.get("pv_ac_kw"),
            "battery_kwh": r.get("battery_kwh"),
            "stc_count": stc_cnt,
            "stc_price": stc_price,
            "stc_value": stc_val,
            "battery_rebate": batt_rebate,
            "price_base": price_base,
            "price_net": price_net,
            "annual_generation_kwh": gen,
            "annual_savings_aud": sav,
            "payback_years_net": payback,
        })
    detailed = pd.DataFrame(rows)
    detailed.to_csv(OUTPUT_DIR / "residential_pricing_detailed.csv", index=False)

    print("[Pricing] Building standardized package recommendations by state...")
    # Estimate STC per kW by state from data if possible
    df_valid = df[(df["pv_dc_kw"] > 0) & (df["stc_count"].notna())]
    perkw_state = df_valid.assign(perkw=df_valid["stc_count"] / df_valid["pv_dc_kw"]).groupby("state")["perkw"].median().to_dict()
    # Estimate 满屋顶 DC by state
    roof_dc_state = compute_state_roof_dc(df)

    package_rows = []
    states = sorted(df["state"].dropna().unique())
    for st in states:
        st_perkw = perkw_state.get(st, 12.0)
        for pkg in [
            ("A 入门", 10.0, 8.0, 9.6),
            ("B 均衡", 13.2, 10.0, 13.5),
            ("C 高配", 15.0, 12.0, 20.0),
        ]:
            name, pv_dc, inv_ac, batt = pkg
            # synthetic row
            r0 = {
                "state": st,
                "install_month": "2025-08",  # assume event after
                "pv_dc_kw": pv_dc,
                "pv_ac_kw": inv_ac,
                "battery_kwh": batt,
                "roof": "Colorbond",
            }
            stc_price = stc_prices.get("2025-08", 35.0)
            stc_cnt = pv_dc * st_perkw
            stc_val = stc_cnt * stc_price
            total_cost, price_base = cost_and_price(r0, costs)
            batt_rebate = battery_rebate_for_row(r0, rebates)
            price_net = price_base - stc_val - batt_rebate
            gen = pv_dc * (yields.get(st, 1400.0))
            sav = annual_savings({**r0, "annual_generation_kwh": gen}, rates)
            payback = float(price_net) / sav if sav and sav > 0 else np.nan
            package_rows.append({
                "state": st,
                "package": name,
                "pv_dc_kw": pv_dc,
                "inverter_ac_kw": inv_ac,
                "battery_kwh": batt,
                "stc_per_kw": st_perkw,
                "stc_price": stc_price,
                "stc_value": stc_val,
                "battery_rebate": batt_rebate,
                "price_base": price_base,
                "price_net": price_net,
                "annual_generation_kwh": gen,
                "annual_savings_aud": sav,
                "payback_years_net": payback,
            })
        # D: 铺满屋顶 + 合理更大电池
        pv_dc_d = roof_dc_state.get(st, 15.0)
        inv_ac_d = select_inverter_ac(pv_dc_d, 1.25)
        batt_d = recommend_battery_for_dc(pv_dc_d, st, yields, max_tier=25.6)
        r0 = {
            "state": st,
            "install_month": "2025-08",
            "pv_dc_kw": pv_dc_d,
            "pv_ac_kw": inv_ac_d,
            "battery_kwh": batt_d,
            "roof": "Colorbond",
        }
        stc_price = stc_prices.get("2025-08", 35.0)
        stc_cnt = pv_dc_d * st_perkw
        stc_val = stc_cnt * stc_price
        total_cost, price_base = cost_and_price(r0, costs)
        batt_rebate = battery_rebate_for_row(r0, rebates)
        price_net = price_base - stc_val - batt_rebate
        gen = pv_dc_d * (yields.get(st, 1400.0))
        sav = annual_savings({**r0, "annual_generation_kwh": gen}, rates)
        payback = float(price_net) / sav if sav and sav > 0 else np.nan
        package_rows.append({
            "state": st,
            "package": "D 铺满屋顶",
            "pv_dc_kw": pv_dc_d,
            "inverter_ac_kw": inv_ac_d,
            "battery_kwh": batt_d,
            "stc_per_kw": st_perkw,
            "stc_price": stc_price,
            "stc_value": stc_val,
            "battery_rebate": batt_rebate,
            "price_base": price_base,
            "price_net": price_net,
            "annual_generation_kwh": gen,
            "annual_savings_aud": sav,
            "payback_years_net": payback,
        })
    pkg_df = pd.DataFrame(package_rows)
    pkg_df.to_csv(OUTPUT_DIR / "residential_packages_by_state.csv", index=False)

    # summary md
    lines = []
    lines.append("# Residential 定价与ROI（经验参数版）\n")
    lines.append("## 数据概览\n")
    lines.append(f"- 明细行数：{len(detailed):,}")
    lines.append(f"- 覆盖州：{', '.join(states)}")
    lines.append("")
    lines.append("## 推荐套餐（示例 Top-5州按净价回本期排序）\n")
    top_states = (
        pkg_df.groupby("state")["payback_years_net"].median().sort_values().head(5).index.tolist()
    )
    for st in top_states:
        sub = pkg_df[pkg_df["state"] == st].sort_values("payback_years_net")
        lines.append(f"- {st}：")
        for _, r in sub.iterrows():
            lines.append(
                f"  - {r['package']}: 净价≈{r['price_net']:.0f} AUD, 年节省≈{r['annual_savings_aud']:.0f} AUD, 回本≈{r['payback_years_net']:.1f} 年"
            )
    (OUTPUT_DIR / "residential_pricing_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("[Pricing] Done. Outputs saved:")
    for p in [
        OUTPUT_DIR / "residential_pricing_detailed.csv",
        OUTPUT_DIR / "residential_packages_by_state.csv",
        OUTPUT_DIR / "residential_pricing_summary.md",
    ]:
        print(" -", p.relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    main()
