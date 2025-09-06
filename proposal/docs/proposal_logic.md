# proposal/proposal.py 逻辑说明（详细版）

本文档系统梳理 `proposal/proposal.py` 中两类 Excel 生成逻辑：
- create_detailed_file(path)：详细版，包含面板/逆变器/电池分项成本与取整逻辑
- create_simplified_file(path)：简化版，使用每 kW 硬件打包成本进行快速报价

并说明各输入参数、各工作表的字段、关键公式、取整规则与回本期估算方法，以及电池改造（Battery Retrofit）场景逻辑。

---

## 1. 依赖与总体结构

- 依赖库：`openpyxl`
  - Workbook、工作表样式 `Font`
  - 工具函数 `get_column_letter`
- 主要函数：
  - `create_detailed_file(path)`：生成包含 `Inputs`、`Plans_By_Columns`、`Battery_Retrofit`、`Readme_Chinese` 的工作簿。
  - `create_simplified_file(path)`：生成包含 `Inputs`、`Plans_Simplified`、`Battery_Retrofit`、`Readme_Chinese` 的工作簿。
- 收尾：自带示例调用将文件保存至 `/mnt/data/` 路径：
  - `solar_estimate_recommended.xlsx`
  - `solar_estimate_simplified_hardware_cost.xlsx`

> 提示：在本地或其他环境使用时，可根据需要修改输出路径，或封装为对外接口/CLI 参数。

---

## 2. 公共输入表 `Inputs`

两种函数都会先创建 `Inputs` 表，并写入四列：
- Parameter (EN)
- 参数中文说明
- Value
- Notes

各参数（键名 -> 含义/单位/备注），默认值在第三列 `Value`：

- roof_total_area_m2：屋顶总面积 (m²)
- roof_effective_area_m2：屋顶有效面积 (m²)
- roof_max_panels：屋顶最大面板数 (块)
- panel_area_m2：单块面板面积 (m²)
- panel_power_kw：单块面板功率 (kW)
- inverter_unit_cost_per_kw（仅详细版）：逆变器成本 (AUD/kW)
- panel_unit_cost（仅详细版）：单块面板成本 (AUD/块)
- hardware_cost_per_kw（仅简化版）：硬件成本 (AUD/kW)（包含 PV+逆变器 等的打包价）
- battery_unit_cost_per_kwh：电池成本 (AUD/kWh)
- install_base_cost：安装基础费用 (AUD)
- install_cost_per_kw：安装每 kW 费用 (AUD/kW)
- dc_ac_ratio：容配比 (DC/AC)
- yield_per_kw_per_year：每 kW 年发电量 (kWh/kW/年)，作为兜底值
- baseline_self_consumption_rate：无电池时基线自用率
- 方案容量系数/自用率目标：
  - plan_a_capacity_factor / plan_b_capacity_factor / plan_c_capacity_factor / plan_d_capacity_factor
  - plan_a_target_sc_rate / plan_b_target_sc_rate / plan_c_target_sc_rate / plan_d_target_sc_rate
- 容量上下限（已细化到每个方案，均可配置）：
  - plan_a_min_kw / plan_a_max_kw
  - plan_b_min_kw / plan_b_max_kw
  - plan_c_min_kw / plan_c_max_kw
  - plan_d_min_kw / plan_d_max_kw
- battery_dod：电池放电深度（Depth of Discharge）
- battery_rte：电池往返效率（Round-Trip Efficiency）
- battery_install_base_cost / battery_install_cost_per_kwh：电池安装基础费与单位 kWh 安装费
- battery_effective_usage_factor：电池有效使用系数
- profit_margin_rate：利润率（用于报价）
- price_range_percent：报价浮动范围（未在公式中直接使用，可拓展）
- 电价：
  - grid_buy_rate：购电价 (AUD/kWh)
  - grid_sell_rate：售电/馈网价 (AUD/kWh)
- annual_home_usage_proxy_low/med/high：年用电量代理（页面已提供三档，当前计算默认使用 med 作为上限）
- 既有系统相关：
  - existing_solar_annual_gen_kwh：已有光伏估算年发电量 (kWh/年)，留空则使用估算
  - existing_sc_rate：已有系统基线自用率
- Retrofit 电池建议容量（A/B/C/D）：retrofit_plan_a_kwh / b / c / d

备注：`Inputs` 表首行加粗；末尾会加入一段中文说明（不同版本有对应提示语）。

---

## 3. 详细版：`Plans_By_Columns`

### 3.1 字段列表

- solar_kw：光伏装机容量 (kW)
- panel_count：面板数量 (块)
- inverter_kw：逆变器容量 (kW)
- annual_generation_kwh：年发电量 (kWh/年)
- daily_energy_to_shift_kwh：每日需转移能量 (kWh/天)
- battery_nominal_kwh：建议电池标称容量 (kWh)
- battery_pack_suggested_kwh：推荐商用电池规格 (kWh)
- cost_panels：面板成本 (AUD)
- cost_inverter：逆变器成本 (AUD)
- cost_battery：电池成本 (AUD)
- cost_install：安装成本 (AUD)
- total_cost：项目总成本 (AUD)
- price_base：报价基准 (AUD)
- payback_base_years / payback_low_years / payback_high_years：回本年限（基线/保守/乐观）

