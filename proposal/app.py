import os
from pathlib import Path

import streamlit as st

# 本应用不修改现有 proposal/proposal.py，而是仅调用其中的导出函数
try:
    # 在以 "streamlit run proposal/app.py" 方式启动时，可直接导入同目录模块
    from proposal import proposal as proposal_excel
except ModuleNotFoundError:
    # 兼容在 proposal 目录内部运行
    import proposal as proposal_excel

try:
    from schemas import InputsConfig
except ModuleNotFoundError:
    InputsConfig = None  # 占位，后续实现

APP_TITLE = "光伏与储能报价演示（Streamlit）"
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def export_excels():
    """调用现有 Excel 生成函数，导出到 proposal/outputs/ 目录。"""
    detailed_path = OUTPUT_DIR / "solar_estimate_recommended.xlsx"
    simplified_path = OUTPUT_DIR / "solar_estimate_simplified_hardware_cost.xlsx"
    try:
        proposal_excel.create_detailed_file(str(detailed_path))
        proposal_excel.create_simplified_file(str(simplified_path))
        st.success(f"已导出 Excel 至: {OUTPUT_DIR}")
        st.write("- 详细版:", detailed_path)
        st.write("- 简化版:", simplified_path)
    except Exception as e:
        st.error(f"导出失败: {e}")


def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.caption("注意：当前为骨架版，计算引擎即将接入。可先体验 Excel 一键导出功能。")

    # 侧边栏：配置管理（占位）
    with st.sidebar:
        st.header("参数配置（占位）")
        st.write("后续将提供完整的参数表单、导入/导出 JSON、恢复默认等功能。")
        st.divider()
        st.subheader("导出")
        if st.button("一键导出 Excel（详细版与简化版）"):
            export_excels()
        st.caption("导出路径：proposal/outputs/")

    # 主区：两个 Tab
    tabs = st.tabs(["新建系统（详细/简化 对比）", "储能扩容（Battery Retrofit）"]) 

    with tabs[0]:
        st.subheader("对比视图（占位）")
        st.info("将在此展示 A/B/C/D 方案的关键指标表格与图表，支持在 详细版/简化版 之间切换对比。")
        st.write("— 计划接入指标：solar_kw, panel_count, inverter_kw(详细), annual_generation_kwh, total_cost, price_base, payback_* 等")

    with tabs[1]:
        st.subheader("储能扩容（占位）")
        st.info("将在此展示 A/B/C/D 容量档的 annual_savings, price_base, payback_years, new_self_consumption_rate 等对比图表。")


if __name__ == "__main__":
    main()
