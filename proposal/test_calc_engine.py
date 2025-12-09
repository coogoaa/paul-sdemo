#!/usr/bin/env python3
"""
测试用例：验证 calc_engine.py 的计算逻辑正确性
"""

import sys
from pathlib import Path

# 添加 proposal 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from schemas import InputsConfig
from calc_engine import (
    compute_plans_detailed, 
    compute_plans_simplified, 
    compute_battery_retrofit,
    _plan_capacity,
    _plan_target_sc,
    _annual_benefit_from_gen,
    ceil_to,
    int_floor,
    safe_payback
)

def test_helper_functions():
    """测试辅助函数"""
    print("=== 测试辅助函数 ===")
    
    # 测试 ceil_to（使用浮点数容差）
    assert abs(ceil_to(3.25, 0.1) - 3.3) < 1e-9, f"ceil_to(3.25, 0.1) = {ceil_to(3.25, 0.1)}, 期望 3.3"
    assert abs(ceil_to(3.2, 0.1) - 3.2) < 1e-9, f"ceil_to(3.2, 0.1) = {ceil_to(3.2, 0.1)}, 期望 3.2"
    assert abs(ceil_to(3.0, 0.1) - 3.0) < 1e-9, f"ceil_to(3.0, 0.1) = {ceil_to(3.0, 0.1)}, 期望 3.0"
    assert abs(ceil_to(5.67, 1.0) - 6.0) < 1e-9, f"ceil_to(5.67, 1.0) = {ceil_to(5.67, 1.0)}, 期望 6.0"
    
    # 测试 int_floor
    assert int_floor(3.9) == 3, f"int_floor(3.9) = {int_floor(3.9)}, 期望 3"
    assert int_floor(5.0) == 5, f"int_floor(5.0) = {int_floor(5.0)}, 期望 5"
    
    # 测试 safe_payback
    assert safe_payback(1000, 100) == 10.0, f"safe_payback(1000, 100) = {safe_payback(1000, 100)}, 期望 10.0"
    assert safe_payback(1000, 0) == float('inf'), f"safe_payback(1000, 0) = {safe_payback(1000, 0)}, 期望 inf"
    assert safe_payback(1000, -50) == float('inf'), f"safe_payback(1000, -50) = {safe_payback(1000, -50)}, 期望 inf"
    
    print("✓ 辅助函数测试通过")

def test_plan_capacity():
    """测试方案容量计算"""
    print("=== 测试方案容量计算 ===")
    
    cfg = InputsConfig.default()
    cfg.roof_max_panels = 20
    cfg.panel_power_kw = 0.5
    # 屋顶最大容量 = 20 * 0.5 = 10 kW
    
    # 测试 A 方案：容量系数 0.2，min 3.5，max 10
    cfg.plan_a_capacity_factor = 0.2
    cfg.plan_a_min_kw = 3.5
    cfg.plan_a_max_kw = 10.0
    
    base_a = 10 * 0.2  # 2.0 kW
    expected_a = max(min(base_a, 10.0), 3.5)  # max(min(2.0, 10.0), 3.5) = 3.5
    actual_a = _plan_capacity(cfg, "A")
    assert actual_a == expected_a, f"Plan A 容量: 实际 {actual_a}, 期望 {expected_a}"
    
    # 测试 B 方案：容量系数 0.5，min 4，max 13.3
    cfg.plan_b_capacity_factor = 0.5
    cfg.plan_b_min_kw = 4.0
    cfg.plan_b_max_kw = 13.3
    
    base_b = 10 * 0.5  # 5.0 kW
    expected_b = max(min(base_b, 13.3), 4.0)  # max(min(5.0, 13.3), 4.0) = 5.0
    actual_b = _plan_capacity(cfg, "B")
    assert actual_b == expected_b, f"Plan B 容量: 实际 {actual_b}, 期望 {expected_b}"
    
    # 测试 C 方案：容量系数 0.8，min 6，max 13.3
    cfg.plan_c_capacity_factor = 0.8
    cfg.plan_c_min_kw = 6.0
    cfg.plan_c_max_kw = 13.3
    
    base_c = 10 * 0.8  # 8.0 kW
    expected_c = max(min(base_c, 13.3), 6.0)  # max(min(8.0, 13.3), 6.0) = 8.0
    actual_c = _plan_capacity(cfg, "C")
    assert actual_c == expected_c, f"Plan C 容量: 实际 {actual_c}, 期望 {expected_c}"
    
    # 测试 D 方案：容量系数 1.0，min 8，max 20
    cfg.plan_d_capacity_factor = 1.0
    cfg.plan_d_min_kw = 8.0
    cfg.plan_d_max_kw = 20.0
    
    base_d = 10 * 1.0  # 10.0 kW
    expected_d = max(min(base_d, 20.0), 8.0)  # max(min(10.0, 20.0), 8.0) = 10.0
    actual_d = _plan_capacity(cfg, "D")
    assert actual_d == expected_d, f"Plan D 容量: 实际 {actual_d}, 期望 {expected_d}"
    
    print("✓ 方案容量计算测试通过")

