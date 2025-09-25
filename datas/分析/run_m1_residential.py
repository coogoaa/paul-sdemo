#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M1 Residential data preparation script
- Cleans, merges and derives fields from GD CSVs
- Filters Residential + Approved + New system + On-Grid
- Outputs merged dataset and summary CSV/Markdown under datas/分析/output/

Run from project root:
  python3 datas/分析/run_m1_residential.py

Dependencies: pandas>=2.0, numpy>=1.25
"""
from __future__ import annotations
import os
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

pd.set_option("display.max_columns", 200)

# ----------------------------
# Config
# ----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATAS_DIR = PROJECT_ROOT / "datas"
GD_DIR = DATAS_DIR / "GD"
OUTPUT_DIR = DATAS_DIR / "分析" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PANELS_CSV = GD_DIR / "greendeal_job_panels_副本.csv"
INVERTERS_CSV = GD_DIR / "greendeal_job_inverters_副本.csv"
STORAGE_CSV = GD_DIR / "greendeal_job_storage_副本.csv"

# Time windows
EVENT_Y, EVENT_M = 2025, 7  # event from 2025-07

# ----------------------------
# Helpers
# ----------------------------

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def _parse_date_series(s: pd.Series) -> pd.Series:
    """Parse dd/mm/yyyy or yyyy-mm-dd; return pandas datetime (naive)."""
    if s is None:
        return pd.NaT
    return pd.to_datetime(s, errors="coerce", dayfirst=True)


def _first_non_null(series: pd.Series) -> object:
    for v in series:
        if pd.notna(v) and v != "":
            return v
    return np.nan


def _mode_or_first(series: pd.Series) -> object:
    if series is None or len(series) == 0:
        return np.nan
    vc = series.dropna().astype(str)
    if vc.empty:
        return np.nan
    mode_vals = vc.mode(dropna=True)
    return mode_vals.iloc[0] if not mode_vals.empty else vc.iloc[0]


def _safe_to_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _join_set(series: pd.Series) -> str:
    vals = sorted({str(x).strip() for x in series if pd.notna(x) and str(x).strip() != ""})
    return "; ".join(vals) if vals else np.nan


def _fmt(x, nd: int = 2) -> str:
    """Format number to fixed decimals; return 'nan' if not a valid number."""
    try:
        if pd.notna(x):
            return f"{float(x):.{nd}f}"
    except Exception:
        pass
    return "nan"


def _assign_period(dt: pd.Series) -> pd.Series:
    y = dt.dt.year
    m = dt.dt.month
    conditions = [
        (y == 2024),
        ((y == 2025) & (m <= 6)),
        ((y == 2025) & (m >= 7)),
        ((y == 2026) & (m <= 3)),
    ]
    choices = ["2024", "2025H1", "2025H2", "2026Q1"]
    return np.select(conditions, choices, default="other").astype(str)


# ----------------------------
# Load CSVs
# ----------------------------

def load_csv(path: Path, usecols: List[str] | None = None) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    df = pd.read_csv(path, encoding="utf-8-sig", dtype=str, low_memory=False)
    df = _normalize_columns(df)
    # Strip whitespace for all string cells
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    if usecols:
        # only keep columns that exist
        cols = [c for c in usecols if c in df.columns]
        df = df[cols]
    return df


# ----------------------------
# Aggregations per table
# ----------------------------

def aggregate_panels(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure numeric conversions
    for num_col in ["rated_output_kw", "number_panels", "watts_per_panel", "rec_qty"]:
        if num_col in df.columns:
            df[num_col] = _safe_to_float(df[num_col])
    # Compute pv_dc_kw_est from panels pieces (sum of number_panels * watts_per_panel / 1000)
    if {"number_panels", "watts_per_panel"}.issubset(df.columns):
        df["_kw_from_pieces"] = (df["number_panels"] * df["watts_per_panel"]) / 1000.0
    else:
        df["_kw_from_pieces"] = np.nan

    group_cols = [c for c in [
        "pvd_id",
        "status",
        "installation_type_name",
        "connected_type_name",
        "connected",
        "property_type",
        "roof",
        "state",
        "post_code",
        "company_name",
        "install_date",
    ] if c in df.columns]

    agg = df.groupby("pvd_id").agg({
        **({"rated_output_kw": "sum"} if "rated_output_kw" in df.columns else {}),
        **({"_kw_from_pieces": "sum"} if "_kw_from_pieces" in df.columns else {}),
        **({"rec_qty": "max"} if "rec_qty" in df.columns else {}),
        **({"panel_brand": _join_set} if "panel_brand" in df.columns else {}),
        **({"panel_item": _join_set} if "panel_item" in df.columns else {}),
        **({"status": _mode_or_first} if "status" in df.columns else {}),
        **({"installation_type_name": _mode_or_first} if "installation_type_name" in df.columns else {}),
        **({"connected_type_name": _mode_or_first} if "connected_type_name" in df.columns else {}),
        **({"connected": _mode_or_first} if "connected" in df.columns else {}),
        **({"property_type": _mode_or_first} if "property_type" in df.columns else {}),
        **({"roof": _mode_or_first} if "roof" in df.columns else {}),
        **({"state": _mode_or_first} if "state" in df.columns else {}),
        **({"post_code": _mode_or_first} if "post_code" in df.columns else {}),
        **({"company_name": _mode_or_first} if "company_name" in df.columns else {}),
        **({"install_date": _first_non_null} if "install_date" in df.columns else {}),
    })

    agg = agg.rename(columns={
        "rated_output_kw": "pv_dc_kw",
        "_kw_from_pieces": "pv_dc_kw_est",
        "rec_qty": "stc_count",
    }).reset_index()

    return agg


def aggregate_inverters(df: pd.DataFrame) -> pd.DataFrame:
    for num_col in ["ac_power", "total_power_kw", "number_inverters"]:
        if num_col in df.columns:
            df[num_col] = _safe_to_float(df[num_col])

    agg = df.groupby("pvd_id").agg({
        **({"ac_power": "sum"} if "ac_power" in df.columns else {}),
        **({"total_power_kw": "sum"} if "total_power_kw" in df.columns else {}),
        **({"number_inverters": "sum"} if "number_inverters" in df.columns else {}),
        **({"inverter_brand": _join_set} if "inverter_brand" in df.columns else {}),
        **({"inverter_model": _join_set} if "inverter_model" in df.columns else {}),
    }).rename(columns={
        "ac_power": "pv_ac_kw",
    }).reset_index()

    # Prefer ac_power sum as pv_ac_kw; if missing, fall back to total_power_kw
    if "pv_ac_kw" in agg.columns and "total_power_kw" in agg.columns:
        agg["pv_ac_kw"] = agg["pv_ac_kw"].fillna(agg["total_power_kw"])
    elif "pv_ac_kw" not in agg.columns and "total_power_kw" in agg.columns:
        agg = agg.rename(columns={"total_power_kw": "pv_ac_kw"})

    return agg


def aggregate_storage(df: pd.DataFrame) -> pd.DataFrame:
    for num_col in ["usable_capacity_kwh", "battery_volume_kwh", "number_batteries"]:
        if num_col in df.columns:
            df[num_col] = _safe_to_float(df[num_col])

    agg = df.groupby("pvd_id").agg({
        **({"usable_capacity_kwh": "sum"} if "usable_capacity_kwh" in df.columns else {}),
        **({"battery_volume_kwh": "sum"} if "battery_volume_kwh" in df.columns else {}),
        **({"number_batteries": "sum"} if "number_batteries" in df.columns else {}),
        **({"battery_brand": _join_set} if "battery_brand" in df.columns else {}),
        **({"battery_item": _join_set} if "battery_item" in df.columns else {}),
    }).rename(columns={
        "usable_capacity_kwh": "battery_kwh",
    }).reset_index()

    return agg


# ----------------------------
# Main processing
# ----------------------------

def main() -> None:
    print("[M1] Loading CSVs...")
    panels_cols = None  # load all, then normalize
    inverters_cols = None
    storage_cols = None

    panels_df = load_csv(PANELS_CSV, panels_cols)
    inverters_df = load_csv(INVERTERS_CSV, inverters_cols)
    storage_df = load_csv(STORAGE_CSV, storage_cols)

    if "pvd_id" not in panels_df.columns:
        raise KeyError("Missing pvd_id in panels CSV")
    if "pvd_id" not in inverters_df.columns:
        raise KeyError("Missing pvd_id in inverters CSV")
    if "pvd_id" not in storage_df.columns:
        # Some storages may be empty – allow empty DF with pvd_id missing
        storage_df = pd.DataFrame({"pvd_id": []})

    print("[M1] Aggregating panels/inverters/storage...")
    p_agg = aggregate_panels(panels_df)
    i_agg = aggregate_inverters(inverters_df)
    s_agg = aggregate_storage(storage_df) if not storage_df.empty else pd.DataFrame({"pvd_id": []})

    print("[M1] Merging to system-level dataset...")
    # Outer merges to keep union of projects (in case of battery-only or inverter-only records)
    merged = p_agg.merge(i_agg, on="pvd_id", how="outer", suffixes=("", "_inv"))
    merged = merged.merge(s_agg, on="pvd_id", how="outer", suffixes=("", "_bat"))

    # Derived fields
    print("[M1] Deriving fields...")
    # Parse install date
    if "install_date" in merged.columns:
        merged["install_date_std"] = _parse_date_series(merged["install_date"])  # may be NaT
    else:
        merged["install_date_std"] = pd.NaT

    merged["install_year"] = merged["install_date_std"].dt.year
    merged["install_month"] = merged["install_date_std"].dt.to_period("M").astype(str)
    merged["install_quarter"] = merged["install_date_std"].dt.to_period("Q")

    # Numeric
    for c in ["pv_dc_kw", "pv_dc_kw_est", "stc_count", "pv_ac_kw", "battery_kwh"]:
        if c in merged.columns:
            merged[c] = _safe_to_float(merged[c])
        else:
            merged[c] = np.nan

    # has_battery
    merged["has_battery"] = (merged["battery_kwh"].fillna(0) > 0).astype(int)

    # dc/ac ratio
    merged["dc_ac_ratio"] = np.where(merged["pv_ac_kw"].fillna(0) > 0,
                                     merged["pv_dc_kw"] / merged["pv_ac_kw"], np.nan)

    # On-grid flag
    if "connected_type_name" in merged.columns:
        merged["on_grid_flag"] = merged["connected_type_name"].str.upper().str.contains("ON-GRID", na=False).astype(int)
    else:
        merged["on_grid_flag"] = np.nan

    # Segment
    if "property_type" in merged.columns:
        merged["segment"] = merged["property_type"].str.title()
    else:
        merged["segment"] = np.nan

    # Big roof (Residential)
    merged["big_roof_flag"] = np.where((merged["segment"] == "Residential") & (merged["pv_dc_kw"] >= 10), 1, 0)

    # Period bucket
    merged["period_bucket"] = _assign_period(merged["install_date_std"]) if "install_date_std" in merged.columns else "other"

    # ----------------------------
    # Sample funnel (counts)
    # ----------------------------
    print("[M1] Building sample funnel (Residential focus)...")
    all_ids = merged["pvd_id"].nunique()

    def count_after(mask: pd.Series) -> int:
        return merged.loc[mask, "pvd_id"].nunique()

    m_status = (merged.get("status").str.title() == "Approved") if "status" in merged.columns else pd.Series(False, index=merged.index)
    m_install = (merged.get("installation_type_name").str.title() == "New System") if "installation_type_name" in merged.columns else pd.Series(False, index=merged.index)
    m_on_grid = (merged.get("on_grid_flag", 0) == 1)
    m_res = (merged.get("segment").str.title() == "Residential") if "segment" in merged.columns else pd.Series(False, index=merged.index)

    funnel = [
        ("union_all", all_ids),
        ("status_approved", count_after(m_status)),
        ("installation_new_system", count_after(m_status & m_install)),
        ("on_grid", count_after(m_status & m_install & m_on_grid)),
        ("residential", count_after(m_status & m_install & m_on_grid & m_res)),
    ]

    # Residential filtered dataset
    res_mask = (m_status & m_install & m_on_grid & m_res)
    res_df = merged.loc[res_mask].copy()

    # Required key fields presence
    key_ok = (
        res_df["install_date_std"].notna() &
        res_df["state"].notna() &
        res_df["post_code"].notna()
    ) if {"install_date_std", "state", "post_code"}.issubset(res_df.columns) else pd.Series(False, index=res_df.index)

    funnel.append(("key_fields_present", res_df.loc[key_ok, "pvd_id"].nunique()))

    # Period splits
    def cnt_period(df: pd.DataFrame, label: str) -> int:
        return df.loc[df["period_bucket"] == label, "pvd_id"].nunique() if "period_bucket" in df.columns else 0

    period_counts = {
        "2024": cnt_period(res_df, "2024"),
        "2025H1": cnt_period(res_df, "2025H1"),
        "2025H2": cnt_period(res_df, "2025H2"),
        "2026Q1": cnt_period(res_df, "2026Q1"),
    }

    # ----------------------------
    # Quick summaries
    # ----------------------------
    print("[M1] Computing quick summaries (by state, roof, big_roof_flag)...")
    def _agg_attach(group: pd.DataFrame) -> pd.Series:
        n = group["pvd_id"].nunique()
        attach = group["has_battery"].mean() if "has_battery" in group.columns else np.nan
        dc_med = group["pv_dc_kw"].median()
        ratio_med = group["dc_ac_ratio"].median()
        return pd.Series({"projects": n, "attach_rate": attach, "pv_dc_kw_median": dc_med, "dc_ac_ratio_median": ratio_med})

    by_state = res_df.groupby("state", dropna=False).apply(_agg_attach).reset_index()
    by_roof = res_df.groupby("roof", dropna=False).apply(_agg_attach).reset_index()
    by_bigroof = res_df.groupby("big_roof_flag", dropna=False).apply(_agg_attach).reset_index()

    # ----------------------------
    # Save outputs
    # ----------------------------
    print("[M1] Saving outputs under datas/分析/output/ ...")
    merged.to_csv(OUTPUT_DIR / "residential_m1_merge_all.csv", index=False)
    res_df.to_csv(OUTPUT_DIR / "residential_m1_filtered.csv", index=False)
    by_state.to_csv(OUTPUT_DIR / "residential_by_state.csv", index=False)
    by_roof.to_csv(OUTPUT_DIR / "residential_by_roof.csv", index=False)
    by_bigroof.to_csv(OUTPUT_DIR / "residential_by_big_roof.csv", index=False)

    funnel_df = pd.DataFrame(funnel, columns=["stage", "unique_pvd_id"])
    funnel_df.to_csv(OUTPUT_DIR / "residential_sample_funnel.csv", index=False)

    # Markdown summary
    summary_lines = []
    summary_lines.append("# Residential M1 数据摘要\n")
    summary_lines.append("## 样本漏斗\n")
    summary_lines.extend([f"- {stage}: {cnt}" for stage, cnt in funnel])
    summary_lines.append("")
    summary_lines.append("## 时间窗口计数（Residential 过滤后）\n")
    for k, v in period_counts.items():
        summary_lines.append(f"- {k}: {v}")
    summary_lines.append("")
    summary_lines.append("## 指标中位数（Residential 过滤后）\n")
    for label, df0 in [("全体", res_df), ("大屋顶=1", res_df[res_df["big_roof_flag"] == 1])]:
        if df0.empty:
            summary_lines.append(f"- {label}: 无样本")
            continue
        attach_rate = df0["has_battery"].mean()
        pv_dc_med = df0["pv_dc_kw"].median()
        ratio_med = df0["dc_ac_ratio"].median()
        summary_lines.append(
            f"- {label}: attach_rate={_fmt(attach_rate, 3)}, pv_dc_kw中位={_fmt(pv_dc_med, 2)}, dc/ac中位={_fmt(ratio_med, 2)}"
        )
    summary_lines.append("")
    summary_lines.append("## 按州汇总（top 5 展示）\n")
    if not by_state.empty:
        top_state = by_state.sort_values("projects", ascending=False).head(5)
        for _, r in top_state.iterrows():
            projects = int(r['projects']) if pd.notna(r['projects']) else 0
            attach = _fmt(r['attach_rate'], 3)
            pv_med = _fmt(r['pv_dc_kw_median'], 2)
            ratio_med = _fmt(r['dc_ac_ratio_median'], 2)
            summary_lines.append(
                f"- {r['state']}: projects={projects}, attach_rate={attach}, pv_dc_kw中位={pv_med}, dc/ac中位={ratio_med}"
            )
    summary_md = "\n".join(summary_lines) + "\n"
    with open(OUTPUT_DIR / "residential_m1_summary.md", "w", encoding="utf-8") as f:
        f.write(summary_md)

    print("[M1] Done. Outputs saved to:")
    for p in [
        OUTPUT_DIR / "residential_m1_merge_all.csv",
        OUTPUT_DIR / "residential_m1_filtered.csv",
        OUTPUT_DIR / "residential_by_state.csv",
        OUTPUT_DIR / "residential_by_roof.csv",
        OUTPUT_DIR / "residential_by_big_roof.csv",
        OUTPUT_DIR / "residential_sample_funnel.csv",
        OUTPUT_DIR / "residential_m1_summary.md",
    ]:
        print(" -", p.relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    main()
