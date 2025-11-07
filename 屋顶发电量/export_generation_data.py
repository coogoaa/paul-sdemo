#!/usr/bin/env python3
"""
导出原始发电量数据
- monthlyHourlyPowerList: 每月每小时发电量 (12月 × 24小时)
- annualGeneratePower: 年度发电量
- monthlyDailyPowerList: 每月每日发电量
- monthlyPowerList: 每月总发电量
"""

import json
import csv
from pathlib import Path


def load_json(file_path):
    """加载 JSON 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_nested_json(json_str):
    """解析嵌套的 JSON 字符串"""
    if not json_str:
        return None
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None


def export_monthly_hourly_power(data_list, output_path):
    """导出 monthlyHourlyPowerList - 每月每小时发电量"""
    rows = []
    
    for data in data_list:
        if 'data' not in data or 'designs' not in data['data']:
            continue
            
        project_id = data['data'].get('id')
        
        for design in data['data']['designs']:
            design_id = design.get('id')
            design_name = design.get('designName')
            
            layout = parse_nested_json(design.get('layout'))
            if not layout or 'panelLocationInfos' not in layout:
                continue
            
            for panel_idx, panel in enumerate(layout['panelLocationInfos']):
                if 'generationPowerVO' not in panel:
                    continue
                
                gen_power = panel['generationPowerVO']
                monthly_hourly = gen_power.get('monthlyHourlyPowerList', [])
                
                # 遍历12个月
                for month_idx, hourly_list in enumerate(monthly_hourly, 1):
                    # 遍历24小时
                    for hour_idx, power in enumerate(hourly_list):
                        rows.append({
                            'projectId': project_id,
                            'designId': design_id,
                            'designName': design_name,
                            'panelIndex': panel_idx,
                            'month': month_idx,
                            'hour': hour_idx,
                            'power': power
                        })
    
    if rows:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f'✓ monthlyHourlyPowerList: {output_path} ({len(rows)} 条记录)')


def export_annual_generate_power(data_list, output_path):
    """导出 annualGeneratePower - 年度发电量"""
    rows = []
    
    for data in data_list:
        if 'data' not in data or 'designs' not in data['data']:
            continue
            
        project_id = data['data'].get('id')
        
        for design in data['data']['designs']:
            design_id = design.get('id')
            design_name = design.get('designName')
            system_size = design.get('systemSize')
            
            layout = parse_nested_json(design.get('layout'))
            if not layout or 'panelLocationInfos' not in layout:
                continue
            
            for panel_idx, panel in enumerate(layout['panelLocationInfos']):
                if 'generationPowerVO' not in panel:
                    continue
                
                gen_power = panel['generationPowerVO']
                annual_power = gen_power.get('annualGeneratePower', 0)
                
                rows.append({
                    'projectId': project_id,
                    'designId': design_id,
                    'designName': design_name,
                    'systemSize': system_size,
                    'panelIndex': panel_idx,
                    'annualGeneratePower': annual_power
                })
    
    if rows:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f'✓ annualGeneratePower: {output_path} ({len(rows)} 条记录)')


def export_monthly_daily_power(data_list, output_path):
    """导出 monthlyDailyPowerList - 每月平均每日发电量"""
    rows = []
    
    for data in data_list:
        if 'data' not in data or 'designs' not in data['data']:
            continue
            
        project_id = data['data'].get('id')
        
        for design in data['data']['designs']:
            design_id = design.get('id')
            design_name = design.get('designName')
            
            layout = parse_nested_json(design.get('layout'))
            if not layout or 'panelLocationInfos' not in layout:
                continue
            
            for panel_idx, panel in enumerate(layout['panelLocationInfos']):
                if 'generationPowerVO' not in panel:
                    continue
                
                gen_power = panel['generationPowerVO']
                monthly_daily_list = gen_power.get('monthlyDailyPowerList', [])
                
                # 遍历12个月（每个值是该月的平均每日发电量）
                for month_idx, avg_daily_power in enumerate(monthly_daily_list, 1):
                    rows.append({
                        'projectId': project_id,
                        'designId': design_id,
                        'designName': design_name,
                        'panelIndex': panel_idx,
                        'month': month_idx,
                        'avgDailyPower': avg_daily_power
                    })
    
    if rows:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f'✓ monthlyDailyPowerList: {output_path} ({len(rows)} 条记录)')


def export_monthly_power(data_list, output_path):
    """导出 monthlyPowerList - 每月总发电量"""
    rows = []
    
    for data in data_list:
        if 'data' not in data or 'designs' not in data['data']:
            continue
            
        project_id = data['data'].get('id')
        
        for design in data['data']['designs']:
            design_id = design.get('id')
            design_name = design.get('designName')
            
            layout = parse_nested_json(design.get('layout'))
            if not layout or 'panelLocationInfos' not in layout:
                continue
            
            for panel_idx, panel in enumerate(layout['panelLocationInfos']):
                if 'generationPowerVO' not in panel:
                    continue
                
                gen_power = panel['generationPowerVO']
                monthly_power = gen_power.get('monthlyPowerList', [])
                
                # 遍历12个月
                for month_idx, power in enumerate(monthly_power, 1):
                    rows.append({
                        'projectId': project_id,
                        'designId': design_id,
                        'designName': design_name,
                        'panelIndex': panel_idx,
                        'month': month_idx,
                        'power': power
                    })
    
    if rows:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f'✓ monthlyPowerList: {output_path} ({len(rows)} 条记录)')


def main():
    base_dir = Path(__file__).parent
    sample_dir = base_dir / 'sample'
    output_dir = base_dir / 'output'
    
    print('=== 开始导出原始发电量数据 ===\n')
    
    # 加载包含 layout 的文件
    view_files = [
        sample_dir / 'creat_battery_view.json',
        sample_dir / 'creat_newsys_preview.json',
    ]
    
    view_data = []
    for file_path in view_files:
        if file_path.exists():
            view_data.append(load_json(file_path))
    
    # 导出各类发电量数据
    export_monthly_hourly_power(view_data, output_dir / 'monthlyHourlyPowerList.csv')
    export_annual_generate_power(view_data, output_dir / 'annualGeneratePower.csv')
    export_monthly_daily_power(view_data, output_dir / 'monthlyDailyPowerList.csv')
    export_monthly_power(view_data, output_dir / 'monthlyPowerList.csv')
    
    print('\n=== 原始发电量数据导出完成 ===')


if __name__ == '__main__':
    main()
