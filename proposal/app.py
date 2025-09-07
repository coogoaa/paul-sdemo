import os
from pathlib import Path

import streamlit as st
import pandas as pd
import math
from types import SimpleNamespace

# 导出摘要 JSON（供 H5 使用）
try:
    from export_summary import export_summary_json
except Exception:
    export_summary_json = None

try:
    from schemas import InputsConfig
except ModuleNotFoundError:
    InputsConfig = None  # 兜底

try:
    from calc_engine import (
        compute_plans_detailed,
        compute_plans_simplified,
        compute_battery_retrofit,
    )
except ModuleNotFoundError:
    compute_plans_detailed = compute_plans_simplified = compute_battery_retrofit = None

APP_TITLE = "光伏与储能报价演示（Streamlit）"
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _load_excel_creators():
    """安全载入 proposal/proposal.py 中的 create_* 函数而不执行底部示例代码。"""
    src_path = Path(__file__).resolve().parent / "proposal.py"
    code = src_path.read_text(encoding="utf-8")
    # 仅执行函数定义部分：截断到示例调用之前（以 'file1 =' 标志作为分割）
    split_marker = "\nfile1 = "
    if split_marker in code:
        code = code.split(split_marker)[0]
    # 执行到本地命名空间
    ns: Dict[str, object] = {}
    exec(code, ns, ns)
    if "create_detailed_file" not in ns or "create_simplified_file" not in ns:
        raise RuntimeError("未在 proposal/proposal.py 中找到导出函数。")
    return SimpleNamespace(
        create_detailed_file=ns["create_detailed_file"],
        create_simplified_file=ns["create_simplified_file"],
    )


def export_excels():
    """调用现有 Excel 生成函数，导出到 proposal/outputs/ 目录。"""
    detailed_path = OUTPUT_DIR / "solar_estimate_recommended.xlsx"
    simplified_path = OUTPUT_DIR / "solar_estimate_simplified_hardware_cost.xlsx"
    try:
        creators = _load_excel_creators()
        creators.create_detailed_file(str(detailed_path))
        creators.create_simplified_file(str(simplified_path))
        st.success(f"已导出 Excel 至: {OUTPUT_DIR}")
        st.write("- 详细版:", detailed_path)
        st.write("- 简化版:", simplified_path)
    except Exception as e:
        st.error(f"导出失败: {e}")