def test_annual_benefit():
    """测试年收益计算"""
    print("=== 测试年收益计算 ===")
    
    cfg = InputsConfig.default()
    cfg.grid_buy_rate = 0.33
    cfg.grid_sell_rate = 0.07
    cfg.annual_home_usage_proxy_med = 6000
    
    # 测试用例1：发电量小于用电量
    annual_gen = 4000
    target_sc = 0.5
    used = min(annual_gen * target_sc, cfg.annual_home_usage_proxy_med)  # min(2000, 6000) = 2000
    export = max(annual_gen - used, 0)  # max(4000 - 2000, 0) = 2000
    expected_benefit = used * cfg.grid_buy_rate + export * cfg.grid_sell_rate  # 2000*0.33 + 2000*0.07 = 800
    actual_benefit = _annual_benefit_from_gen(cfg, annual_gen, target_sc)
    assert abs(actual_benefit - expected_benefit) < 0.01, f"年收益1: 实际 {actual_benefit}, 期望 {expected_benefit}"
    
    # 测试用例2：发电量大于用电量
    annual_gen = 10000
    target_sc = 0.8
    used = min(annual_gen * target_sc, cfg.annual_home_usage_proxy_med)  # min(8000, 6000) = 6000
    export = max(annual_gen - used, 0)  # max(10000 - 6000, 0) = 4000
    expected_benefit = used * cfg.grid_buy_rate + export * cfg.grid_sell_rate  # 6000*0.33 + 4000*0.07 = 2260
    actual_benefit = _annual_benefit_from_gen(cfg, annual_gen, target_sc)
    assert abs(actual_benefit - expected_benefit) < 0.01, f"年收益2: 实际 {actual_benefit}, 期望 {expected_benefit}"
    
    print("✓ 年收益计算测试通过")

def test_detailed_plan_calculation():
    """测试详细版计算的关键步骤"""
    print("=== 测试详细版计算 ===")
    
    cfg = InputsConfig.default()
    # 设置简化的测试参数
    cfg.roof_max_panels = 20
    cfg.panel_power_kw = 0.5  # 10 kW 总容量
    cfg.yield_per_kw_per_year = 1200
    cfg.dc_ac_ratio = 1.3
    cfg.baseline_self_consumption_rate = 0.3
    cfg.plan_a_capacity_factor = 0.5  # 5 kW
    cfg.plan_a_target_sc_rate = 0.4
    cfg.plan_a_min_kw = 3.5
    cfg.plan_a_max_kw = 10.0
    cfg.battery_dod = 0.9
    cfg.battery_rte = 0.9
    cfg.panel_unit_cost = 300
    cfg.inverter_unit_cost_per_kw = 500
    cfg.battery_unit_cost_per_kwh = 800
    cfg.install_base_cost = 1000
    cfg.install_cost_per_kw = 200
    cfg.profit_margin_rate = 0.1
    
    df = compute_plans_detailed(cfg)
    
    # 手动验证 Plan A 的计算
    solar_kw_a = 5.0  # 已验证过的容量
    panel_count_a = int_floor(solar_kw_a / cfg.panel_power_kw)  # int_floor(5.0 / 0.5) = 10
    inverter_kw_a = ceil_to(solar_kw_a / cfg.dc_ac_ratio, 0.1)  # ceil_to(5.0 / 1.3, 0.1) = ceil_to(3.846, 0.1) = 3.9
    annual_gen_a = solar_kw_a * cfg.yield_per_kw_per_year  # 5.0 * 1200 = 6000
    daily_shift_a = (annual_gen_a / 365) * (cfg.plan_a_target_sc_rate - cfg.baseline_self_consumption_rate)  # (6000/365) * (0.4-0.3) = 16.44 * 0.1 = 1.644
    battery_nominal_a = ceil_to(daily_shift_a / (cfg.battery_dod * cfg.battery_rte), 1.0)  # ceil_to(1.644 / (0.9*0.9), 1.0) = ceil_to(2.03, 1.0) = 3.0
    
    cost_panels_a = panel_count_a * cfg.panel_unit_cost  # 10 * 300 = 3000
    cost_inverter_a = inverter_kw_a * cfg.inverter_unit_cost_per_kw  # 3.9 * 500 = 1950
    cost_battery_a = battery_nominal_a * cfg.battery_unit_cost_per_kwh  # 3.0 * 800 = 2400
    cost_install_a = cfg.install_base_cost + solar_kw_a * cfg.install_cost_per_kw  # 1000 + 5.0 * 200 = 2000
    total_cost_a = cost_panels_a + cost_inverter_a + cost_battery_a + cost_install_a  # 3000 + 1950 + 2400 + 2000 = 9350
    price_base_a = total_cost_a * (1 + cfg.profit_margin_rate)  # 9350 * 1.1 = 10285
    
    # 验证计算结果
    assert abs(df.loc["solar_kw", "Plan A"] - solar_kw_a) < 0.01, f"solar_kw: 实际 {df.loc['solar_kw', 'Plan A']}, 期望 {solar_kw_a}"
    assert df.loc["panel_count", "Plan A"] == panel_count_a, f"panel_count: 实际 {df.loc['panel_count', 'Plan A']}, 期望 {panel_count_a}"
    assert abs(df.loc["inverter_kw", "Plan A"] - inverter_kw_a) < 0.01, f"inverter_kw: 实际 {df.loc['inverter_kw', 'Plan A']}, 期望 {inverter_kw_a}"
    assert abs(df.loc["annual_generation_kwh", "Plan A"] - annual_gen_a) < 0.01, f"annual_gen: 实际 {df.loc['annual_generation_kwh', 'Plan A']}, 期望 {annual_gen_a}"
    assert abs(df.loc["battery_nominal_kwh", "Plan A"] - battery_nominal_a) < 0.01, f"battery_nominal: 实际 {df.loc['battery_nominal_kwh', 'Plan A']}, 期望 {battery_nominal_a}"
    assert abs(df.loc["total_cost", "Plan A"] - total_cost_a) < 0.01, f"total_cost: 实际 {df.loc['total_cost', 'Plan A']}, 期望 {total_cost_a}"
    assert abs(df.loc["price_base", "Plan A"] - price_base_a) < 0.01, f"price_base: 实际 {df.loc['price_base', 'Plan A']}, 期望 {price_base_a}"
    
    print("✓ 详细版计算测试通过")

