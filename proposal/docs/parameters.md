# 参数总览（InputsConfig）

以下表格整理了报价引擎 `proposal/schemas.py` 中 `InputsConfig` 的全部参数，包含英文键名、中文说明、默认值与备注。

| Parameter (EN) | 参数中文说明 | Value | Notes |
|---|---|---:|---|
| roof_total_area_m2 | 屋顶总面积 (m²) | 120.0 | 来自上游 3D/测绘估算 |
| roof_effective_area_m2 | 屋顶有效面积 (m²) | 80.0 | 过滤朝向/过小坡面后的有效面积 |
| roof_max_panels | 屋顶最大面板数 (块) | 16 | 上游计算得出/可人工修正 |
| panel_area_m2 | 单块面板面积 (m²) | 1.94 | 面板规格 |
| panel_power_kw | 单块面板功率 (kW) | 0.41 | 面板标称功率 |
| panel_unit_cost | 单块面板成本 (AUD/块) | 350 | 详细版使用 |
| inverter_unit_cost_per_kw | 逆变器成本 (AUD/kW) | 250 | 详细版使用 |
| hardware_cost_per_kw | 硬件包价 (AUD/kW) | 1200 | 简化版使用（含 PV+逆变器 等） |
| battery_unit_cost_per_kwh | 电池成本 (AUD/kWh) | 800 | |
| install_base_cost | 安装基础费用 (AUD) | 1000 | |
| install_cost_per_kw | 安装每 kW 费用 (AUD/kW) | 1000 | |
| dc_ac_ratio | 容配比 (DC/AC) | 1.33 | 影响逆变器容量取整 |
| yield_per_kw_per_year | 每 kW 年发电量 (kWh/kW/年) | 1460 | 兜底值；如接入 pvlib 则以模型为准 |
| baseline_self_consumption_rate | 基线自用率 | 0.30 | 无电池条件下的自用率估计 |
| plan_a_capacity_factor | 方案A 容量系数 | 0.2 | 参与计算装机 kW，并受上下限钳制 |
| plan_b_capacity_factor | 方案B 容量系数 | 0.5 | 同上 |
| plan_c_capacity_factor | 方案C 容量系数 | 0.8 | 同上 |
| plan_d_capacity_factor | 方案D 容量系数 | 1.0 | 同上 |
| plan_a_min_kw | 方案A 最小上装机下限 (kW) | 3.5 | 每方案单独上下限 |
| plan_a_max_kw | 方案A 最大上限 (kW) | 10.0 |  |
| plan_b_min_kw | 方案B 最小上装机下限 (kW) | 4.0 |  |
| plan_b_max_kw | 方案B 最大上限 (kW) | 13.3 |  |
| plan_c_min_kw | 方案C 最小上装机下限 (kW) | 6.0 |  |
| plan_c_max_kw | 方案C 最大上限 (kW) | 13.3 |  |
| plan_d_min_kw | 方案D 最小上装机下限 (kW) | 8.0 |  |
| plan_d_max_kw | 方案D 最大上限 (kW) | 20.0 |  |
| plan_a_target_sc_rate | 方案A 目标自用率 | 0.35 | 与基线之差用于推导电池容量（若>0） |
| plan_b_target_sc_rate | 方案B 目标自用率 | 0.45 |  |
| plan_c_target_sc_rate | 方案C 目标自用率 | 0.50 |  |
| plan_d_target_sc_rate | 方案D 目标自用率 | 0.60 |  |
| battery_dod | 电池放电深度 DoD | 0.90 | 用于电池标称容量计算 |
| battery_rte | 电池往返效率 RTE | 0.90 | 同上 |
| battery_install_base_cost | 电池安装基础费 (AUD) | 500 | |
| battery_install_cost_per_kwh | 电池安装每 kWh 费用 (AUD/kWh) | 50 | |
| battery_effective_usage_factor | 电池有效使用系数 | 0.90 | Retrofit 估算使用天数与利用率 |
| profit_margin_rate | 利润率 | 0.10 | 用于报价 `price_base = total_cost*(1+rate)` |
| price_range_percent | 报价浮动范围（占位） | 0.05 | 当前未直接用于公式，可扩展 |
| grid_buy_rate | 购电价 (AUD/kWh) | 0.33 | |
| grid_sell_rate | 馈网价/售电价 (AUD/kWh) | 0.07 | 校验不高于购电价（见校验器） |
| annual_home_usage_proxy_low | 家庭年用电代理-低 (kWh/年) | 3000 | 用于截断自用收益上限 |
| annual_home_usage_proxy_med | 家庭年用电代理-中 (kWh/年) | 6000 | 回本计算默认使用 `med` 作为上限 |
| annual_home_usage_proxy_high | 家庭年用电代理-高 (kWh/年) | 9000 | 可用于扩展多场景 |
| existing_solar_annual_gen_kwh | 既有系统估算年发电量 (kWh/年) | — | 可空（None）：为空则按屋顶估算 |
| existing_sc_rate | 既有系统基线自用率 | 0.30 | Retrofit 计算中使用 |
| retrofit_plan_a_kwh | Retrofit 建议容量 A (kWh) | 5 | 仅 Retrofit 表用 |
| retrofit_plan_b_kwh | Retrofit 建议容量 B (kWh) | 10 |  |
| retrofit_plan_c_kwh | Retrofit 建议容量 C (kWh) | 13.5 |  |
| retrofit_plan_d_kwh | Retrofit 建议容量 D (kWh) | 20 |  |

说明：
- 默认值来源于 `proposal/schemas.py` 中 `InputsConfig`，可在 Streamlit 侧边栏进行调整。
- `grid_sell_rate` 有校验：不允许高于 `grid_buy_rate`，如高于将被矫正为与 `buy` 相同。
- 详细/简化版均会在 `proposal/outputs/` 目录导出结果（Excel/JSON）。
