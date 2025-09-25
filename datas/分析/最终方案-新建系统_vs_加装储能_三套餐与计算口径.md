# 最终方案：新建系统 vs 加装储能（双类型三套餐与计算口径）

本文件汇总 Residential（On-Grid，新建/加装）场景的标准化套餐与计算方法，结合《计算规则 v2.0》与《计算规则 v2.1 草案》的参数化增补（STC、电池补贴、州别电价、门槛吸附）。

原则：
- 铺满屋顶优先：在不超过屋顶潜力与并网规范前提下，优先更高的 DC 容量（Residential 建议 10–15kW，dc/ac ≈ 1.2–1.33）。
- 电池“合理更大”：以补贴容量门槛为锚点（10/13.5/20kWh），在目标自用率与回本期可接受范围内向上吸附到下一档。

引用：
- 规则与参数：`提案-0914/docs/计算规则_v2.0.md`、`datas/分析/计算规则_v2.1_草案.md`、`datas/分析/参数清单.md`
- 数据产出：
  - 新建系统套餐（州别）：`datas/分析/output/residential_packages_by_state.csv`
  - 电池加装套餐（州别）：`datas/分析/output/battery_only_packages_by_state.csv`
  - 概览摘要：`datas/分析/output/residential_pricing_summary.md`、`datas/分析/output/battery_only_pricing_summary.md`

---

## 一、类型A：新建系统（PV+Battery）

标准三套餐（可按州替换品牌与 AC 并网机型）：
- A 入门：PV DC 10.0 kW，逆变器 AC 8 kW（dc/ac≈1.25），Battery 9.6 kWh
- B 均衡：PV DC 13.2 kW，逆变器 AC 10 kW（dc/ac≈1.32），Battery 13.5 kWh
- C 高配：PV DC 15.0 kW，逆变器 AC 12 kW（dc/ac≈1.25），Battery 20.0 kWh
- D 铺满屋顶（可选）：按州“满屋顶”P90（大屋顶样本）估算 DC（上限 15kW），AC 由目标 dc/ac 反推，电池按目标自用率→“门槛吸附”选档

计算口径（v2.1 增补）：
- 成本与毛价（在 v2.0 基础上）：
  - `cost_panels = pv_dc_kw × panel_per_kw_cost_dc × roof_coef`
  - `cost_inverter = pv_ac_kw × inverter_unit_cost_per_kw`
  - `cost_battery = battery_kwh × battery_unit_cost_per_kwh_new`
  - `cost_install = install_base_cost + pv_dc_kw × install_cost_per_kw`（× `roof_coef`）
  - `price_base = (cost_panels + cost_inverter + cost_battery + cost_install) × (1 + profit_margin_rate)`
- 补贴抵扣：
  - `stc_value = stc_count × stc_price_t`（无 stc_count 时，用 `pv_dc_kw × STC_per_kW` 兜底）
  - `battery_rebate_value = rebate(state, install_month, battery_kwh)`（固定/按kWh/上限）
  - `price_net = price_base - stc_value - battery_rebate_value`
- 经济性：
  - `annual_generation_kwh = pv_dc_kw × yield_per_kw_per_year[state]`
  - `annual_savings = annual_self×buy_rate + annual_export×sell_rate`，其中 `annual_self = gen×target_sc`；有电池默认 `target_sc≈0.7`
  - `payback_years_net = price_net / annual_savings`

数据与示例：
- 州别套餐结果见 `residential_packages_by_state.csv`；摘要见 `residential_pricing_summary.md`
- 经验参数下（示例）：SA-B 套餐净价≈27.3k，年节省≈5.3k，回本≈5.1 年；NSW-B 回本≈6.1 年（详见摘要文件）

---

## 二、类型B：已有光伏系统加装储能（Battery-only）

标准三套餐（AC 耦合通用优先；确认品牌白名单与并网要求）：
- A' 入门：Battery 9.6 kWh
- B' 均衡：Battery 13.5 kWh
- C' 高配：Battery 20.0 kWh

计算口径（电池加装 v2.1 扩展）：
- 成本与毛价：
  - `cost_battery = battery_kwh × battery_unit_cost_per_kwh_new`
  - `install_batt_only = battery_only_install_base_cost + battery_kwh × battery_only_install_per_kwh`
  - `price_base = (cost_battery + install_batt_only) × (1 + profit_margin_rate_battery_only)`
- 补贴：`battery_rebate_value = rebate(state, month, battery_kwh)` → `price_net = price_base - rebate`
- 经济性提升（节省增量，假设自用率从 0.3 → 0.7）：
  - `annual_generation_kwh = pv_dc_median[state] × yield_per_kw_per_year[state]`
  - `annual_savings_uplift = (gen×0.7×buy + gen×0.3×sell) - (gen×0.3×buy + gen×0.7×sell)`
  - `payback_years_net = price_net / annual_savings_uplift`

数据与示例：
- 州别套餐结果见 `battery_only_packages_by_state.csv`；摘要见 `battery_only_pricing_summary.md`
- 经验参数下（示例）：NSW A' 套餐净价≈12.2k，年节省增量≈1.24k，回本≈9.8 年；NT A' 回本≈4.8 年（高年发电量假设）

---

## 三、品牌与兼容性建议
- 面板：Jinko、LONGi、JA、Risen、REC（结合当地供应链）
- 逆变器：GoodWe、Sungrow、Fronius、Huawei、SolarEdge（州别与并网约束）
- 电池：Tesla Powerwall、Sungrow SBR、Alpha ESS、BYD（容量档标准化）
- 同生态优先（如 Sungrow 逆变器 × SBR 电池），AC 耦合（Tesla）具通用性；以厂家白名单为准。

---

## 四、落地与再计算
- 更新参数（`datas/分析/参数清单.md`）：STC 价格、州/联邦电池补贴、电价/上网电价、年发电量与成本系数
- 重新生成：
  - 新建系统：`python3 datas/分析/run_pricing_residential.py`
  - 电池加装：`python3 datas/分析/run_pricing_battery_only.py`
- 报价展示建议：固定展示“毛价 → STC → 电池补贴 → 净价 → 年节省（或节省增量） → 回本（净）”，并标注参数来源与有效期。

---

## 五、附：铺满屋顶与更大电池的“合理边界”
- 满屋顶 DC：按州“住宅大屋顶”样本的 P90 估算（上限 15kW；不低于 13.2kW），满足并网容量与屋顶强度约束
- 电池吸附：依据目标自用率推导名义容量后，向上吸附至 10/13.5/20/22.4/25.6kWh 档位；通常建议上限至 25.6kWh（住宅场景）
- 风险提示：当卖电价显著低于买电价时，提升电池容量更有利；若上网电价较高或自用潜力有限，需避免过度配置延长回本期