def sidebar_params():
    st.header("参数配置")
    st.caption("为简化初版 UI，仅暴露最关键参数。完整参数稍后补齐。")
    if InputsConfig is None:
        st.warning("未找到参数模型模块（schemas.py）")
        return None
    cfg = InputsConfig.default()

    with st.expander("基础（面板/发电）", expanded=True):
        cfg.roof_max_panels = st.number_input("屋顶最大面板数 (块)", min_value=0, value=cfg.roof_max_panels)
        cfg.panel_power_kw = st.number_input("单块面板功率 (kW)", min_value=0.01, value=float(cfg.panel_power_kw), step=0.01)
        cfg.yield_per_kw_per_year = st.number_input("每kW年发电量(兜底)", min_value=1.0, value=float(cfg.yield_per_kw_per_year), step=10.0)
        cfg.dc_ac_ratio = st.number_input("容配比 (DC/AC)", min_value=0.1, value=float(cfg.dc_ac_ratio), step=0.01)
        # 额外信息（当前计算未直接使用，但保留可配置）
        cfg.roof_total_area_m2 = st.number_input("屋顶总面积 (m²)", min_value=0.0, value=float(cfg.roof_total_area_m2), step=1.0)
        cfg.roof_effective_area_m2 = st.number_input("屋顶有效面积 (m²)", min_value=0.0, value=float(cfg.roof_effective_area_m2), step=1.0)
        cfg.panel_area_m2 = st.number_input("单块面板面积 (m²)", min_value=0.0, value=float(cfg.panel_area_m2), step=0.01)

    with st.expander("策略（容量系数/自用率/上下限）", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            cfg.plan_a_capacity_factor = st.number_input("A 容量系数", min_value=0.0, value=float(cfg.plan_a_capacity_factor), step=0.05)
            cfg.plan_b_capacity_factor = st.number_input("B 容量系数", min_value=0.0, value=float(cfg.plan_b_capacity_factor), step=0.05)
        with col2:
            cfg.plan_c_capacity_factor = st.number_input("C 容量系数", min_value=0.0, value=float(cfg.plan_c_capacity_factor), step=0.05)
            cfg.plan_d_capacity_factor = st.number_input("D 容量系数", min_value=0.0, value=float(cfg.plan_d_capacity_factor), step=0.05)
        col3, col4 = st.columns(2)
        with col3:
            cfg.plan_a_target_sc_rate = st.number_input("A 目标自用率", min_value=0.0, max_value=1.0, value=float(cfg.plan_a_target_sc_rate), step=0.01)
            cfg.plan_b_target_sc_rate = st.number_input("B 目标自用率", min_value=0.0, max_value=1.0, value=float(cfg.plan_b_target_sc_rate), step=0.01)
        with col4:
            cfg.plan_c_target_sc_rate = st.number_input("C 目标自用率", min_value=0.0, max_value=1.0, value=float(cfg.plan_c_target_sc_rate), step=0.01)
            cfg.plan_d_target_sc_rate = st.number_input("D 目标自用率", min_value=0.0, max_value=1.0, value=float(cfg.plan_d_target_sc_rate), step=0.01)
        st.markdown("**每方案装机上下限 (kW)**")
        ca, cb = st.columns(2)
        with ca:
            cfg.plan_a_min_kw = st.number_input("A 最小", min_value=0.0, value=float(cfg.plan_a_min_kw), step=0.1)
            cfg.plan_b_min_kw = st.number_input("B 最小", min_value=0.0, value=float(cfg.plan_b_min_kw), step=0.1)
            cfg.plan_c_min_kw = st.number_input("C 最小", min_value=0.0, value=float(cfg.plan_c_min_kw), step=0.1)
            cfg.plan_d_min_kw = st.number_input("D 最小", min_value=0.0, value=float(cfg.plan_d_min_kw), step=0.1)
        with cb:
            cfg.plan_a_max_kw = st.number_input("A 最大", min_value=0.0, value=float(cfg.plan_a_max_kw), step=0.1)
            cfg.plan_b_max_kw = st.number_input("B 最大", min_value=0.0, value=float(cfg.plan_b_max_kw), step=0.1)
            cfg.plan_c_max_kw = st.number_input("C 最大", min_value=0.0, value=float(cfg.plan_c_max_kw), step=0.1)
            cfg.plan_d_max_kw = st.number_input("D 最大", min_value=0.0, value=float(cfg.plan_d_max_kw), step=0.1)
        cfg.baseline_self_consumption_rate = st.number_input("基线自用率", min_value=0.0, max_value=1.0, value=float(cfg.baseline_self_consumption_rate), step=0.01)

    with st.expander("成本/电价", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            cfg.panel_unit_cost = st.number_input("面板成本 (AUD/块)", min_value=0.0, value=float(cfg.panel_unit_cost), step=10.0)
            cfg.inverter_unit_cost_per_kw = st.number_input("逆变器成本 (AUD/kW)", min_value=0.0, value=float(cfg.inverter_unit_cost_per_kw), step=10.0)
            cfg.hardware_cost_per_kw = st.number_input("硬件包价 (AUD/kW)", min_value=0.0, value=float(cfg.hardware_cost_per_kw), step=10.0)
        with col2:
            cfg.install_base_cost = st.number_input("安装基础费 (AUD)", min_value=0.0, value=float(cfg.install_base_cost), step=10.0)
            cfg.install_cost_per_kw = st.number_input("安装每kW (AUD/kW)", min_value=0.0, value=float(cfg.install_cost_per_kw), step=10.0)
            cfg.profit_margin_rate = st.number_input("利润率", min_value=0.0, value=float(cfg.profit_margin_rate), step=0.01)
        cfg.price_range_percent = st.number_input("报价浮动范围（占位）", min_value=0.0, value=float(cfg.price_range_percent), step=0.01)
        cfg.grid_buy_rate = st.number_input("购电价 (AUD/kWh)", min_value=0.0, value=float(cfg.grid_buy_rate), step=0.01)
        cfg.grid_sell_rate = st.number_input("馈网价 (AUD/kWh)", min_value=0.0, value=float(cfg.grid_sell_rate), step=0.01)
        st.markdown("**家庭年用电代理 (kWh/年)**")
        ua, ub, uc = st.columns(3)
        cfg.annual_home_usage_proxy_low = ua.number_input("Low", min_value=0.0, value=float(cfg.annual_home_usage_proxy_low), step=100.0)
        cfg.annual_home_usage_proxy_med = ub.number_input("Med", min_value=0.0, value=float(cfg.annual_home_usage_proxy_med), step=100.0)
        cfg.annual_home_usage_proxy_high = uc.number_input("High", min_value=0.0, value=float(cfg.annual_home_usage_proxy_high), step=100.0)

    with st.expander("策略开关", expanded=True):
        cfg.use_plan_limits = st.checkbox("启用每方案装机上下限 (use_plan_limits)", value=bool(getattr(cfg, "use_plan_limits", False)))
        cfg.usage_cap_policy = st.selectbox(
            "回本自用上限策略 (usage_cap_policy)",
            options=["med", "per_plan"],
            index=0 if getattr(cfg, "usage_cap_policy", "med") == "med" else 1,
            help="med: 统一使用 annual_home_usage_proxy_med；per_plan: A→low, B→med, C/D→high"
        )

    with st.expander("政策/补贴（STC / 电池补贴）", expanded=True):
        st.subheader("STC 粗略估算（新建系统）")
        cfg.stc_enable = st.checkbox("启用 STC 粗略抵扣", value=bool(getattr(cfg, "stc_enable", True)))
        c1, c2, c3 = st.columns(3)
        cfg.stc_zone_rating = c1.number_input("STC 区域系数 (zone)", min_value=0.0, value=float(getattr(cfg, "stc_zone_rating", 1.185)), step=0.001, format="%.3f")
        cfg.stc_price_aud = c2.number_input("STC 价格 (AUD/张)", min_value=0.0, value=float(getattr(cfg, "stc_price_aud", 35.0)), step=1.0)
        cfg.stc_years_to_2030 = c3.number_input("Deeming 剩余年数", min_value=0, value=int(getattr(cfg, "stc_years_to_2030", 6)), step=1)
        st.caption("说明：示意值，实际以安装商报价与政策为准；SRES 将于 2030 结束，deeming 每年递减。")

        st.subheader("电池补贴（Retrofit & 新建中的电池部分）")
        d1, d2, d3 = st.columns(3)
        cfg.rebate_fixed_aud = d1.number_input("固定补贴 (AUD)", min_value=0.0, value=float(getattr(cfg, "rebate_fixed_aud", 0.0)), step=50.0)
        cfg.rebate_per_kwh_aud = d2.number_input("每 kWh 补贴 (AUD/kWh)", min_value=0.0, value=float(getattr(cfg, "rebate_per_kwh_aud", 0.0)), step=10.0)
        cfg.rebate_cap_aud = d3.number_input("总补贴上限 (0 不限)", min_value=0.0, value=float(getattr(cfg, "rebate_cap_aud", 0.0)), step=50.0)
        cfg.rebate_stack_mode = st.selectbox("叠加策略", options=["stack", "max"], index=0 if getattr(cfg, "rebate_stack_mode", "stack") == "stack" else 1, help="stack: 固定+每kWh 叠加；max: 两者取其大")

    with st.expander("电池/Retrofit", expanded=False):
        cfg.battery_dod = st.number_input("电池 DoD", min_value=0.0, max_value=1.0, value=float(cfg.battery_dod), step=0.01)
        cfg.battery_rte = st.number_input("电池 RTE", min_value=0.0, max_value=1.0, value=float(cfg.battery_rte), step=0.01)
        cfg.battery_unit_cost_per_kwh = st.number_input("电池成本 (AUD/kWh)", min_value=0.0, value=float(cfg.battery_unit_cost_per_kwh), step=10.0)
        cfg.battery_install_base_cost = st.number_input("电池安装基础费 (AUD)", min_value=0.0, value=float(cfg.battery_install_base_cost), step=10.0)
        cfg.battery_install_cost_per_kwh = st.number_input("电池安装每kWh (AUD/kWh)", min_value=0.0, value=float(cfg.battery_install_cost_per_kwh), step=10.0)
        cfg.battery_effective_usage_factor = st.number_input("电池有效使用系数", min_value=0.0, max_value=1.0, value=float(cfg.battery_effective_usage_factor), step=0.01)
        st.markdown("**Retrofit 容量建议 (kWh)**")
        c1, c2, c3, c4 = st.columns(4)
        cfg.retrofit_plan_a_kwh = c1.number_input("A", min_value=0.0, value=float(cfg.retrofit_plan_a_kwh), step=0.5)
        cfg.retrofit_plan_b_kwh = c2.number_input("B", min_value=0.0, value=float(cfg.retrofit_plan_b_kwh), step=0.5)
        cfg.retrofit_plan_c_kwh = c3.number_input("C", min_value=0.0, value=float(cfg.retrofit_plan_c_kwh), step=0.5)
        cfg.retrofit_plan_d_kwh = c4.number_input("D", min_value=0.0, value=float(cfg.retrofit_plan_d_kwh), step=0.5)
        st.markdown("**既有系统（可空）**")
        cfg.existing_solar_annual_gen_kwh = st.number_input("已有光伏估算年发电量 (kWh/年)", min_value=0.0, value=float(cfg.existing_solar_annual_gen_kwh or 0.0), step=100.0)
        cfg.existing_solar_annual_gen_kwh = None if cfg.existing_solar_annual_gen_kwh == 0 else cfg.existing_solar_annual_gen_kwh
        cfg.existing_sc_rate = st.number_input("已有系统基线自用率", min_value=0.0, max_value=1.0, value=float(cfg.existing_sc_rate), step=0.01)

    apply = st.button("应用参数并计算")
    return cfg if apply else None


def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    # 全局样式（标题字号变小，表格更紧凑）
    st.markdown(
        """
        <style>
        h1, h2, .stMarkdown h1, .stMarkdown h2 { margin: 0.2rem 0; }
        /* 主标题、分标题调小字号 */
        .app-title { font-size: 1.4rem; font-weight: 600; }
        .section-title { font-size: 1.05rem; font-weight: 600; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='app-title'>{APP_TITLE}</div>", unsafe_allow_html=True)
    st.caption("详细版/简化版 对比视图 + 储能扩容。支持一键导出 Excel（路径：proposal/outputs/）。")

    def _numeric_format(x):
        return f"{x:.2f}" if isinstance(x, (int, float)) and not math.isinf(x) else x

    def _with_notes_first_col(df: pd.DataFrame, notes_map: dict, col_name: str = "说明") -> pd.DataFrame:
        notes = pd.Series("", index=df.index)
        for idx, tip in notes_map.items():
            if idx in notes.index:
                notes.loc[idx] = tip
        # 将说明列放在最前
        df2 = pd.concat({col_name: notes}, axis=1).join(df)
        return df2

    # 侧边栏：参数与导出
    with st.sidebar:
        cfg = sidebar_params()
        st.divider()
        st.subheader("导出")
        if st.button("一键导出 Excel（详细版与简化版）"):
            export_excels()
        if st.button("导出摘要 JSON（proposal_summary.json）"):
            if cfg is None:
                st.warning("请先设置参数并点击‘应用参数并计算’后再导出 JSON。")
            elif export_summary_json is None:
                st.error("未找到 export_summary 模块或导出函数。")
            else:
                try:
                    out_path = OUTPUT_DIR / "proposal_summary.json"
                    export_summary_json(cfg, out_path)
                    st.success(f"已导出摘要 JSON 至: {out_path}")
                    st.code(str(out_path), language="bash")
                except Exception as e:
                    st.error(f"导出失败: {e}")
        st.caption("导出路径：proposal/outputs/")
        st.divider()
        show_notes = st.checkbox("显示说明列", value=True)

    # 主区：四个 Tab（新增“参数总览”）
    tabs = st.tabs(["新建系统（详细/简化 对比）", "储能扩容（Battery Retrofit）", "参数总览", "计算逻辑（文档）"]) 

    with tabs[0]:
        st.markdown("<div class='section-title'>新建系统 — 详细版/简化版 对比</div>", unsafe_allow_html=True)
        if cfg is None:
            st.info("请在左侧设置参数并点击‘应用参数并计算’。");
        else:
            if compute_plans_detailed is None:
                st.error("计算引擎未找到（calc_engine.py）。")
            else:
                df_detailed = compute_plans_detailed(cfg)
                df_simpl = compute_plans_simplified(cfg)
                # 逐行提示（首列：Plan A）
                detailed_tips = {
                    "solar_kw": "光伏装机容量：按容量系数与上下限 MAX/MIN（A 含最小下限）",
                    "panel_count": "面板数量：INT(solar_kw / panel_power_kw)",
                    "inverter_kw": "逆变器容量：CEILING(solar_kw / dc_ac_ratio, 0.1)",
                    "annual_generation_kwh": "年发电量：solar_kw * yield_per_kw_per_year",
                    "daily_energy_to_shift_kwh": "每日需转移能量：(annual_gen/365) * (target - baseline_sc)",
                    "battery_nominal_kwh": "电池标称：CEILING(daily_shift / (DoD*RTE), 1)",
                    "cost_panels": "面板成本：panel_count * panel_unit_cost",
                    "cost_inverter": "逆变器成本：inverter_kw * inverter_unit_cost_per_kw",
                    "cost_battery": "电池成本：battery_nominal_kwh * battery_unit_cost_per_kwh",
                    "cost_install": "安装成本：install_base_cost + solar_kw * install_cost_per_kw",
                    "total_cost": "项目总成本：面板+逆变器+电池+安装",
                    "price_base": "报价：total_cost * (1 + 利润率)",
                    "payback_base_years": "回本（基线）：自用+馈网收益",
                    "payback_low_years": "回本（保守）：-15%发电，-20%购电价，+10%成本",
                    "payback_high_years": "回本（乐观）：+15%发电，+20%购电价，-10%成本",
                }
                simplified_tips = {
                    "solar_kw": "同详细版容量计算",
                    "panel_count": "INT(solar_kw / panel_power_kw)",
                    "annual_generation_kwh": "solar_kw * yield_per_kw_per_year",
                    "total_hardware_cost": "硬件成本：solar_kw * hardware_cost_per_kw",
                    "cost_battery": "简化版默认 0（可扩展）",
                    "cost_install": "install_base_cost + solar_kw * install_cost_per_kw",
                    "total_cost": "硬件+安装",
                    "price_base": "total_cost * (1 + 利润率)",
                    "payback_base_years": "回本（基线）",
                    "payback_low_years": "回本（保守）",
                    "payback_high_years": "回本（乐观）",
                }
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**详细版**")
                    # 隐藏商用品规建议（battery_pack_suggested_kwh）
                    df_det_disp = df_detailed.drop(index=["battery_pack_suggested_kwh"], errors="ignore")
                    if show_notes:
                        df_show = _with_notes_first_col(df_det_disp, detailed_tips, col_name="说明")
                        st.dataframe(df_show.style.format(_numeric_format), use_container_width=True, height=620)
                    else:
                        st.dataframe(df_det_disp.style.format(_numeric_format), use_container_width=True, height=620)
                with col2:
                    st.markdown("**简化版**")
                    if show_notes:
                        df_show2 = _with_notes_first_col(df_simpl, simplified_tips, col_name="说明")
                        st.dataframe(df_show2.style.format(_numeric_format), use_container_width=True, height=620)
                    else:
                        st.dataframe(df_simpl.style.format(_numeric_format), use_container_width=True, height=620)

                st.divider()
                # --- 新建系统：STC 并列视图（仅影响展示，不改原数据） ---
                if getattr(cfg, "stc_enable", True):
                    st.markdown("**STC 粗略抵扣（展示）** — 并列显示不含/含 STC 的报价与回本（基线）。")
                    cols_names = ["Plan A", "Plan B", "Plan C", "Plan D"]
                    comp_index = [
                        "price_base_no_stc",
                        "price_base_with_stc",
                        "payback_base_no_stc",
                        "payback_base_with_stc",
                        "stc_count",
                        "stc_credit_aud",
                    ]
                    df_comp = pd.DataFrame(index=comp_index, columns=cols_names, dtype=float)
                    for i, colname in enumerate(cols_names):
                        solar_kw = float(df_detailed.loc["solar_kw", colname])
                        total_cost = float(df_detailed.loc["total_cost", colname])
                        price_base = float(df_detailed.loc["price_base", colname])
                        payback_base = float(df_detailed.loc["payback_base_years", colname])
                        # 反推出 annual_benefit（基线）
                        annual_benefit = price_base / payback_base if payback_base and not math.isinf(payback_base) else 0.0
                        stc_count = round(solar_kw * cfg.stc_zone_rating * int(cfg.stc_years_to_2030))
                        stc_credit = stc_count * cfg.stc_price_aud
                        total_cost_after = max(total_cost - stc_credit, 0.0)
                        price_after = total_cost_after * (1 + cfg.profit_margin_rate)
                        payback_after = (price_after / annual_benefit) if annual_benefit > 0 else float("inf")
                        df_comp.loc[:, colname] = [
                            price_base,
                            price_after,
                            payback_base,
                            payback_after,
                            stc_count,
                            stc_credit,
                        ]
                    st.dataframe(df_comp.style.format(_numeric_format), use_container_width=True)

                st.divider()
                st.markdown("**粗略估算（cap=Med）** — 按你提出的公式展示：自用/上网/年节省与回本。")
                show_rough = st.checkbox("显示粗略估算结果", value=True)
                if show_rough:
                    try:
                        from calc_engine import _plan_target_sc, _plan_capacity
                    except Exception:
                        _plan_target_sc = _plan_capacity = None
                    if _plan_capacity is None:
                        st.warning("找不到容量/自用率函数，无法计算粗略估算。")
                    else:
                        cols = ["Plan A", "Plan B", "Plan C", "Plan D"]
                        index = [
                            "annual_generation_kwh",
                            "self_use_kwh_effective",
                            "export_kwh",
                            "self_use_rate_effective",
                            "annual_savings",
                            "price_base",
                            "payback_years",
                        ]
                        df_rough = pd.DataFrame(index=index, columns=cols, dtype=float)
                        cap_med = float(cfg.annual_home_usage_proxy_med)
                        opt_enable = bool(getattr(cfg, "rough_optimize_enable", False))
                        opt_factor = float(getattr(cfg, "rough_optimize_factor", 1.08))
                        if opt_enable:
                            st.info(f"行为优化已开启：有效自用率按 {opt_factor:.2f} 倍参考提升（仍受 cap 截断，且不影响正式结果）")
                        for i, letter in enumerate(["A", "B", "C", "D"]):
                            colname = cols[i]
                            solar_kw = _plan_capacity(cfg, letter)
                            annual_gen = solar_kw * cfg.yield_per_kw_per_year
                            target_sc = _plan_target_sc(cfg, letter)
                            eff_target = target_sc * (opt_factor if opt_enable else 1.0)
                            eff_target = min(eff_target, 1.0)
                            used = min(annual_gen * eff_target, cap_med)
                            export = max(annual_gen - used, 0.0)
                            savings = used * cfg.grid_buy_rate + export * cfg.grid_sell_rate
                            price_base = float(df_detailed.loc["price_base", colname]) if "price_base" in df_detailed.index else 0.0
                            payback = (price_base / savings) if savings > 0 else float("inf")
                            eff_sc = (used / annual_gen) if annual_gen > 0 else 0.0
                            df_rough.loc[:, colname] = [
                                annual_gen,
                                used,
                                export,
                                eff_sc,
                                savings,
                                price_base,
                                payback,
                            ]
                        tips = {
                            "self_use_kwh_effective": "有效自用电量 = MIN(年发电×目标自用率, annual_home_usage_proxy_med)",
                            "export_kwh": "上网电量 = 年发电 - 自用",
                            "self_use_rate_effective": "有效自用率 = 自用/年发电（已受cap截断）",
                            "annual_savings": "年节省 = 自用×购电价 + 上网×售电价",
                            "payback_years": "回本周期 = 报价/年节省（报价取详细版的 price_base）",
                        }
                        if show_notes:
                            df_show_rough = _with_notes_first_col(df_rough, tips, col_name="说明")
                            st.dataframe(df_show_rough.style.format(_numeric_format), use_container_width=True)
                        else:
                            st.dataframe(df_rough.style.format(_numeric_format), use_container_width=True)

    with tabs[1]:
        st.markdown("<div class='section-title'>储能扩容（Battery Retrofit）</div>", unsafe_allow_html=True)
        if cfg is None:
            st.info("请在左侧设置参数并点击‘应用参数并计算’。")
        else:
            df_ret = compute_battery_retrofit(cfg)
            retrofit_tips = {
                "battery_nominal_kwh": "名义容量：来自侧边栏 Retrofit 建议",
                "usable_battery_capacity_kwh": "可用容量：nominal * DoD",
                "annual_shifted_kwh_est": "估计可转移：usable * 有效系数 * 365",
                "max_shiftable_kwh": "可最大转移：由剩余馈网量决定",
                "final_annual_shifted_kwh": "实际转移：MIN(估计, 最大)",
                "annual_savings": "年节省：(购电-馈网) * 实际转移",
                "total_cost": "总成本：电池+安装基础+单位安装费",
                "price_base": "报价：total_cost * (1 + 利润率)",
                "payback_years": "回本：price / annual_savings",
                "new_self_consumption_rate": "新自用率：基线自用 + 转移量 / 年发电",
                "roi_warning": "ROI 提示：转移量 < 500 kWh/年 则提示 Low ROI",
            }
            if show_notes:
                df_show3 = _with_notes_first_col(df_ret, retrofit_tips, col_name="说明")
                st.dataframe(df_show3.style.format(_numeric_format), use_container_width=True, height=620)
            else:
                st.dataframe(df_ret.style.format(_numeric_format), use_container_width=True, height=620)

            # 并列：含/不含电池补贴
            st.divider()
            st.markdown("**电池补贴（展示）** — 并列显示不含/含补贴的报价与回本。")
            comp_idx = [
                "price_base_no_rebate",
                "price_base_with_rebate",
                "payback_no_rebate",
                "payback_with_rebate",
                "rebate_applied_aud",
            ]
            cols_names = list(df_ret.columns)
            df_comp2 = pd.DataFrame(index=comp_idx, columns=cols_names, dtype=float)
            for name in cols_names:
                total_cost = float(df_ret.loc["total_cost", name])
                price_base = float(df_ret.loc["price_base", name])
                payback = float(df_ret.loc["payback_years", name])
                annual_savings = price_base / payback if payback and not math.isinf(payback) else 0.0
                nominal = float(df_ret.loc["battery_nominal_kwh", name])
                rebate_fixed = float(getattr(cfg, "rebate_fixed_aud", 0.0))
                rebate_per_kwh = float(getattr(cfg, "rebate_per_kwh_aud", 0.0))
                stack = getattr(cfg, "rebate_stack_mode", "stack") == "stack"
                if stack:
                    rebate_total = rebate_fixed + rebate_per_kwh * nominal
                else:
                    rebate_total = max(rebate_fixed, rebate_per_kwh * nominal)
                cap_total = float(getattr(cfg, "rebate_cap_aud", 0.0))
                if cap_total > 0:
                    rebate_total = min(rebate_total, cap_total)
                total_after = max(total_cost - rebate_total, 0.0)
                price_after = total_after * (1 + cfg.profit_margin_rate)
                payback_after = (price_after / annual_savings) if annual_savings > 0 else float("inf")
                df_comp2.loc[:, name] = [
                    price_base,
                    price_after,
                    payback,
                    payback_after,
                    rebate_total,
                ]
            st.dataframe(df_comp2.style.format(_numeric_format), use_container_width=True)

    with tabs[2]:
        st.markdown("<div class='section-title'>参数总览</div>", unsafe_allow_html=True)
        p_md = (Path(__file__).resolve().parent / "docs" / "parameters.md")
        p_html = (Path(__file__).resolve().parent / "docs" / "parameters.html")
        # 动态生成 HTML：以当前 InputsConfig 默认值渲染
        try:
            from schemas import InputsConfig as _IC
            _cfg = _IC.default()
            rows = [
                ("roof_total_area_m2", "屋顶总面积 (m²)", _cfg.roof_total_area_m2, "来自上游 3D/测绘估算"),
                ("roof_effective_area_m2", "屋顶有效面积 (m²)", _cfg.roof_effective_area_m2, "过滤朝向/过小坡面后的有效面积"),
                ("roof_max_panels", "屋顶最大面板数 (块)", _cfg.roof_max_panels, "上游计算得出/可人工修正"),
                ("panel_area_m2", "单块面板面积 (m²)", _cfg.panel_area_m2, "面板规格"),
                ("panel_power_kw", "单块面板功率 (kW)", _cfg.panel_power_kw, "面板标称功率"),
                ("panel_unit_cost", "单块面板成本 (AUD/块)", _cfg.panel_unit_cost, "详细版使用"),
                ("inverter_unit_cost_per_kw", "逆变器成本 (AUD/kW)", _cfg.inverter_unit_cost_per_kw, "详细版使用"),
                ("hardware_cost_per_kw", "硬件包价 (AUD/kW)", _cfg.hardware_cost_per_kw, "简化版使用（含 PV+逆变器 等）"),
                ("battery_unit_cost_per_kwh", "电池成本 (AUD/kWh)", _cfg.battery_unit_cost_per_kwh, ""),
                ("install_base_cost", "安装基础费用 (AUD)", _cfg.install_base_cost, ""),
                ("install_cost_per_kw", "安装每 kW 费用 (AUD/kW)", _cfg.install_cost_per_kw, ""),
                ("dc_ac_ratio", "容配比 (DC/AC)", _cfg.dc_ac_ratio, "影响逆变器容量取整"),
                ("yield_per_kw_per_year", "每 kW 年发电量 (kWh/kW/年)", _cfg.yield_per_kw_per_year, "兜底值；如接入 pvlib 则以模型为准"),
                ("baseline_self_consumption_rate", "基线自用率", _cfg.baseline_self_consumption_rate, "无电池条件下的自用率估计"),
                ("plan_a_capacity_factor", "方案A 容量系数", _cfg.plan_a_capacity_factor, "参与计算装机 kW，并受上下限钳制"),
                ("plan_b_capacity_factor", "方案B 容量系数", _cfg.plan_b_capacity_factor, "同上"),
                ("plan_c_capacity_factor", "方案C 容量系数", _cfg.plan_c_capacity_factor, "同上"),
                ("plan_d_capacity_factor", "方案D 容量系数", _cfg.plan_d_capacity_factor, "同上"),
                ("plan_a_min_kw", "方案A 最小上装机下限 (kW)", _cfg.plan_a_min_kw, "每方案单独上下限"),
                ("plan_a_max_kw", "方案A 最大上限 (kW)", _cfg.plan_a_max_kw, ""),
                ("plan_b_min_kw", "方案B 最小上装机下限 (kW)", _cfg.plan_b_min_kw, ""),
                ("plan_b_max_kw", "方案B 最大上限 (kW)", _cfg.plan_b_max_kw, ""),
                ("plan_c_min_kw", "方案C 最小上装机下限 (kW)", _cfg.plan_c_min_kw, ""),
                ("plan_c_max_kw", "方案C 最大上限 (kW)", _cfg.plan_c_max_kw, ""),
                ("plan_d_min_kw", "方案D 最小上装机下限 (kW)", _cfg.plan_d_min_kw, ""),
                ("plan_d_max_kw", "方案D 最大上限 (kW)", _cfg.plan_d_max_kw, ""),
                ("plan_a_target_sc_rate", "方案A 目标自用率", _cfg.plan_a_target_sc_rate, "与基线之差用于推导电池容量（若>0）"),
                ("plan_b_target_sc_rate", "方案B 目标自用率", _cfg.plan_b_target_sc_rate, ""),
                ("plan_c_target_sc_rate", "方案C 目标自用率", _cfg.plan_c_target_sc_rate, ""),
                ("plan_d_target_sc_rate", "方案D 目标自用率", _cfg.plan_d_target_sc_rate, ""),
                ("battery_dod", "电池放电深度 DoD", _cfg.battery_dod, "用于电池标称容量计算"),
                ("battery_rte", "电池往返效率 RTE", _cfg.battery_rte, "同上"),
                ("battery_install_base_cost", "电池安装基础费 (AUD)", _cfg.battery_install_base_cost, ""),
                ("battery_install_cost_per_kwh", "电池安装每 kWh 费用 (AUD/kWh)", _cfg.battery_install_cost_per_kwh, ""),
                ("battery_effective_usage_factor", "电池有效使用系数", _cfg.battery_effective_usage_factor, "Retrofit 估算使用天数与利用率"),
                ("profit_margin_rate", "利润率", _cfg.profit_margin_rate, "用于报价 price_base = total_cost*(1+rate)"),
                ("price_range_percent", "报价浮动范围（占位）", _cfg.price_range_percent, "当前未直接用于公式，可扩展"),
                ("grid_buy_rate", "购电价 (AUD/kWh)", _cfg.grid_buy_rate, ""),
                ("grid_sell_rate", "馈网价/售电价 (AUD/kWh)", _cfg.grid_sell_rate, "有校验：不高于购电价"),
                ("annual_home_usage_proxy_low", "家庭年用电代理-低 (kWh/年)", _cfg.annual_home_usage_proxy_low, "用于截断自用收益上限"),
                ("annual_home_usage_proxy_med", "家庭年用电代理-中 (kWh/年)", _cfg.annual_home_usage_proxy_med, "回本计算默认使用 med（或方案映射）"),
                ("annual_home_usage_proxy_high", "家庭年用电代理-高 (kWh/年)", _cfg.annual_home_usage_proxy_high, "可用于多场景"),
                ("existing_solar_annual_gen_kwh", "既有系统估算年发电量 (kWh/年)", _cfg.existing_solar_annual_gen_kwh or "—", "为空则按屋顶估算"),
                ("existing_sc_rate", "既有系统基线自用率", _cfg.existing_sc_rate, "Retrofit 计算中使用"),
                ("retrofit_plan_a_kwh", "Retrofit 建议容量 A (kWh)", _cfg.retrofit_plan_a_kwh, "仅 Retrofit 表用"),
                ("retrofit_plan_b_kwh", "Retrofit 建议容量 B (kWh)", _cfg.retrofit_plan_b_kwh, ""),
                ("retrofit_plan_c_kwh", "Retrofit 建议容量 C (kWh)", _cfg.retrofit_plan_c_kwh, ""),
                ("retrofit_plan_d_kwh", "Retrofit 建议容量 D (kWh)", _cfg.retrofit_plan_d_kwh, ""),
            ]
            html = [
                "<!doctype html>",
                "<html lang='zh'>",
                "<head>",
                "<meta charset='utf-8'/>",
                "<meta name='viewport' content='width=device-width, initial-scale=1' />",
                "<title>参数总览（InputsConfig）</title>",
                "<style>body{font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,Helvetica,Arial,sans-serif;padding:24px;}h1{font-size:20px;margin:0 0 12px;}table{border-collapse:collapse;width:100%;}th,td{border:1px solid #e5e7eb;padding:8px 10px;font-size:14px;}th{background:#f9fafb;text-align:left;}tbody tr:nth-child(odd){background:#fbfdff;}code{color:#ef4444;}</style>",
                "</head>",
                "<body>",
                "<h1>参数总览（InputsConfig）</h1>",
                "<p>此页面由当前默认参数动态生成。</p>",
                "<table><thead><tr><th>Parameter (EN)</th><th>参数中文说明</th><th style='text-align:right;'>Value</th><th>Notes</th></tr></thead><tbody>",
            ]
            for k, zh, val, note in rows:
                v = "—" if val is None else val
                html.append(f"<tr><td>{k}</td><td>{zh}</td><td style='text-align:right;'>{v}</td><td>{note}</td></tr>")
            html.extend(["</tbody></table>", "</body>", "</html>"])
            p_html.write_text("\n".join(html), encoding="utf-8")
        except Exception as _e:
            st.warning(f"生成参数 HTML 失败：{_e}")
        if p_md.exists():
            content = p_md.read_text(encoding="utf-8")
            st.markdown(content, unsafe_allow_html=True)
        else:
            st.warning(f"未找到参数文档：{p_md}")
        st.divider()
        if p_html.exists():
            st.caption("静态 HTML 版本：")
            st.code(str(p_html), language="bash")
        else:
            st.caption("未生成静态 HTML（parameters.html）")

    with tabs[3]:
        st.subheader("计算逻辑（与 Excel 公式对齐）")
        doc_path = (Path(__file__).resolve().parent / "docs" / "proposal_logic.md")
        if doc_path.exists():
            content = doc_path.read_text(encoding="utf-8")
            st.markdown(content)
        else:
            st.warning(f"未找到文档：{doc_path}")


if __name__ == "__main__":
    main()
