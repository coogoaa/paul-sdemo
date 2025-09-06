from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List

import math
import pandas as pd

# 占位：后续实现完整的与 Excel 一致的计算


def ceil_to(x: float, step: float) -> float:
    if step <= 0:
        return x
    return math.ceil(x / step) * step


def int_floor(x: float) -> int:
    return int(math.floor(x))


def safe_div(a: float, b: float):
    return a / b if b else float("inf")


def compute_plans_detailed(cfg) -> pd.DataFrame:
    # TODO: 复刻 proposal.py Plans_By_Columns 的所有字段
    cols = ["Plan A", "Plan B", "Plan C", "Plan D"]
    df = pd.DataFrame(index=[
        "solar_kw",
        "panel_count",
        "inverter_kw",
        "annual_generation_kwh",
        "total_cost",
        "price_base",
        "payback_base_years",
        "payback_low_years",
        "payback_high_years",
    ], columns=cols)
    return df


def compute_plans_simplified(cfg) -> pd.DataFrame:
    # TODO: 复刻 proposal.py Plans_Simplified 的所有字段
    cols = ["Plan A", "Plan B", "Plan C", "Plan D"]
    df = pd.DataFrame(index=[
        "solar_kw",
        "panel_count",
        "annual_generation_kwh",
        "total_hardware_cost",
        "total_cost",
        "price_base",
        "payback_base_years",
        "payback_low_years",
        "payback_high_years",
    ], columns=cols)
    return df


def compute_battery_retrofit(cfg) -> pd.DataFrame:
    # TODO: 复刻 proposal.py Battery_Retrofit 的所有字段
    cols = ["Retrofit A", "Retrofit B", "Retrofit C", "Retrofit D"]
    df = pd.DataFrame(index=[
        "battery_nominal_kwh",
        "usable_battery_capacity_kwh",
        "annual_shifted_kwh_est",
        "max_shiftable_kwh",
        "final_annual_shifted_kwh",
        "annual_savings",
        "total_cost",
        "price_base",
        "payback_years",
        "new_self_consumption_rate",
        "roi_warning",
    ], columns=cols)
    return df
