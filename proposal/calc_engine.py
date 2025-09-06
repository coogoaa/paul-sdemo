from __future__ import annotations
from typing import Dict, List, Tuple

import math
import pandas as pd


# ===============
# Helper functions
# ===============
def ceil_to(x: float, step: float) -> float:
    if step <= 0:
        return x
    return math.ceil(x / step) * step


def int_floor(x: float) -> int:
    return int(math.floor(x))


def safe_payback(price: float, annual_benefit: float):
    if annual_benefit is None or annual_benefit <= 0:
        return float("inf")
    return price / annual_benefit


def _plan_capacity(cfg, letter: str) -> float:
    # solar_kw capacity by plan with per-plan min/max
    max_panels = cfg.roof_max_panels
    ppkw = cfg.panel_power_kw
    if letter == "A":
        capf = cfg.plan_a_capacity_factor
        base = max_panels * ppkw * capf
        return max(min(base, cfg.plan_a_max_kw), cfg.plan_a_min_kw)
    elif letter == "B":
        capf = cfg.plan_b_capacity_factor
        base = max_panels * ppkw * capf
        return max(min(base, cfg.plan_b_max_kw), cfg.plan_b_min_kw)
    elif letter == "C":
        capf = cfg.plan_c_capacity_factor
        base = max_panels * ppkw * capf
        return max(min(base, cfg.plan_c_max_kw), cfg.plan_c_min_kw)
    else:
        capf = cfg.plan_d_capacity_factor
        base = max_panels * ppkw * capf
        return max(min(base, cfg.plan_d_max_kw), cfg.plan_d_min_kw)


def _plan_target_sc(cfg, letter: str) -> float:
    return (
        cfg.plan_a_target_sc_rate
        if letter == "A"
        else cfg.plan_b_target_sc_rate
        if letter == "B"
        else cfg.plan_c_target_sc_rate
        if letter == "C"
        else cfg.plan_d_target_sc_rate
    )


def _annual_benefit_from_gen(cfg, annual_gen: float, target_sc: float) -> float:
    # Benefit = MIN(annual_gen*target_sc, usage_med)*buy + (annual_gen - MIN(...))*sell
    used = min(annual_gen * target_sc, cfg.annual_home_usage_proxy_med)
    export = max(annual_gen - used, 0)
    return used * cfg.grid_buy_rate + export * cfg.grid_sell_rate


def compute_plans_detailed(cfg) -> pd.DataFrame:
    cols = ["Plan A", "Plan B", "Plan C", "Plan D"]
    index = [
        "solar_kw",
        "panel_count",
        "inverter_kw",
        "annual_generation_kwh",
        "daily_energy_to_shift_kwh",
        "battery_nominal_kwh",
        "battery_pack_suggested_kwh",
        "cost_panels",
        "cost_inverter",
        "cost_battery",
        "cost_install",
        "total_cost",
        "price_base",
        "payback_base_years",
        "payback_low_years",
        "payback_high_years",
    ]
    df = pd.DataFrame(index=index, columns=cols, dtype=float)

    for i, letter in enumerate(["A", "B", "C", "D"]):
        col = cols[i]
        solar_kw = _plan_capacity(cfg, letter)
        panel_count = int_floor(solar_kw / cfg.panel_power_kw)
        inverter_kw = ceil_to(solar_kw / cfg.dc_ac_ratio, 0.1)
        annual_gen = solar_kw * cfg.yield_per_kw_per_year
        target_sc = _plan_target_sc(cfg, letter)
        daily_shift = (annual_gen / 365.0) * (target_sc - cfg.baseline_self_consumption_rate)
        batt_nominal = ceil_to(daily_shift / (cfg.battery_dod * cfg.battery_rte), 1.0) if daily_shift > 0 else 0.0
        # suggested pack ladder: 20, 13.5, 10, 6.5, 5
        pack = 5.0
        for p in [20.0, 13.5, 10.0, 6.5, 5.0]:
            if batt_nominal >= p:
                pack = p
                break

        cost_panels = panel_count * cfg.panel_unit_cost
        cost_inverter = inverter_kw * cfg.inverter_unit_cost_per_kw
        cost_battery = batt_nominal * cfg.battery_unit_cost_per_kwh
        cost_install = cfg.install_base_cost + (solar_kw * cfg.install_cost_per_kw)
        total_cost = cost_panels + cost_inverter + cost_battery + cost_install
        price_base = total_cost * (1 + cfg.profit_margin_rate)

        # Payback variants
        base_benefit = _annual_benefit_from_gen(cfg, annual_gen, target_sc)
        payback_base = safe_payback(price_base, base_benefit)

        low_gen = annual_gen * 0.85
        low_target_benefit = _annual_benefit_from_gen(cfg, low_gen, target_sc) * 0.8
        payback_low = safe_payback(total_cost * 1.1 * (1 + cfg.profit_margin_rate), low_target_benefit)

        high_gen = annual_gen * 1.15
        high_target_benefit = _annual_benefit_from_gen(cfg, high_gen, target_sc) * 1.2
        payback_high = safe_payback(total_cost * 0.9 * (1 + cfg.profit_margin_rate), high_target_benefit)

        df.loc[:, col] = [
            solar_kw,
            panel_count,
            inverter_kw,
            annual_gen,
            daily_shift,
            batt_nominal,
            pack,
            cost_panels,
            cost_inverter,
            cost_battery,
            cost_install,
            total_cost,
            price_base,
            payback_base,
            payback_low,
            payback_high,
        ]

    return df


