from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any
import pandas as pd

import sys
from pathlib import Path as _Path

# Prefer local-folder imports to avoid colliding with proposal/proposal.py top-level module
_HERE = _Path(__file__).parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from schemas import InputsConfig  # type: ignore
from calc_engine import (  # type: ignore
    compute_plans_detailed,
    compute_plans_simplified,
    _plan_target_sc,
)


def build_summary_payload(cfg: InputsConfig) -> Dict[str, Any]:
    """
    Build a compact summary covering the card metrics used in the H5 page,
    without changing the H5. This payload includes, per plan (A/B/C/D):
      - system_size_kw (solar_kw)
      - budget_low/high (incl. margin), derived from detailed low/high price assumptions
      - payback_base/low/high (years)
      - self_consumption_target (target_sc rate) and baseline_self_consumption_rate
      - annual_bill_savings_base/low/high
      - annual_generation_kwh
      - cost_total (detailed), plus breakdowns
    Also includes simplified total_hardware_cost for reference.
    """
    det = compute_plans_detailed(cfg)
    simp = compute_plans_simplified(cfg)

    plans = ["Plan A", "Plan B", "Plan C", "Plan D"]

    def get_price_low_high_for_plan(p: str) -> Dict[str, float]:
        # Reconstruct low/high price used in calc_engine (for consistency)
        # price_low = total_cost * 1.1 * (1 + margin)
        # price_high = total_cost * 0.9 * (1 + margin)
        total = float(det.loc["total_cost", p])
        margin = cfg.profit_margin_rate
        return {
            "low": total * 1.1 * (1 + margin),
            "high": total * 0.9 * (1 + margin),
        }

    data: Dict[str, Any] = {
        "meta": {
            "version": "1.0",
            "notes": "Summary aligns with calc_engine payback low/base/high scenarios.",
            "use_plan_limits": getattr(cfg, "use_plan_limits", False),
            "usage_cap_policy": getattr(cfg, "usage_cap_policy", "med"),
            "stc": {
                "enabled": getattr(cfg, "stc_enable", False),
                "zone_rating": getattr(cfg, "stc_zone_rating", None),
                "price_aud": getattr(cfg, "stc_price_aud", None),
                "years_to_2030": getattr(cfg, "stc_years_to_2030", None),
            },
            "battery_rebate": {
                "fixed_aud": getattr(cfg, "rebate_fixed_aud", 0.0),
                "per_kwh_aud": getattr(cfg, "rebate_per_kwh_aud", 0.0),
                "cap_aud": getattr(cfg, "rebate_cap_aud", 0.0),
                "stack_mode": getattr(cfg, "rebate_stack_mode", "stack"),
            },
            "rough_optimize": {
                "enabled": getattr(cfg, "rough_optimize_enable", False),
                "factor": getattr(cfg, "rough_optimize_factor", 1.0),
            },
            "capacity_caps": {
                "cap_mode": getattr(cfg, "cap_mode", "simple"),
                "facet_count": getattr(cfg, "facet_count", 0),
                "facet_max_panels": getattr(cfg, "facet_max_panels", 0),
                "facet_max_power_kw": getattr(cfg, "facet_max_power_kw", 0.0),
                "facet_panels_list": getattr(cfg, "facet_panels_list", []),
                "facet_power_kw_list": getattr(cfg, "facet_power_kw_list", []),
                "existing_kw_fraction_of_cap": getattr(cfg, "existing_kw_fraction_of_cap", 0.70),
            },
        },
        "baseline_self_consumption_rate": cfg.baseline_self_consumption_rate,
        "electricity_rates": {
            "buy": cfg.grid_buy_rate,
            "sell": cfg.grid_sell_rate,
        },
        "plans": {},
    }

    for idx, letter in enumerate(["A", "B", "C", "D"]):
        p = plans[idx]
        target_sc = _plan_target_sc(cfg, letter)

        price_range = get_price_low_high_for_plan(p)
        # annual bill savings equals annual_benefit in detailed table
        annual_saving_base = float(det.loc["price_base", p]) / float(det.loc["payback_base_years", p]) if det.loc["payback_base_years", p] not in (None, 0) else 0.0
        annual_saving_low = price_range["low"] / float(det.loc["payback_low_years", p]) if det.loc["payback_low_years", p] not in (None, 0) else 0.0
        annual_saving_high = price_range["high"] / float(det.loc["payback_high_years", p]) if det.loc["payback_high_years", p] not in (None, 0) else 0.0

        data["plans"][letter] = {
            "labels": {"name": p},
            "system_size_kw": float(det.loc["solar_kw", p]),
            "panel_count": int(det.loc["panel_count", p]) if not pd.isna(det.loc["panel_count", p]) else None,
            "annual_generation_kwh": float(det.loc["annual_generation_kwh", p]),
            "self_consumption_target": target_sc,
            "battery": {
                "nominal_kwh": float(det.loc["battery_nominal_kwh", p]),
                "has": bool(float(det.loc["battery_nominal_kwh", p]) > 0.0),
            },
            "budget": {
                "base": float(det.loc["price_base", p]),
                "low": float(price_range["low"]),
                "high": float(price_range["high"]),
            },
            "payback_years": {
                "base": float(det.loc["payback_base_years", p]),
                "low": float(det.loc["payback_low_years", p]),
                "high": float(det.loc["payback_high_years", p]),
            },
            "annual_bill_savings": {
                "base": float(annual_saving_base),
                "low": float(annual_saving_low),
                "high": float(annual_saving_high),
            },
            "costs_detailed": {
                "panels": float(det.loc["cost_panels", p]),
                "inverter": float(det.loc["cost_inverter", p]),
                "battery": float(det.loc["cost_battery", p]),
                "install": float(det.loc["cost_install", p]),
                "total": float(det.loc["total_cost", p]),
            },
            "costs_simplified": {
                "total_hardware_cost": float(simp.loc["total_hardware_cost", p]),
            },
        }

    return data


def export_summary_json(cfg: InputsConfig, out_path: str | Path) -> Path:
    payload = build_summary_payload(cfg)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2))
    return out_path


if __name__ == "__main__":
    cfg = InputsConfig.default()
    path = export_summary_json(cfg, Path(__file__).parent / "outputs" / "proposal_summary.json")
    print(f"Summary written to: {path}")
