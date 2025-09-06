# 开发计划（Streamlit 界面化报价系统）

本计划用于指导在 `proposal/` 目录下新建一个基于 Streamlit 的界面化应用，实现参数可配置、"新建系统"与"储能扩容"两大场景的多方案对比与导出功能。注意：不修改现有 `proposal/proposal.py`，而是新建独立脚本与模块。

---

## 1. 目标与范围

- 新建 `app.py`（Streamlit 主入口），提供交互界面：
  - 侧边栏管理参数（与 `Inputs` 表对应）。
  - Tab 切换：
    - 新建系统（含 详细版/简化版 对比视图）
    - 储能扩容（Battery Retrofit）
  - 展示：方案 A/B/C/D 的成本、报价、回本期等表格与图表。
  - 导出：一键生成 Excel（输出到 `proposal/outputs/`）。
- 抽取计算引擎：将 `proposal/proposal.py` 的 Excel 公式逻辑复刻为 Python 计算，便于实时可视化与测试。
- 配置管理：导入/导出 JSON 配置；支持“恢复默认”。

---

## 2. 目录与文件规划

- `proposal/`
  - `proposal.py`（保留现状）
  - `app.py`（新建，Streamlit 主入口）
  - `calc_engine.py`（新建，复刻 Plans 与 Battery Retrofit 的核心公式）
  - `schemas.py`（新建，Pydantic 数据模型与校验）
  - `outputs/`（新建目录，存放导出的 Excel/CSV/图表）
  - `docs/`
    - `proposal_logic.md`（已存在）
    - `dev_plan.md`（本文件）
  - `configs/`（可选：预置 JSON 配置样例）

---

## 3. 依赖与运行方式

- 依赖（初版）：
  - streamlit（Web 界面）
  - pydantic（参数模型与校验）
  - pandas（表格数据与导出辅助）
  - openpyxl（已用于 Excel 生成）
  - numpy（取整与数值辅助，可选）
- 运行：
  - 在项目根目录或 `proposal/` 目录执行：
    ```bash
    streamlit run proposal/app.py
    ```
- 导出路径：
  - Excel 默认导出到 `proposal/outputs/`，若不存在则自动创建。

---

## 4. 数据模型（schemas.py）

- 定义 `InputsConfig`：完整映射 `Inputs` 表字段，包含默认值与范围校验：
  - 屋顶/面板：`roof_max_panels`, `panel_power_kw`, `panel_area_m2`, `dc_ac_ratio` 等。
  - 成本：`panel_unit_cost`, `inverter_unit_cost_per_kw`, `hardware_cost_per_kw`, `battery_unit_cost_per_kwh`, `install_base_cost`, `install_cost_per_kw` 等。
  - 发电与策略：`yield_per_kw_per_year`, `baseline_self_consumption_rate`, `plan_*_capacity_factor`, `plan_*_target_sc_rate`, `plan_a_min_kw`, `plan_c_max_kw`。
  - 电价：`grid_buy_rate`, `grid_sell_rate`。
  - 家庭年用电代理：`annual_home_usage_proxy_med`（简化版核心；详细版可扩展 low/high）。
  - 既有系统：`existing_solar_annual_gen_kwh`（可空）, `existing_sc_rate`。
  - Retrofit 容量：`retrofit_plan_a_kwh` ~ `retrofit_plan_d_kwh`。
- 提供：
  - `default()` 工厂方法，返回与 Excel 一致的默认参数。
  - `load_json(path)`/`dump_json(path)` 读写。

---

## 5. 计算引擎（calc_engine.py）

- 入口函数：
  - `compute_plans_detailed(cfg: InputsConfig) -> pd.DataFrame`
  - `compute_plans_simplified(cfg: InputsConfig) -> pd.DataFrame`
  - `compute_battery_retrofit(cfg: InputsConfig) -> pd.DataFrame`
- 关键实现（与 Excel 逻辑保持一致）：
  - 新建系统 Plans：
    - `solar_kw`：A/B/C/D 按容量系数/上下限（A 含下限约束），`MAX/MIN` 规则。
    - `panel_count = INT(solar_kw / panel_power_kw)`（向下取整）。
    - 详细版：`inverter_kw = CEILING(solar_kw / dc_ac_ratio, 0.1)`。
    - `annual_generation_kwh = solar_kw * yield_per_kw_per_year`。
    - `daily_energy_to_shift_kwh` 与 `battery_nominal_kwh`（DoD & RTE，向上取整到 1）。
    - 成本：面板/逆变器/电池/安装，`total_cost` 与 `price_base`。
    - 回本期（基线/保守/乐观）：收益=自用节省+馈网收益，使用 `MIN` 与 `IFERROR` 思路（Python 中显式处理 0/负数）。
  - 储能扩容 Retrofit：
    - `usable = nominal * DoD`，`annual_shifted_est = usable * effective_usage_factor * 365`。
    - `max_shiftable`：按 `existing_solar_annual_gen_kwh` 是否为空走两套估算；
    - `final_shifted = min(est, max)`；
    - `annual_savings = final * (buy - sell)`；
    - `total_cost`、`price_base`、`payback_years`、`new_self_consumption_rate` 与 ROI 提示。
