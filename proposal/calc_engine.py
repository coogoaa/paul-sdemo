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
    # 计算需要多少个 step 单位
    steps_needed = x / step
    # 如果已经是整数倍，直接返回
    if abs(steps_needed - round(steps_needed)) < 1e-10:
        return round(steps_needed) * step
    # 否则向上取整
    return math.ceil(steps_needed) * step


def int_floor(x: float) -> int:
    return int(math.floor(x))


def safe_payback(price: float, annual_benefit: float):
    if annual_benefit is None or annual_benefit <= 0:
        return float("inf")
    return price / annual_benefit


def _plan_capacity(cfg, letter: str) -> float:
    """Compute solar_kw per plan with optional roof/facet caps.
    Strategy:
    - Define a capacity baseline using roof_max_power_kw_like:
      If facet info exists, use roof_max_power_kw = facet_count * facet_max_power_kw (simple sum); otherwise fallback to roof_max_panels*panel_power_kw.
    - Compute per-plan unconstrained = baseline * capacity_factor.
    - Apply cap depending on cfg.cap_mode:
      * simple: kw_cap = facet_count*facet_max_power_kw (if >0), else no cap
      * strict: kw_cap = min( sum facet power, panel-cap power ) where panel-cap power = min(roof_max_panels, facet_count*facet_max_panels)*panel_power_kw (when available)
    - Optionally apply per-plan min/max when use_plan_limits is True.
    """
    ppkw = cfg.panel_power_kw
    # capacity factors per plan
    capf = (
        cfg.plan_a_capacity_factor if letter == "A" else
        cfg.plan_b_capacity_factor if letter == "B" else
        cfg.plan_c_capacity_factor if letter == "C" else
        cfg.plan_d_capacity_factor
    )

    # Derive baseline "roof_max_power" style capacity
    facet_cnt = int(getattr(cfg, "facet_count", 0) or 0)
    facet_max_p_kw = float(getattr(cfg, "facet_max_power_kw", 0.0) or 0.0)
    facet_max_pan = int(getattr(cfg, "facet_max_panels", 0) or 0)
    roof_max_pan = int(getattr(cfg, "roof_max_panels", 0) or 0)
    # Prefer per-facet lists if provided
    try:
        power_list = list(getattr(cfg, "facet_power_kw_list", []) or [])
        power_list = [float(x) for x in power_list if x is not None]
    except Exception:
        power_list = []
    try:
        panels_list = list(getattr(cfg, "facet_panels_list", []) or [])
        panels_list = [int(x) for x in panels_list if x is not None]
    except Exception:
        panels_list = []

    sum_power_list = sum(power_list) if len(power_list) > 0 else 0.0
    sum_panels_list = sum(panels_list) if len(panels_list) > 0 else 0

    sum_facet_power = sum_power_list if sum_power_list > 0 else (facet_cnt * facet_max_p_kw if (facet_cnt > 0 and facet_max_p_kw > 0) else 0.0)
    sum_facet_panels = sum_panels_list if sum_panels_list > 0 else (facet_cnt * facet_max_pan if (facet_cnt > 0 and facet_max_pan > 0) else 0)
    baseline_kw = sum_facet_power if sum_facet_power > 0 else (roof_max_pan * ppkw)

    unconstrained = baseline_kw * capf

    # Compute caps
    cap_mode = getattr(cfg, "cap_mode", "simple")
    kw_cap = float("inf")
    if sum_facet_power > 0:
        if cap_mode == "strict":
            panel_cap_count = min(roof_max_pan if roof_max_pan > 0 else float("inf"),
                                   sum_facet_panels if sum_facet_panels > 0 else (facet_cnt * facet_max_pan if (facet_cnt > 0 and facet_max_pan > 0) else float("inf")))
            panel_cap_kw = panel_cap_count * ppkw if panel_cap_count != float("inf") else float("inf")
            kw_cap = min(sum_facet_power, panel_cap_kw)
        else:
            kw_cap = sum_facet_power

    solar_kw = min(unconstrained, kw_cap)

    # Optional per-plan min/max when enabled
    if getattr(cfg, "use_plan_limits", False):
        if letter == "A":
            solar_kw = max(min(solar_kw, cfg.plan_a_max_kw), cfg.plan_a_min_kw)
        elif letter == "B":
            solar_kw = max(min(solar_kw, cfg.plan_b_max_kw), cfg.plan_b_min_kw)
        elif letter == "C":
            solar_kw = max(min(solar_kw, cfg.plan_c_max_kw), cfg.plan_c_min_kw)
        else:
            solar_kw = max(min(solar_kw, cfg.plan_d_max_kw), cfg.plan_d_min_kw)

    return solar_kw


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
    # Default (legacy) behavior uses MED cap
    used = min(annual_gen * target_sc, cfg.annual_home_usage_proxy_med)
    export = max(annual_gen - used, 0)
    return used * cfg.grid_buy_rate + export * cfg.grid_sell_rate