列头为：参数（中/EN）/Plan A/Plan B/Plan C/Plan D。

### 3.2 关键公式与取整

以下以某列 `col` 表示当前方案列的列字母：

- 光伏装机容量 `solar_kw`
  - 采用“每方案独立的上下限”进行钳制：
  - A：`MAX(MIN(roof_max_panels*panel_power_kw*plan_a_capacity_factor, plan_a_max_kw), plan_a_min_kw)`
  - B：`MAX(MIN(roof_max_panels*panel_power_kw*plan_b_capacity_factor, plan_b_max_kw), plan_b_min_kw)`
  - C：`MAX(MIN(roof_max_panels*panel_power_kw*plan_c_capacity_factor, plan_c_max_kw), plan_c_min_kw)`
  - D：`MAX(MIN(roof_max_panels*panel_power_kw*plan_d_capacity_factor, plan_d_max_kw), plan_d_min_kw)`
- 面板数量 `panel_count`
  - `INT(col[row_solar] / panel_power_kw)`（向下取整）
- 逆变器容量 `inverter_kw`
  - `CEILING(solar_kw / dc_ac_ratio, 0.1)`（向上取整至 0.1 kW）
- 年发电量 `annual_generation_kwh`
  - `solar_kw * yield_per_kw_per_year`（若后续接入 pvlib，可替换为更精细模型）
- 每日需转移能量 `daily_energy_to_shift_kwh`
  - `(annual_generation_kwh / 365) * (target_sc_rate - baseline_self_consumption_rate)`
  - 其中 `target_sc_rate` 随方案 A/B/C/D 变化
- 电池标称 `battery_nominal_kwh`
  - `IF(daily_energy_to_shift>0, CEILING(daily_energy_to_shift / (battery_dod*battery_rte), 1), 0)`（向上取整到 1 kWh）
- 商用品规建议 `battery_pack_suggested_kwh`
  - 分段选择：`{20, 13.5, 10, 6.5, 5}` 中就近上限
- 成本：
  - panels：`panel_count * panel_unit_cost`
  - inverter：`inverter_kw * inverter_unit_cost_per_kw`
  - battery：`battery_nominal_kwh * battery_unit_cost_per_kwh`
  - install：`install_base_cost + (solar_kw * install_cost_per_kw)`
- 总成本 `total_cost`
  - `cost_panels + cost_inverter + cost_battery + cost_install`
- 报价基准 `price_base`
  - `total_cost * (1 + profit_margin_rate)`

### 3.3 回本期估算（年）

目标：`price / 年度收益`。收益由自用与馈网构成（受目标自用率与家庭年用电上限约束）。

- 基线 `payback_base_years`
  - `IFERROR( price_base / ( MIN(annual_gen*target, annual_home_usage_proxy_med)*grid_buy_rate + (annual_gen - MIN(...))*grid_sell_rate ), "Inf" )`
- 保守 `payback_low_years`
  - 成本偏高 10%，发电量与目标自用成分打 85%，购电价打 0.8：
  - `IFERROR( (total_cost*1.1*(1+pm)) / ( MIN(annual_gen*0.85*target, med)*buy*0.8 + (annual_gen*0.85 - MIN(...))*sell ), "Inf" )`
- 乐观 `payback_high_years`
  - 成本偏低 10%，发电量与目标自用成分打 115%，购电价提到 1.2：
  - `IFERROR( (total_cost*0.9*(1+pm)) / ( MIN(annual_gen*1.15*target, med)*buy*1.2 + (annual_gen*1.15 - MIN(...))*sell ), "Inf" )`

表尾备注：强调 `INT/CEILING` 取整、商用品规建议的存在。

---

## 4. 简化版：`Plans_Simplified`

### 4.1 字段列表

- solar_kw / panel_count / annual_generation_kwh
- total_hardware_cost（硬件包价）
- cost_battery（默认 0，可按需自行改写）
- cost_install / total_cost / price_base
- payback_base_years / payback_low_years / payback_high_years

### 4.2 关键公式

- `solar_kw` 与 `panel_count / annual_generation_kwh` 与详细版一致（无逆变器与电池标称字段）。
- 硬件成本 `total_hardware_cost`：`solar_kw * hardware_cost_per_kw`
- 电池成本 `cost_battery`：默认 `0`（如需带电池可基于电池标称逻辑扩展）
- 安装成本 `cost_install`：`install_base_cost + solar_kw * install_cost_per_kw`
- 总成本/报价与回本期估算：与详细版相同结构。

---

## 5. 电池改造（Battery_Retrofit）

两版本均包含 `Battery_Retrofit` 表，列为 A/B/C/D 四个容量档位（默认 5/10/13.5/20 kWh，可在 `Inputs` 修改）。

字段：
- battery_nominal_kwh：电池标称容量（来自 Inputs 的四个建议值）
- usable_battery_capacity_kwh：可用容量 = 名义容量 * DoD
- annual_shifted_kwh_est：理论可转移量（按 `battery_effective_usage_factor` 与全年 365 天估算）
  - `usable * battery_effective_usage_factor * 365`