- 工具函数：
  - `ceil_to(x, step)`、`int_floor(x)`、`safe_payback(price, annual_benefit)` 等。

---

## 6. 界面设计（app.py）

- 侧边栏（Sidebar）：
  - 参数表单分组：
    - 基础参数（面板/屋顶/容配比/发电兜底）
    - 成本参数（面板/逆变器/电池/安装/利润率/电价）
    - 策略参数（容量系数、自用率目标、装机上下限）
    - 既有系统（发电量可空、自用率）
    - Retrofit 容量建议（A/B/C/D）
  - 操作区：导入配置（JSON）、导出配置（JSON）、恢复默认、应用参数按钮。
- 主区 Tabs：
  - `新建系统`：包含“详细版/简化版 对比视图”
    - 表格：并排展示 A/B/C/D 关键指标（`solar_kw`, `panel_count`, `inverter_kw(详细)`, `annual_gen`, `total_cost`, `price_base`, `payback_*`）。
    - 图表：
      - 柱状：`price_base` 对比
      - 折线/柱状：`payback_base_years` 对比
    - 导出：按钮“导出 Detailed Excel”、“导出 Simplified Excel”（写入 `proposal/outputs/`）。
  - `储能扩容（Battery Retrofit）`：
    - 表格：A/B/C/D 的 `annual_savings`, `price_base`, `payback_years`, `new_self_consumption_rate`, `roi_warning`。
    - 图表：`payback_years` 柱状；`annual_savings` 柱状。
- 交互：
  - 点击“应用参数”后重新计算；
  - 对异常/无效输入给出提示（例如收益为 0 导致回本期为 Inf）。

---

## 7. 导出与集成

- Excel 导出：
  - 直接调用 `proposal/proposal.py` 里的 `create_detailed_file()` 与 `create_simplified_file()`。
  - 输出到 `proposal/outputs/` 下：
    - `solar_estimate_recommended.xlsx`
    - `solar_estimate_simplified_hardware_cost.xlsx`
- 数据导出（增强项）：
  - 将计算结果导出 CSV 与图表 PNG。
  - 后续可引入 `reportlab` 或 `weasyprint` 生成 PDF 报告。

---

## 8. 测试与验收

- 单元测试：
  - 针对 `calc_engine.py` 的关键函数，准备与 Excel 一致的输入输出样例。
  - 覆盖边界：0/空值/极端容量与价格。
- 手工测试：
  - 比较页面结果与 Excel 输出的一致性（允许存在取整差异但需在可解释范围）。

---

## 9. 里程碑与时间规划（T0 为确认本计划的当天）

- M1（T0 + 0.5 天）：`schemas.py` 与 `calc_engine.py` 初版，确保与 Excel 公式对齐。
- M2（T0 + 1 天）：`app.py` 基本交互完成（参数表单 + 新建系统对比 + 基础图表）。
- M3（T0 + 1.5 天）：储能扩容页完成；导入/导出 JSON。
- M4（T0 + 2 天）：Excel 导出打通（至 `proposal/outputs/`）；回归测试与文档补全。
- M5（可选 +0.5 天）：报告导出增强（CSV/PNG，评估 PDF）。

---

## 10. 风险与应对

- 公式对齐风险：严格比照 `proposal_logic.md` 与 Excel 公式，增加单元测试；
- 输入异常：引入 Pydantic 校验并在 UI 中做范围提示；
- 取整差异：明确 `INT/CEILING` 行为并在文档/界面中提示；
- 依赖环境：补充 `requirements.txt` 并在 README 说明运行方式。

---

## 11. 计算逻辑展示与格式化修复（新增）

- 新增页签：在 `app.py` 中增加第三个 Tab —— `计算逻辑（文档）`，直接渲染 `proposal/docs/proposal_logic.md`，用于在界面端展示与 Excel 一致的计算逻辑说明，便于对照核验。
- 表格格式化修复：
  - 由于部分单元格为字符串（例如 ROI 提示、“Inf”等），统一套用数值格式化 `"{:.2f}"` 会触发 `ValueError: Unknown format code 'f' for object of type 'str'`。
  - 处理：使用安全格式化函数，仅对数值且非 `inf` 的单元格进行 `"{:.2f}"` 格式化；其余保留原样。
  - 位置：`app.py` 中对详细版/简化版/Retrofit 三处 DataFrame 展示均已改为 `lambda` 判定后格式化。

### 11.1 悬停说明方案调整

- 原方案：使用 `Styler.set_tooltips()` 在首列添加悬停提示，但会在某些数值单元格中插入 `<span>` 导致显示异常（例如 `3.50<span class="pd-t"></span>`）。
- 新方案：去除悬停 tooltip，改为在表格最左侧新增一列“说明”，逐行给出公式/口径说明，避免污染数值展示。
