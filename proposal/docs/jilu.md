
# 光伏与储能报价计算记录（jilu）

本文详细拆解当前实现的计算逻辑，逐步记录每个步骤的输入、输出、公式与参数来源（预设/计算/外部），便于核验与维护。

- 计算引擎：[proposal/calc_engine.py](cci:7://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/calc_engine.py:0:0-0:0)
- 参数模型：[proposal/schemas.py](cci:7://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/schemas.py:0:0-0:0)
- 界面：[proposal/app.py](cci:7://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/app.py:0:0-0:0)
- 逻辑概述：[proposal/docs/proposal_logic.md](cci:7://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/docs/proposal_logic.md:0:0-0:0)

## 约定与标注

- 参数来源标注
  - [P] 预设（默认值，可在 UI 中配置）
  - [C] 计算得到（运行时计算）
  - [E] 外部/经验值（估算或来自既有系统输入，可为 None）

- 取整约定
  - INT 向下取整：[int_floor(x) = floor(x)](cci:1://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/calc_engine.py:16:0-17:29)
  - CEILING 以步长向上取整：[ceil_to(x, step)](cci:1://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/calc_engine.py:10:0-13:37)
  - 本项目：逆变器容量向上取整到 0.1 kW；电池标称向上取整到 1 kWh

- 方案说明
  - 新建系统包含 A/B/C/D 四个方案（详细版与简化版）
  - 每个方案有独立的容量系数、目标自用率、最小/最大装机上下限（均可配置）

---

## 1. 参数清单（按类别）

以下参数在 [schemas.py](cci:7://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/schemas.py:0:0-0:0) 定义，并在 [app.py](cci:7://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/app.py:0:0-0:0) 侧边栏可配置（部分为扩展信息，当前计算未直接使用，但按“参数补齐”要求已露出）。

1) 屋顶/面板/发电
- `roof_max_panels` [P] 屋顶最大可装面板数（块）
- `panel_power_kw` [P] 单块面板功率（kW）
- `yield_per_kw_per_year` [P] 每 kW 年发电量（kWh/kW/年，兜底值）
- `dc_ac_ratio` [P] 容配比（DC/AC）
- `roof_total_area_m2` [P] 屋顶总面积（m²）[当前未直接用]
- `roof_effective_area_m2` [P] 屋顶有效面积（m²）[当前未直接用]
- `panel_area_m2` [P] 单块面板面积（m²）[当前未直接用]

2) 方案策略
- `plan_{a|b|c|d}_capacity_factor` [P] 容量系数
- `plan_{a|b|c|d}_target_sc_rate` [P] 目标自用率
- `plan_{a|b|c|d}_min_kw` / `plan_{a|b|c|d}_max_kw` [P] 方案装机下限/上限
- `baseline_self_consumption_rate` [P] 基线自用率

3) 成本与商务
- `panel_unit_cost` [P] 面板成本（AUD/块）
- `inverter_unit_cost_per_kw` [P] 逆变器成本（AUD/kW）
- `hardware_cost_per_kw` [P] 硬件包价（AUD/kW，简化版用）
- `install_base_cost` [P] 安装基础费（AUD）
- `install_cost_per_kw` [P] 安装每 kW 成本（AUD/kW）
- `profit_margin_rate` [P] 利润率
- `price_range_percent` [P] 报价浮动范围（占位，当前未参与计算）

4) 电价与负荷
- `grid_buy_rate` [P] 购电价（AUD/kWh）
- `grid_sell_rate` [P] 馈网价（AUD/kWh）
- `annual_home_usage_proxy_low/med/high` [P] 年用电代理（当前计算默认以 `med` 作为上限）

5) 既有系统（可空）
- `existing_solar_annual_gen_kwh` [E] 已有光伏系统年发电量（kWh/年），可为空
- `existing_sc_rate` [P] 已有系统基线自用率

6) 电池与 Retrofit
- `battery_dod` [P] 电池放电深度 DoD（0~1）
- `battery_rte` [P] 电池往返效率 RTE（0~1）
- `battery_unit_cost_per_kwh` [P] 电池成本（AUD/kWh）
- `battery_install_base_cost` [P] 电池安装基础费（AUD）
- `battery_install_cost_per_kwh` [P] 电池单位安装成本（AUD/kWh）
- `battery_effective_usage_factor` [P] 电池有效使用系数（0~1）
- `retrofit_plan_{a|b|c|d}_kwh` [P] 电池扩容档位（kWh）

---

## 2. 新建系统（详细版）计算步骤

函数：[compute_plans_detailed(cfg)](cci:1://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/calc_engine.py:67:0-143:13)  
输出：行 = 指标，列 = `Plan A/B/C/D`（DataFrame）

步骤 2.1 容量（solar_kw）[C]
- 输入：`roof_max_panels` [P], `panel_power_kw` [P], `plan_*_capacity_factor` [P], `plan_*_min/max_kw` [P]
- 公式（每方案独立钳制）：
  - `base = roof_max_panels * panel_power_kw * plan_x_capacity_factor`
  - `solar_kw = MAX(MIN(base, plan_x_max_kw), plan_x_min_kw)`

步骤 2.2 面板数（panel_count）[C]
- 输入：`solar_kw` [C], `panel_power_kw` [P]
- 公式：`panel_count = INT(solar_kw / panel_power_kw)`

步骤 2.3 逆变器（inverter_kw）[C]
- 输入：`solar_kw` [C], `dc_ac_ratio` [P]
- 公式：`inverter_kw = CEILING(solar_kw / dc_ac_ratio, 0.1)`

步骤 2.4 年发电（annual_generation_kwh）[C]
- 输入：`solar_kw` [C], `yield_per_kw_per_year` [P]
- 公式：`annual_generation_kwh = solar_kw * yield_per_kw_per_year`

步骤 2.5 每日需转移能量（daily_energy_to_shift_kwh）[C]
- 输入：`annual_generation_kwh` [C], `baseline_self_consumption_rate` [P], `plan_*_target_sc_rate` [P]
- 公式：`daily_energy_to_shift_kwh = (annual_generation_kwh / 365) * (target_sc - baseline_sc)`

步骤 2.6 电池标称（battery_nominal_kwh）[C]
- 输入：`daily_energy_to_shift_kwh` [C], `battery_dod` [P], `battery_rte` [P]
- 公式：若 `daily_shift > 0`：  
  `battery_nominal_kwh = CEILING(daily_shift / (battery_dod * battery_rte), 1.0)`  
  否则 `battery_nominal_kwh = 0`

步骤 2.7 商用品规建议（battery_pack_suggested_kwh）[C]
- 输入：`battery_nominal_kwh` [C]
- 规则：从 `[20, 13.5, 10, 6.5, 5]` 中选择“第一个 ≤ `battery_nominal_kwh` 的值”；否则取 5

步骤 2.8 成本拆分与合计 [C]
- 输入：
  - 面板：`panel_count` [C], `panel_unit_cost` [P]
  - 逆变器：`inverter_kw` [C], `inverter_unit_cost_per_kw` [P]
  - 电池：`battery_nominal_kwh` [C], `battery_unit_cost_per_kwh` [P]
  - 安装：`install_base_cost` [P], `install_cost_per_kw` [P], `solar_kw` [C]
- 公式：
  - `cost_panels = panel_count * panel_unit_cost`
  - `cost_inverter = inverter_kw * inverter_unit_cost_per_kw`
  - `cost_battery = battery_nominal_kwh * battery_unit_cost_per_kwh`
  - `cost_install = install_base_cost + solar_kw * install_cost_per_kw`
  - `total_cost = cost_panels + cost_inverter + cost_battery + cost_install`

步骤 2.9 报价（price_base）[C]
- 输入：`total_cost` [C], `profit_margin_rate` [P]
- 公式：`price_base = total_cost * (1 + profit_margin_rate)`

步骤 2.10 年收益与回本（基线/保守/乐观）[C]
- 中间函数：[_annual_benefit_from_gen(cfg, annual_gen, target_sc)](cci:1://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/calc_engine.py:60:0-64:65)
  - `used = MIN(annual_gen * target_sc, annual_home_usage_proxy_med)`
  - `export = MAX(annual_gen - used, 0)`
  - `annual_benefit = used * grid_buy_rate + export * grid_sell_rate`
- 基线：
  - `benefit_base = _annual_benefit_from_gen(annual_gen, target_sc)`
  - `payback_base_years = price_base / benefit_base`（≤0 则 Inf）
- 保守：
  - `low_gen = annual_gen * 0.85`
  - `benefit_low = _annual_benefit_from_gen(low_gen, target_sc) * 0.8`
  - `price_low = total_cost * 1.1 * (1 + profit_margin_rate)`
  - `payback_low_years = price_low / benefit_low`（≤0 则 Inf）
- 乐观：
  - `high_gen = annual_gen * 1.15`
  - `benefit_high = _annual_benefit_from_gen(high_gen, target_sc) * 1.2`
  - `price_high = total_cost * 0.9 * (1 + profit_margin_rate)`
  - `payback_high_years = price_high / benefit_high`（≤0 则 Inf）

输出（每列 A/B/C/D）：
- `solar_kw`, `panel_count`, `inverter_kw`, `annual_generation_kwh`
- `daily_energy_to_shift_kwh`, `battery_nominal_kwh`, `battery_pack_suggested_kwh`
- `cost_panels`, `cost_inverter`, `cost_battery`, `cost_install`, `total_cost`
- `price_base`, `payback_base_years`, `payback_low_years`, `payback_high_years`


2.11 保守/乐观情景的回本周期估算（详细版与简化版通用）

本项目在“基线”回本之外，同时估算“保守（Low）”与“乐观（High）”两种情景，以覆盖发电量、收益与成本在现实中的波动范围。

- 输入与中间量
  - annual_gen_base [C]：基线年发电量（由上文年发电公式得到）
  - target_sc [P]：方案目标自用率（A/B/C/D）
  - total_cost [C]：项目总成本（详见“成本拆分与合计”，或简化版的硬件+安装合计）
  - profit_margin_rate [P]：利润率
  - grid_buy_rate / grid_sell_rate [P]
  - 计算函数 [_annual_benefit_from_gen(cfg, annual_gen, target_sc)](cci:1://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/calc_engine.py:60:0-64:65)：
    - used = MIN(annual_gen * target_sc, annual_home_usage_proxy_med)
    - export = MAX(annual_gen - used, 0)
    - annual_benefit = used * grid_buy_rate + export * grid_sell_rate

- 基线（以便对比）
  - annual_benefit_base = [_annual_benefit_from_gen(cfg, annual_gen_base, target_sc)](cci:1://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/calc_engine.py:60:0-64:65)
  - price_base = total_cost * (1 + profit_margin_rate)
  - payback_base_years = price_base / annual_benefit_base
  - 若 annual_benefit_base ≤ 0，则 payback_base_years = Inf

- 保守（Low）情景
  - 年发电量下调：annual_gen_low = annual_gen_base * 0.85
  - 收益下调：annual_benefit_low = [_annual_benefit_from_gen(cfg, annual_gen_low, target_sc)](cci:1://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/calc_engine.py:60:0-64:65) × 0.8
  - 成本上调：price_low = (total_cost × 1.1) × (1 + profit_margin_rate)
  - 回本：payback_low_years = price_low / annual_benefit_low
  - 若 annual_benefit_low ≤ 0，则 payback_low_years = Inf

- 乐观（High）情景
  - 年发电量上调：annual_gen_high = annual_gen_base * 1.15
  - 收益上调：annual_benefit_high = [_annual_benefit_from_gen(cfg, annual_gen_high, target_sc)](cci:1://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/calc_engine.py:60:0-64:65) × 1.2
  - 成本下调：price_high = (total_cost × 0.9) × (1 + profit_margin_rate)
  - 回本：payback_high_years = price_high / annual_benefit_high
  - 若 annual_benefit_high ≤ 0，则 payback_high_years = Inf

- 说明
  - 以上系数（0.85/0.8/1.1/1.15/1.2/0.9）用于覆盖现实波动区间，来源于报价经验假设，与 [calc_engine.py](cci:7://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/calc_engine.py:0:0-0:0) 实现一致：
    - compute_plans_detailed() 与 compute_plans_simplified() 中的对应代码段：
      - Low: gen×0.85, benefit×0.8, total_cost×1.1
      - High: gen×1.15, benefit×1.2, total_cost×0.9
  - “简化版”的回本估算与“详细版”保持相同模式，只是 total_cost 的构成简化为“硬件包价 + 安装”。



## 3. 新建系统（简化版）计算步骤

函数：[compute_plans_simplified(cfg)](cci:1://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/calc_engine.py:41:0-55:13)  
输出：行 = 指标，列 = `Plan A/B/C/D`

简化要点
- 以 `hardware_cost_per_kw` 替代面板+逆变器成本拆分
- 电池成本计算与详细版保持一致（确保成本准确性）
- 收益/回本逻辑与详细版一致

步骤 3.1~3.4
- 与详细版相同：容量、面板数、年发电、目标自用率

步骤 3.5 成本与报价 [C]
- 电池成本（复用详细版逻辑）：
  - `daily_shift = (annual_gen / 365) * (target_sc - baseline_sc)`
  - `battery_nominal = CEILING(daily_shift / (battery_dod * battery_rte), 1.0)` 若 daily_shift > 0，否则为 0
  - `cost_battery = battery_nominal * battery_unit_cost_per_kwh`
- `total_hardware_cost = solar_kw * hardware_cost_per_kw`
- `cost_install = install_base_cost + solar_kw * install_cost_per_kw`
- `total_cost = total_hardware_cost + cost_battery + cost_install`
- `price_base = total_cost * (1 + profit_margin_rate)`

步骤 3.6 回本（基线/保守/乐观）[C]
- 用 [_annual_benefit_from_gen](cci:1://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/calc_engine.py:60:0-64:65) 计算，取商

输出：
- `solar_kw`, `panel_count`, `annual_generation_kwh`
- `total_hardware_cost`, `cost_battery`, `cost_install`, `total_cost`, `price_base`
- `payback_base_years`, `payback_low_years`, `payback_high_years`

---

## 4. 储能扩容（Battery Retrofit）计算步骤

函数：[compute_battery_retrofit(cfg)](cci:1://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/calc_engine.py:58:0-74:13)  
输出：列 = `Retrofit A/B/C/D`，行如下一组指标

步骤 4.1 电池名义容量（battery_nominal_kwh）[P]
- 来自 UI：`retrofit_plan_a/b/c/d_kwh`

步骤 4.2 可用容量（usable_battery_capacity_kwh）[C]
- `usable = nominal * battery_dod`

步骤 4.3 年可转移电量估计（annual_shifted_kwh_est）[C]
- `annual_est = usable * battery_effective_usage_factor * 365`

步骤 4.4 最大可转移上限（max_shiftable_kwh）[C]
- 若 `existing_solar_annual_gen_kwh` [E] 为空/0：
  - `estimated_gen = roof_max_panels * panel_power_kw * 0.7 * 1200`（经验估算）
  - `max_shift = estimated_gen * (1 - existing_sc_rate)`
- 否则：
  - `max_shift = existing_solar_annual_gen_kwh * (1 - existing_sc_rate)`

步骤 4.5 实际可转移（final_annual_shifted_kwh）[C]
- `final_shift = MIN(annual_est, max_shift)`

步骤 4.6 年节省（annual_savings）[C]
- `annual_savings = final_shift * (grid_buy_rate - grid_sell_rate)`

步骤 4.7 成本与报价 [C]
- `total_cost = nominal * battery_unit_cost_per_kwh + battery_install_base_cost + nominal * battery_install_cost_per_kwh`
- `price_base = total_cost * (1 + profit_margin_rate)`

步骤 4.8 回本年限（payback_years）[C]
- `payback = price_base / annual_savings`（≤0 则 Inf）

步骤 4.9 新自用率（new_self_consumption_rate）[C]
- 若 `existing_solar_annual_gen_kwh` 为空/0：
  - `denom = estimated_gen`
  - `numer = estimated_gen * existing_sc_rate + final_shift`
- 否则：
  - `denom = existing_solar_annual_gen_kwh`
  - `numer = existing_solar_annual_gen_kwh * existing_sc_rate + final_shift`
- `new_sc = numer / denom`（denom=0 取 0）

步骤 4.10 ROI 提示（roi_warning）[C]
- 若 `final_shift < 500 kWh/年` → `"Low ROI - small export available"`，否则 `"OK"`
- 注：阈值 500 可在后续迭代中做成可配置项

输出：
- `battery_nominal_kwh`, `usable_battery_capacity_kwh`, `annual_shifted_kwh_est`
- `max_shiftable_kwh`, `final_annual_shifted_kwh`
- `annual_savings`, `total_cost`, `price_base`, `payback_years`
- `new_self_consumption_rate`, `roi_warning`

---

## 5. 边界与异常处理

- 回本年限：当收益（或年节省）≤ 0 时为 `Inf`
- 电池标称：当 `daily_energy_to_shift_kwh <= 0` 时置 0
- 简化版：默认不计电池成本；可接入详细版逻辑扩展
- 估算发电量：`estimated_gen = roof_max_panels * panel_power_kw * 0.7 * 1200` 为经验估算，可替换为更精细模型

---

## 6. 默认值速查（可在 UI 修改）

- 方案上下限（kW）：A 3.5~10，B 4~13.3，C 6~13.3，D 8~20
- 年用电代理：low=3000，med=6000，high=9000
- 电池：DoD=0.9，RTE=0.9，有效系数示例=0.7
- 电价：购电 0.33，馈网 0.07（示例）
- 利润率：10%（示例）

---

## 7. 与 Excel 的一致性

- 详细/简化/Retrofit 三板块与 [proposal/proposal.py](cci:7://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/proposal.py:0:0-0:0) 的核心口径保持一致
- 新增：每方案独立上下限、年用电代理 Low/Med/High、既有系统输入（可空）

———————— 复制结束 ————————

请将以上内容粘贴保存到 [proposal/docs/jilu.md](cci:7://file:///Users/paulgao/Documents/augment-projects/sales_agent_demo/proposal/docs/jilu.md:0:0-0:0)。保存后回复我“已保存”，我会立刻提交本地 git。