- max_shiftable_kwh：可最大转移上限（由剩余可自用潜力决定）
  - 若 `existing_solar_annual_gen_kwh` 留空：`(roof_max_panels*panel_power_kw*0.7*1200)*(1-existing_sc_rate)` 作为估算剩余馈网量
  - 否则：`existing * (1-existing_sc_rate)`
- final_annual_shifted_kwh：`MIN(annual_shifted_kwh_est, max_shiftable_kwh)`
- annual_savings：`final_annual_shifted_kwh * (grid_buy_rate - grid_sell_rate)`
- total_cost：`battery_kwh * battery_unit_cost_per_kwh + battery_install_base_cost + battery_kwh * battery_install_cost_per_kwh`
- price_base：`total_cost * (1 + profit_margin_rate)`
- payback_years：`IF(annual_savings>0, price_base/annual_savings, "Inf")`
- new_self_consumption_rate：
  - 若无现有发电量输入：`((estimated_gen*existing_sc_rate + final_shift)/estimated_gen)`
  - 否则：`((existing*existing_sc_rate + final_shift)/existing)`
- roi_warning：若 `final_annual_shifted_kwh < 500`，提示 "Low ROI - small export available"，否则 "OK"

---

## 6. 外观与可读性

两个版本都会：
- 对标题行加粗
- 自动计算每列宽度（遍历列内容长度，`width = max_len + 2`）

---

## 7. 使用与扩展建议

- 运行：
  - 直接调用：`create_detailed_file(path)` / `create_simplified_file(path)`
  - 示例中默认保存到 `/mnt/data/` 下。建议结合项目结构改为相对路径或可配置路径。
- 自发电量模型：
  - 当前以 `yield_per_kw_per_year` 为兜底常量，可与 `pvlib` 或本地辐照度时序数据对接升级。
- 电池容量建议：
  - 目前根据目标提升自用率的差额推导，需要注意实际家庭负荷曲线与发电曲线的错配可能性。
- 回本期估算：
  - 使用了代理年用电量 `annual_home_usage_proxy_med` 做上限截断，若有真实用电数据，可替换或增加多场景计算。
- 错误处理：
  - Excel 中使用 `IFERROR` 与字符串 "Inf" 表示不可计算或收益为零的情况。

---

## 8. 与详细版/简化版的取舍

- 详细版：适合需要拆分材料项与逆变器、电池容量建议与取整逻辑透明化的场景。
- 简化版：适合快速报价，只需按装机 kW 乘以硬件包价，减少参数输入与沟通成本。

---

## 9. 文件清单

- 详细版输出示例：`solar_estimate_recommended.xlsx`
- 简化版输出示例：`solar_estimate_simplified_hardware_cost.xlsx`

---

## 10. 维护建议

- 将输入参数抽象为配置文件（JSON/YAML）或数据库来源，便于多项目复用。
- 提供 CLI 或 Web 表单收集输入并触发生成，提高可用性。
- 引入单元测试：针对关键公式与边界值（如 0/空值/极大极小值）进行校验。

---

## 11. 已知边界与注意事项（自用率目标 < 基线）

当某方案的目标自用率 `target_sc_rate` 低于基线自用率 `baseline_self_consumption_rate` 时：

- 根据 3.2 的公式：`daily_energy_to_shift_kwh = (annual_generation_kwh / 365) * (target_sc_rate - baseline_sc)`，将产生负值。
- 当前实现对电池容量的推导为：`IF(daily_energy_to_shift>0, CEILING(...), 0)`，因此在该场景下：
  - `battery_nominal_kwh = 0`（不建议配置电池，符合“需要减少自用/增加馈网”的逻辑）。
  - `cost_battery = 0`。
- 该负值仅表示“自用率目标较基线更低”的意向，对电池 sizing 不会产生正向容量；但在对外展示或进一步衍生计算中，若默认假设“需转移能量应为非负”，可能引起歧义。

产品建议：

- 前端文案或导出摘要中，对 `daily_energy_to_shift_kwh` 可：
  - 保留原始值用于诊断；
  - 或显示为 `max(daily_energy_to_shift_kwh, 0)` 以避免负值引发误读（不改变公式，仅在展示处约束）。
- 对 H5 卡片而言，若仅依赖“是否需要电池”与“电池容量”，上述实现已经确保 `battery_nominal_kwh = 0`，不会误导配置。
- 如需在节省/回本计算中引入该差值，请确保公式能正确处理负向“转移”含义，或加入边界保护。

验证记录：

- 示例：Plan A 在默认基线 `baseline_sc = 0.30` 下，将 `plan_a_target_sc_rate` 设为 `0.27`：
  - `annual_generation_kwh = 5110`，则 `daily_energy_to_shift_kwh = 5110/365 * (0.27 - 0.30) ≈ -0.42 kWh/天`；
  - `battery_nominal_kwh = 0`，`cost_battery = 0`；
  - 预算与回本期计算仍可进行，但请注意解释口径与展示。