def test_simplified_plan_calculation():
    """测试简化版计算"""
    print("=== 测试简化版计算 ===")
    
    cfg = InputsConfig.default()
    cfg.roof_max_panels = 20
    cfg.panel_power_kw = 0.5
    cfg.plan_a_capacity_factor = 0.5
    cfg.plan_a_min_kw = 3.5
    cfg.plan_a_max_kw = 10.0
    cfg.plan_a_target_sc_rate = 0.4
    cfg.baseline_self_consumption_rate = 0.3
    cfg.battery_dod = 0.9
    cfg.battery_rte = 0.9
    cfg.battery_unit_cost_per_kwh = 800
    cfg.hardware_cost_per_kw = 1500
    cfg.install_base_cost = 1000
    cfg.install_cost_per_kw = 200
    cfg.profit_margin_rate = 0.1
    cfg.yield_per_kw_per_year = 1200
    
    df = compute_plans_simplified(cfg)
    
    # 手动验证 Plan A（现在包含电池成本）
    solar_kw_a = 5.0
    annual_gen_a = solar_kw_a * cfg.yield_per_kw_per_year  # 5.0 * 1200 = 6000
    daily_shift_a = (annual_gen_a / 365.0) * (cfg.plan_a_target_sc_rate - cfg.baseline_self_consumption_rate)  # (6000/365) * (0.4-0.3) = 1.644
    battery_nominal_a = ceil_to(daily_shift_a / (cfg.battery_dod * cfg.battery_rte), 1.0)  # ceil_to(1.644 / 0.81, 1.0) = 3.0
    
    total_hardware_cost_a = solar_kw_a * cfg.hardware_cost_per_kw  # 5.0 * 1500 = 7500
    cost_battery_a = battery_nominal_a * cfg.battery_unit_cost_per_kwh  # 3.0 * 800 = 2400
    cost_install_a = cfg.install_base_cost + solar_kw_a * cfg.install_cost_per_kw  # 1000 + 5.0 * 200 = 2000
    total_cost_a = total_hardware_cost_a + cost_battery_a + cost_install_a  # 7500 + 2400 + 2000 = 11900
    price_base_a = total_cost_a * (1 + cfg.profit_margin_rate)  # 11900 * 1.1 = 13090
    
    assert abs(df.loc["total_hardware_cost", "Plan A"] - total_hardware_cost_a) < 0.01, f"hardware_cost: 实际 {df.loc['total_hardware_cost', 'Plan A']}, 期望 {total_hardware_cost_a}"
    assert abs(df.loc["cost_battery", "Plan A"] - cost_battery_a) < 0.01, f"battery_cost: 实际 {df.loc['cost_battery', 'Plan A']}, 期望 {cost_battery_a}"
    assert abs(df.loc["total_cost", "Plan A"] - total_cost_a) < 0.01, f"total_cost: 实际 {df.loc['total_cost', 'Plan A']}, 期望 {total_cost_a}"
    assert abs(df.loc["price_base", "Plan A"] - price_base_a) < 0.01, f"price_base: 实际 {df.loc['price_base', 'Plan A']}, 期望 {price_base_a}"
    
    print("✓ 简化版计算测试通过")