def compute_plans_simplified(cfg) -> pd.DataFrame:
    cols = ["Plan A", "Plan B", "Plan C", "Plan D"]
    index = [
        "solar_kw",
        "panel_count",
        "annual_generation_kwh",
        "total_hardware_cost",
        "cost_battery",
        "cost_install",
        "total_cost",
        "price_base",
        "payback_base_years",
        "payback_low_years",
        "payback_high_years",
    ]
    df = pd.DataFrame(index=index, columns=cols, dtype=float)

    for i, letter in enumerate(["A", "B", "C", "D"]):
        col = cols[i]
        solar_kw = _plan_capacity(cfg, letter)
        panel_count = int_floor(solar_kw / cfg.panel_power_kw)
        annual_gen = solar_kw * cfg.yield_per_kw_per_year
        target_sc = _plan_target_sc(cfg, letter)

        total_hardware_cost = solar_kw * cfg.hardware_cost_per_kw
        cost_battery = 0.0  # 简化版默认不计电池
        cost_install = cfg.install_base_cost + (solar_kw * cfg.install_cost_per_kw)
        total_cost = total_hardware_cost + cost_battery + cost_install
        price_base = total_cost * (1 + cfg.profit_margin_rate)

        base_benefit = _annual_benefit_from_gen(cfg, annual_gen, target_sc)
        payback_base = safe_payback(price_base, base_benefit)

        low_gen = annual_gen * 0.85
        low_target_benefit = _annual_benefit_from_gen(cfg, low_gen, target_sc) * 0.8
        payback_low = safe_payback(total_cost * 1.1 * (1 + cfg.profit_margin_rate), low_target_benefit)

        high_gen = annual_gen * 1.15
        high_target_benefit = _annual_benefit_from_gen(cfg, high_gen, target_sc) * 1.2
        payback_high = safe_payback(total_cost * 0.9 * (1 + cfg.profit_margin_rate), high_target_benefit)

        df.loc[:, col] = [
            solar_kw,
            panel_count,
            annual_gen,
            total_hardware_cost,
            cost_battery,
            cost_install,
            total_cost,
            price_base,
            payback_base,
            payback_low,
            payback_high,
        ]

    return df


def compute_battery_retrofit(cfg) -> pd.DataFrame:
    cols = ["Retrofit A", "Retrofit B", "Retrofit C", "Retrofit D"]
    index = [
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
    ]
    df = pd.DataFrame(index=index, columns=cols, dtype=float)

    sizes = [
        cfg.retrofit_plan_a_kwh,
        cfg.retrofit_plan_b_kwh,
        cfg.retrofit_plan_c_kwh,
        cfg.retrofit_plan_d_kwh,
    ]

    # Estimate of export energy without explicit existing solar input
    estimated_gen = cfg.roof_max_panels * cfg.panel_power_kw * 0.7 * 1200
    esg = cfg.existing_solar_annual_gen_kwh

    for i, name in enumerate(cols):
        nominal = sizes[i]
        usable = nominal * cfg.battery_dod
        annual_est = usable * cfg.battery_effective_usage_factor * 365.0
        max_shift = (
            estimated_gen * (1 - cfg.existing_sc_rate)
            if esg is None or esg == 0
            else esg * (1 - cfg.existing_sc_rate)
        )
        final_shift = min(annual_est, max_shift)
        annual_savings = final_shift * (cfg.grid_buy_rate - cfg.grid_sell_rate)

        total_cost = (
            nominal * cfg.battery_unit_cost_per_kwh
            + cfg.battery_install_base_cost
            + nominal * cfg.battery_install_cost_per_kwh
        )
        price_base = total_cost * (1 + cfg.profit_margin_rate)
        payback = safe_payback(price_base, annual_savings)

        # new self-consumption rate
        if esg is None or esg == 0:
            denom = estimated_gen
            numer = estimated_gen * cfg.existing_sc_rate + final_shift
        else:
            denom = esg
            numer = esg * cfg.existing_sc_rate + final_shift
        new_sc = numer / denom if denom else 0

        roi_warning = "Low ROI - small export available" if final_shift < 500 else "OK"

        df.loc[:, name] = [
            nominal,
            usable,
            annual_est,
            max_shift,
            final_shift,
            annual_savings,
            total_cost,
            price_base,
            payback,
            new_sc,
            roi_warning,
        ]

    return df