def _plan_usage_cap(cfg, letter: str) -> float:
    """Return usage cap per policy.
    - If cfg.usage_cap_policy == 'med': always MED
    - If 'per_plan': A->low, B->med, C/D->high
    """
    policy = getattr(cfg, "usage_cap_policy", "med")
    if policy == "per_plan":
        if letter == "A":
            return cfg.annual_home_usage_proxy_low
        elif letter == "B":
            return cfg.annual_home_usage_proxy_med
        else:
            return cfg.annual_home_usage_proxy_high
    # default: med
    return cfg.annual_home_usage_proxy_med


def _annual_benefit_from_gen_cap(cfg, annual_gen: float, target_sc: float, cap: float) -> float:
    used = min(annual_gen * target_sc, cap)
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
        # 改为：按自用率推算电池标称容量，保留两位小数（不再向上取整到 1kWh）
        batt_nominal = round(daily_shift / (cfg.battery_dod * cfg.battery_rte), 2) if daily_shift > 0 else 0.0
        # 商用品规建议暂不采用靠档显示（置为空）
        pack = float('nan')

        cost_panels = panel_count * cfg.panel_unit_cost
        cost_inverter = inverter_kw * cfg.inverter_unit_cost_per_kw
        cost_battery = batt_nominal * cfg.battery_unit_cost_per_kwh
        cost_install = cfg.install_base_cost + (solar_kw * cfg.install_cost_per_kw)
        total_cost = cost_panels + cost_inverter + cost_battery + cost_install
        price_base = total_cost * (1 + cfg.profit_margin_rate)

        # Payback variants
        cap = _plan_usage_cap(cfg, letter)
        base_benefit = _annual_benefit_from_gen_cap(cfg, annual_gen, target_sc, cap)
        payback_base = safe_payback(price_base, base_benefit)

        low_gen = annual_gen * 0.85
        low_target_benefit = _annual_benefit_from_gen_cap(cfg, low_gen, target_sc, cap) * 0.8
        payback_low = safe_payback(total_cost * 1.1 * (1 + cfg.profit_margin_rate), low_target_benefit)

        high_gen = annual_gen * 1.15
        high_target_benefit = _annual_benefit_from_gen_cap(cfg, high_gen, target_sc, cap) * 1.2
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

        # 计算电池成本（复用详细版逻辑，保留两位小数）
        daily_shift = (annual_gen / 365.0) * (target_sc - cfg.baseline_self_consumption_rate)
        battery_nominal = round(daily_shift / (cfg.battery_dod * cfg.battery_rte), 2) if daily_shift > 0 else 0.0
        cost_battery = battery_nominal * cfg.battery_unit_cost_per_kwh

        total_hardware_cost = solar_kw * cfg.hardware_cost_per_kw
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
    esg = cfg.existing_solar_annual_gen_kwh
    # Fallback existing_gen using roof/facet cap and fraction
    if esg is None or esg == 0:
        facet_cnt = int(getattr(cfg, "facet_count", 0) or 0)
        facet_max_p_kw = float(getattr(cfg, "facet_max_power_kw", 0.0) or 0.0)
        facet_max_pan = int(getattr(cfg, "facet_max_panels", 0) or 0)
        roof_max_pan = int(getattr(cfg, "roof_max_panels", 0) or 0)
        try:
            power_list = list(getattr(cfg, "facet_power_kw_list", []) or [])
            power_list = [float(x) for x in power_list if x is not None]
        except Exception:
            power_list = []
        try:
            panels_list = list(getattr(cfg, "facet_panels_list", []) or [])
            panels_list = [int(x) for x in panels_list if x is not None]
        except Exception:
            panels_list = []
        sum_power_list = sum(power_list) if len(power_list) > 0 else 0.0
        sum_panels_list = sum(panels_list) if len(panels_list) > 0 else 0
        sum_facet_power = sum_power_list if sum_power_list > 0 else (facet_cnt * facet_max_p_kw if (facet_cnt > 0 and facet_max_p_kw > 0) else 0.0)
        sum_facet_panels = sum_panels_list if sum_panels_list > 0 else (facet_cnt * facet_max_pan if (facet_cnt > 0 and facet_max_pan > 0) else 0)
        if getattr(cfg, "cap_mode", "simple") == "strict" and sum_facet_power > 0:
            panel_cap_count = min(roof_max_pan if roof_max_pan > 0 else float("inf"),
                                   sum_facet_panels if sum_facet_panels > 0 else (facet_cnt * facet_max_pan if (facet_cnt > 0 and facet_max_pan > 0) else float("inf")))
            panel_cap_kw = panel_cap_count * cfg.panel_power_kw if panel_cap_count != float("inf") else float("inf")
            cap_kw = min(sum_facet_power, panel_cap_kw)
        else:
            cap_kw = sum_facet_power if sum_facet_power > 0 else (roof_max_pan * cfg.panel_power_kw)
        existing_kw = cap_kw * float(getattr(cfg, "existing_kw_fraction_of_cap", 0.70) or 0.0)
        estimated_gen = existing_kw * cfg.yield_per_kw_per_year
    else:
        estimated_gen = esg

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