def test_retrofit_calculation():
    """测试储能扩容计算"""
    print("=== 测试储能扩容计算 ===")
    
    cfg = InputsConfig.default()
    cfg.retrofit_plan_a_kwh = 10.0
    cfg.battery_dod = 0.9
    cfg.battery_effective_usage_factor = 0.7
    cfg.roof_max_panels = 20
    cfg.panel_power_kw = 0.5
    cfg.existing_sc_rate = 0.3
    cfg.existing_solar_annual_gen_kwh = None  # 使用估算
    cfg.grid_buy_rate = 0.33
    cfg.grid_sell_rate = 0.07
    cfg.battery_unit_cost_per_kwh = 800
    cfg.battery_install_base_cost = 500
    cfg.battery_install_cost_per_kwh = 100
    cfg.profit_margin_rate = 0.1
    
    df = compute_battery_retrofit(cfg)
    
    # 手动验证 Retrofit A
    nominal_a = 10.0
    usable_a = nominal_a * cfg.battery_dod  # 10.0 * 0.9 = 9.0
    annual_est_a = usable_a * cfg.battery_effective_usage_factor * 365  # 9.0 * 0.7 * 365 = 2299.5
    estimated_gen = cfg.roof_max_panels * cfg.panel_power_kw * 0.7 * 1200  # 20 * 0.5 * 0.7 * 1200 = 8400
    max_shift_a = estimated_gen * (1 - cfg.existing_sc_rate)  # 8400 * (1 - 0.3) = 5880
    final_shift_a = min(annual_est_a, max_shift_a)  # min(2299.5, 5880) = 2299.5
    annual_savings_a = final_shift_a * (cfg.grid_buy_rate - cfg.grid_sell_rate)  # 2299.5 * (0.33 - 0.07) = 597.87
    total_cost_a = nominal_a * cfg.battery_unit_cost_per_kwh + cfg.battery_install_base_cost + nominal_a * cfg.battery_install_cost_per_kwh  # 10*800 + 500 + 10*100 = 9500
    price_base_a = total_cost_a * (1 + cfg.profit_margin_rate)  # 9500 * 1.1 = 10450
    payback_a = price_base_a / annual_savings_a  # 10450 / 597.87 ≈ 17.48
    
    assert abs(df.loc["usable_battery_capacity_kwh", "Retrofit A"] - usable_a) < 0.01, f"usable: 实际 {df.loc['usable_battery_capacity_kwh', 'Retrofit A']}, 期望 {usable_a}"
    assert abs(df.loc["final_annual_shifted_kwh", "Retrofit A"] - final_shift_a) < 0.01, f"final_shift: 实际 {df.loc['final_annual_shifted_kwh', 'Retrofit A']}, 期望 {final_shift_a}"
    assert abs(df.loc["annual_savings", "Retrofit A"] - annual_savings_a) < 0.01, f"annual_savings: 实际 {df.loc['annual_savings', 'Retrofit A']}, 期望 {annual_savings_a}"
    assert abs(df.loc["total_cost", "Retrofit A"] - total_cost_a) < 0.01, f"total_cost: 实际 {df.loc['total_cost', 'Retrofit A']}, 期望 {total_cost_a}"
    assert abs(df.loc["payback_years", "Retrofit A"] - payback_a) < 0.1, f"payback: 实际 {df.loc['payback_years', 'Retrofit A']}, 期望 {payback_a}"
    
    # 验证 ROI 提示
    roi_warning_a = "Low ROI - small export available" if final_shift_a < 500 else "OK"
    assert df.loc["roi_warning", "Retrofit A"] == roi_warning_a, f"ROI warning: 实际 {df.loc['roi_warning', 'Retrofit A']}, 期望 {roi_warning_a}"
    
    print("✓ 储能扩容计算测试通过")

def run_all_tests():
    """运行所有测试"""
    print("开始运行计算引擎测试...")
    print()
    
    try:
        test_helper_functions()
        test_plan_capacity()
        test_annual_benefit()
        test_detailed_plan_calculation()
        test_simplified_plan_calculation()
        test_retrofit_calculation()
        
        print()
        print("🎉 所有测试通过！计算逻辑正确。")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
