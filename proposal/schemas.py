from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, validator


class InputsConfig(BaseModel):
    # 屋顶/面板/发电参数
    roof_total_area_m2: float = Field(120.0)
    roof_effective_area_m2: float = Field(80.0)
    roof_max_panels: int = Field(16, ge=0)
    panel_area_m2: float = Field(1.9, gt=0)
    panel_power_kw: float = Field(0.44, gt=0)

    # 成本参数（详细版）
    panel_unit_cost: float = Field(350, ge=0)
    inverter_unit_cost_per_kw: float = Field(250, ge=0)

    # 成本参数（简化版）
    hardware_cost_per_kw: float = Field(1200, ge=0)

    # 电池与安装
    battery_unit_cost_per_kwh: float = Field(800, ge=0)
    install_base_cost: float = Field(1000, ge=0)
    install_cost_per_kw: float = Field(1000, ge=0)

    # 比率与年发电兜底
    dc_ac_ratio: float = Field(1.33, gt=0)
    yield_per_kw_per_year: float = Field(1526, gt=0)

    # 自用率
    baseline_self_consumption_rate: float = Field(0.30, ge=0, le=1)

    # 方案容量系数与目标自用率
    plan_a_capacity_factor: float = Field(0.2, ge=0)
    plan_b_capacity_factor: float = Field(0.5, ge=0)
    plan_c_capacity_factor: float = Field(0.8, ge=0)
    plan_d_capacity_factor: float = Field(1.0, ge=0)

    # 每方案装机上下限（新增）
    plan_a_min_kw: float = Field(3.5, ge=0)
    plan_a_max_kw: float = Field(10.0, ge=0)
    plan_b_min_kw: float = Field(4.0, ge=0)
    plan_b_max_kw: float = Field(13.3, ge=0)
    plan_c_min_kw: float = Field(6.0, ge=0)
    plan_c_max_kw: float = Field(13.3, ge=0)
    plan_d_min_kw: float = Field(8.0, ge=0)
    plan_d_max_kw: float = Field(20.0, ge=0)

    plan_a_target_sc_rate: float = Field(0.30, ge=0, le=1)
    plan_b_target_sc_rate: float = Field(0.45, ge=0, le=1)
    plan_c_target_sc_rate: float = Field(0.50, ge=0, le=1)
    plan_d_target_sc_rate: float = Field(0.60, ge=0, le=1)

    # 策略开关
    # 是否启用每方案装机上下限（默认关闭，回归原始：仅按屋顶上限与容量系数计算）
    use_plan_limits: bool = Field(False)
    # 回本期自用上限策略：'med' 统一使用 MED；'per_plan' 按方案二映射
    usage_cap_policy: str = Field("med")

    # 电池参数
    battery_dod: float = Field(0.90, ge=0, le=1)
    battery_rte: float = Field(0.90, ge=0, le=1)
    battery_install_base_cost: float = Field(500, ge=0)
    battery_install_cost_per_kwh: float = Field(50, ge=0)
    battery_effective_usage_factor: float = Field(0.90, ge=0, le=1)

    # 商务
    profit_margin_rate: float = Field(0.10, ge=0)
    price_range_percent: float = Field(0.05, ge=0)

    # 电价
    grid_buy_rate: float = Field(0.33, ge=0)
    grid_sell_rate: float = Field(0.07, ge=0)

    # 家用电量代理
    annual_home_usage_proxy_low: float = Field(3000, ge=0)
    annual_home_usage_proxy_med: float = Field(6000, ge=0)
    annual_home_usage_proxy_high: float = Field(9000, ge=0)

    # 既有系统
    existing_solar_annual_gen_kwh: Optional[float] = Field(None)
    existing_sc_rate: float = Field(0.30, ge=0, le=1)

    # Retrofit 容量建议
    retrofit_plan_a_kwh: float = Field(5, ge=0)
    retrofit_plan_b_kwh: float = Field(10, ge=0)
    retrofit_plan_c_kwh: float = Field(13.5, ge=0)
    retrofit_plan_d_kwh: float = Field(20, ge=0)

    @validator(
        "grid_sell_rate",
        always=True,
    )
    def _sell_not_higher_than_buy(cls, v, values):
        buy = values.get("grid_buy_rate", 0.33)
        if v > buy:
            # 若馈网价大于购电价，给出温和矫正（可在 UI 中提示）
            return buy
        return v

    @classmethod
    def default(cls) -> "InputsConfig":
        return cls()
