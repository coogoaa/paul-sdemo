#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M2 Residential profiling script
- Consumes M1 output: datas/分析/output/residential_m1_filtered.csv
- Produces monthly time series, battery capacity bands, threshold alignment, brand Top-N/combos,
  and pre/post (2025H1 vs 2025H2) comparisons by state.
- Saves CSVs and a Markdown summary under datas/分析/output/

Run from project root:
  python3 datas/分析/run_m2_residential_profiles.py

Dependencies: pandas>=2.0, numpy>=1.25
"""
from __future__ import annotations
import os
from pathlib import Path
import pandas as pd
import numpy as np

pd.set_option("display.max_columns", 200)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "datas" / "分析" / "output"
M1_FILE = OUTPUT_DIR / "residential_m1_filtered.csv"

OUTPUTS = {
    "ts_monthly": OUTPUT_DIR / "residential_ts_monthly.csv",
    "battery_bands_monthly": OUTPUT_DIR / "residential_battery_bands_monthly.csv",
    "threshold_alignment_monthly": OUTPUT_DIR / "residential_threshold_alignment_monthly.csv",
    "brand_topn": OUTPUT_DIR / "residential_brand_topn.csv",
    "brand_combos": OUTPUT_DIR / "residential_brand_primary_combo.csv",
    "prepost_by_state": OUTPUT_DIR / "residential_prepost_by_state.csv",
    "summary_md": OUTPUT_DIR / "residential_m2_profile_summary.md",
}

BAND_LABELS = ["4-6", "9-10", "13-14", "20-30", "30+"]


def load_m1() -> pd.DataFrame:
    if not M1_FILE.exists():
        raise FileNotFoundError(f"M1 file not found: {M1_FILE}")
    df = pd.read_csv(M1_FILE, dtype=str, low_memory=False)
    df.columns = [c.strip().lower() for c in df.columns]
    # casts
    for c in ["pv_dc_kw", "pv_ac_kw", "dc_ac_ratio", "battery_kwh", "has_battery", "big_roof_flag"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    # install_month
    if "install_month" in df.columns:
        # M1 stores string like '2024-07', keep as string but create datetime for sort
        df["install_month_dt"] = pd.to_datetime(df["install_month"].astype(str) + "-01", errors="coerce")
    else:
        df["install_month"] = np.nan
        df["install_month_dt"] = pd.NaT
    return df


def compute_ts_monthly(df: pd.DataFrame) -> pd.DataFrame:
    dfg = df.groupby("install_month").agg(
        projects=("pvd_id", "nunique"),
        attach_rate=("has_battery", lambda s: pd.to_numeric(s, errors="coerce").mean()),
        pv_dc_kw_median=("pv_dc_kw", "median"),
        dc_ac_ratio_median=("dc_ac_ratio", "median"),
        battery_kwh_median_all=("battery_kwh", "median"),
    ).reset_index()
    # battery_kwh median for battery-only
    has_batt = df[df["has_battery"] == 1]
    med_batt = has_batt.groupby("install_month").agg(battery_kwh_median_batt=("battery_kwh", "median")).reset_index()
    dfg = dfg.merge(med_batt, on="install_month", how="left")
    # sort by date
    if "install_month_dt" in df.columns:
        order = df.drop_duplicates("install_month")[["install_month", "install_month_dt"]].sort_values("install_month_dt")
        dfg = order.merge(dfg, on="install_month", how="left").drop(columns=["install_month_dt"])
    return dfg


def map_battery_band(x: float) -> str:
    if pd.isna(x) or x <= 0:
        return "NoBattery"
    if 4 <= x <= 6:
        return "4-6"
    if 9 <= x <= 10:
        return "9-10"
    if 13 <= x <= 14:
        return "13-14"
    if 20 <= x <= 30:
        return "20-30"
    if x > 30:
        return "30+"
    return "Other"


def compute_battery_bands_monthly(df: pd.DataFrame) -> pd.DataFrame:
    tmp = df.copy()
    tmp["band"] = df["battery_kwh"].apply(map_battery_band)
    dfg = (
        tmp.groupby(["install_month", "band"]).agg(n=("pvd_id", "nunique")).reset_index()
    )
    total = dfg.groupby("install_month")["n"].transform("sum")
    dfg["share"] = dfg["n"] / total
    return dfg


def compute_threshold_alignment_monthly(df: pd.DataFrame, thresholds=(10, 13.5, 20)) -> pd.DataFrame:
    rows = []
    for mon, g in df.groupby("install_month"):
        g_batt = g.copy()
        g_batt["battery_kwh"] = pd.to_numeric(g_batt["battery_kwh"], errors="coerce")
        total = len(g_batt)
        for th in thresholds:
            share = np.nan
            if total > 0:
                share = (g_batt["battery_kwh"] >= th).mean()
            rows.append({"install_month": mon, "threshold_kwh": th, "share_ge": share, "projects": total})
    return pd.DataFrame(rows)


def split_first_brand(cell: str) -> str:
    if pd.isna(cell):
        return np.nan
    parts = [p.strip() for p in str(cell).split(";") if p.strip()]
    return parts[0] if parts else np.nan


def compute_brand_topn_and_combos(df: pd.DataFrame, topn: int = 10) -> tuple[pd.DataFrame, pd.DataFrame]:
    # Primary brands (first one per field)
    for col in ["panel_brand", "inverter_brand", "battery_brand"]:
        if col in df.columns:
            df[col + "_primary"] = df[col].apply(split_first_brand)
        else:
            df[col + "_primary"] = np.nan

    counts = {}
    for col in ["panel_brand_primary", "inverter_brand_primary", "battery_brand_primary"]:
        vc = df[col].value_counts(dropna=True).reset_index()
        vc.columns = ["brand", "projects"]
        vc["category"] = col.replace("_primary", "")
        counts[col] = vc
    topn_df = pd.concat(counts.values(), ignore_index=True)
    topn_df = topn_df.sort_values(["category", "projects"], ascending=[True, False])
    # Keep topn per category
    topn_df = topn_df.groupby("category").head(topn).reset_index(drop=True)

    # Combos (primary only)
    combo = df[["panel_brand_primary", "inverter_brand_primary", "battery_brand_primary"]].copy()
    combo["combo"] = combo.apply(lambda r: f"{r['panel_brand_primary']} | {r['inverter_brand_primary']} | {r['battery_brand_primary']}", axis=1)
    combo_vc = combo["combo"].value_counts(dropna=True).reset_index()
    combo_vc.columns = ["combo", "projects"]
    return topn_df, combo_vc


def compute_prepost_by_state(df: pd.DataFrame) -> pd.DataFrame:
    # Define pre/post using M1 period_bucket or install_month
    if "period_bucket" in df.columns:
        def flag_prepost(x: str) -> str:
            if x == "2025H1":
                return "pre"
            if x == "2025H2":
                return "post"
            return "other"
        df["prepost"] = df["period_bucket"].astype(str).apply(flag_prepost)
    else:
        # fallback by month
        df["install_month_dt"] = pd.to_datetime(df["install_month"].astype(str) + "-01", errors="coerce")
        df["prepost"] = np.where(df["install_month_dt"] < pd.Timestamp("2025-07-01"), "pre",
                            np.where(df["install_month_dt"] >= pd.Timestamp("2025-07-01"), "post", "other"))

    g = df[df["prepost"].isin(["pre", "post"])].groupby(["state", "prepost"]).agg(
        projects=("pvd_id", "nunique"),
        attach_rate=("has_battery", lambda s: pd.to_numeric(s, errors="coerce").mean()),
        pv_dc_kw_median=("pv_dc_kw", "median"),
        dc_ac_ratio_median=("dc_ac_ratio", "median"),
        battery_kwh_median_all=("battery_kwh", "median"),
    ).reset_index()

    # Pivot pre/post to compute deltas
    piv = g.pivot_table(index="state", columns="prepost", values=["projects", "attach_rate", "pv_dc_kw_median", "dc_ac_ratio_median", "battery_kwh_median_all"]).reset_index()
    piv.columns = ["_".join([c for c in col if c]) for col in piv.columns.to_flat_index()]
    # Compute deltas (post - pre)
    for col in ["attach_rate", "pv_dc_kw_median", "dc_ac_ratio_median", "battery_kwh_median_all"]:
        if f"{col}_post" in piv.columns and f"{col}_pre" in piv.columns:
            piv[f"{col}_delta"] = piv[f"{col}_post"] - piv[f"{col}_pre"]
    return piv


def main() -> None:
    print("[M2] Loading M1 filtered dataset...")
    df = load_m1()
    if df.empty:
        print("[M2] No data. Abort.")
        return

    print("[M2] Computing monthly time series...")
    ts_monthly = compute_ts_monthly(df)
    ts_monthly.to_csv(OUTPUTS["ts_monthly"], index=False)

    print("[M2] Computing battery capacity bands (monthly)...")
    bands = compute_battery_bands_monthly(df)
    bands.to_csv(OUTPUTS["battery_bands_monthly"], index=False)

    print("[M2] Computing threshold alignment (monthly)...")
    thresh = compute_threshold_alignment_monthly(df)
    thresh.to_csv(OUTPUTS["threshold_alignment_monthly"], index=False)

    print("[M2] Computing brand Top-N and primary combos...")
    topn_df, combo_df = compute_brand_topn_and_combos(df.copy())
    topn_df.to_csv(OUTPUTS["brand_topn"], index=False)
    combo_df.to_csv(OUTPUTS["brand_combos"], index=False)

    print("[M2] Computing pre/post by state (2025H1 vs 2025H2)...")
    prepost = compute_prepost_by_state(df)
    prepost.to_csv(OUTPUTS["prepost_by_state"], index=False)

    print("[M2] Writing summary markdown...")
    # quick highlights (compute from raw df for robustness)
    df_num = df.copy()
    df_num["has_battery"] = pd.to_numeric(df_num["has_battery"], errors="coerce")
    if "period_bucket" in df_num.columns:
        pre_mask_raw = df_num["period_bucket"].astype(str).eq("2025H1")
        post_mask_raw = df_num["period_bucket"].astype(str).eq("2025H2")
    else:
        df_num["install_month_dt"] = pd.to_datetime(df_num["install_month"].astype(str) + "-01", errors="coerce")
        pre_mask_raw = df_num["install_month_dt"] < pd.Timestamp("2025-07-01")
        post_mask_raw = df_num["install_month_dt"] >= pd.Timestamp("2025-07-01")

    attach_pre = df_num.loc[pre_mask_raw, "has_battery"].mean()
    attach_post = df_num.loc[post_mask_raw, "has_battery"].mean()
    delta_attach = (attach_post - attach_pre) if pd.notna(attach_pre) and pd.notna(attach_post) else np.nan

    # best states by attach_rate delta
    if "attach_rate_delta" in prepost.columns:
        best_states = prepost.sort_values("attach_rate_delta", ascending=False).head(5)
    else:
        best_states = prepost.head(0)

    lines = []
    lines.append("# Residential M2 画像与事件研究（初步）\n")
    lines.append("## 关键发现（初稿）\n")
    lines.append(f"- pre（2025H1）平均 attach rate ≈ {attach_pre:.4f}" if pd.notna(attach_pre) else "- pre（2025H1）平均 attach rate ≈ nan")
    lines.append(f"- post（2025H2）平均 attach rate ≈ {attach_post:.4f}" if pd.notna(attach_post) else "- post（2025H2）平均 attach rate ≈ nan")
    lines.append(f"- 事件后 attach rate 变化（post-pre）≈ {delta_attach:.4f}" if pd.notna(delta_attach) else "- 事件后 attach rate 变化（post-pre）≈ nan")
    lines.append("")
    if not best_states.empty:
        lines.append("- 州别 attach rate 改善（Top-5）：")
        for _, r in best_states.iterrows():
            st = r.get("state_", r.get("state", "?"))
            delta = r.get("attach_rate_delta", np.nan)
            lines.append(f"  - {st}: Δattach_rate={delta}")
    lines.append("")
    lines.append("## 产出文件\n")
    for name, path in OUTPUTS.items():
        if name == "summary_md":
            continue
        lines.append(f"- {name}: {path.relative_to(PROJECT_ROOT)}")

    with open(OUTPUTS["summary_md"], "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("[M2] Done. Outputs:")
    for name, path in OUTPUTS.items():
        print(" -", path.relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    main()
