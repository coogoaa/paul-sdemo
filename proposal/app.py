import os
from pathlib import Path

import streamlit as st
import pandas as pd
import math
from types import SimpleNamespace

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
        cfg.plan_a_min_kw = st.number_input("A 最小装机下限 (kW)", min_value=0.0, value=float(cfg.plan_a_min_kw), step=0.1)
        cfg.plan_c_max_kw = st.number_input("C 最大上限 (kW)", min_value=0.0, value=float(cfg.plan_c_max_kw), step=0.1)
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
        cfg.grid_buy_rate = st.number_input("购电价 (AUD/kWh)", min_value=0.0, value=float(cfg.grid_buy_rate), step=0.01)
        cfg.grid_sell_rate = st.number_input("馈网价 (AUD/kWh)", min_value=0.0, value=float(cfg.grid_sell_rate), step=0.01)
        cfg.annual_home_usage_proxy_med = st.number_input("年用电代理 (kWh/年)", min_value=0.0, value=float(cfg.annual_home_usage_proxy_med), step=100.0)

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

    def _attach_tooltips(df: pd.DataFrame, tooltips_map: dict, first_col_name: str) -> pd.io.formats.style.Styler:
        sty = df.style.format(_numeric_format)
        try:
            # 仅在首列（如 Plan A）添加逐行提示
            tips = pd.DataFrame("", index=df.index, columns=df.columns)
            if first_col_name in tips.columns:
                for idx, tip in tooltips_map.items():
                    if idx in tips.index:
                        tips.loc[idx, first_col_name] = tip
            sty = sty.set_tooltips(tips)
        except Exception:
            pass
        return sty

    # 侧边栏：参数与导出
    with st.sidebar:
        cfg = sidebar_params()
        st.divider()
        st.subheader("导出")
        if st.button("一键导出 Excel（详细版与简化版）"):
            export_excels()
        st.caption("导出路径：proposal/outputs/")

    # 主区：三个 Tab（新增“计算逻辑”）
    tabs = st.tabs(["新建系统（详细/简化 对比）", "储能扩容（Battery Retrofit）", "计算逻辑（文档）"]) 

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
                    "battery_pack_suggested_kwh": "商用品规建议：按 20/13.5/10/6.5/5 分档",
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
                    sty = _attach_tooltips(df_detailed, detailed_tips, first_col_name="Plan A")
                    st.dataframe(sty, use_container_width=True, height=620)
                with col2:
                    st.markdown("**简化版**")
                    sty2 = _attach_tooltips(df_simpl, simplified_tips, first_col_name="Plan A")
                    st.dataframe(sty2, use_container_width=True, height=620)

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
            sty3 = _attach_tooltips(df_ret, retrofit_tips, first_col_name="Retrofit A")
            st.dataframe(sty3, use_container_width=True, height=620)

    with tabs[2]:
        st.subheader("计算逻辑（与 Excel 公式对齐）")
        doc_path = (Path(__file__).resolve().parent / "docs" / "proposal_logic.md")
        if doc_path.exists():
            content = doc_path.read_text(encoding="utf-8")
            st.markdown(content)
        else:
            st.warning(f"未找到文档：{doc_path}")


if __name__ == "__main__":
    main()
