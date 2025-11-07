#!/usr/bin/env python3
"""
将 sample 目录的 JSON 数据按类别导出为 CSV 文件
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any


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


def export_project_info(data_list: List[Dict], output_path: Path):
    """导出项目基本信息"""
    rows = []
    for data in data_list:
        if 'data' in data:
            d = data['data']
            rows.append({
                'id': d.get('id'),
                'projectCode': d.get('projectCode'),
                'address': d.get('address'),
                'countryCode': d.get('countryCode'),
                'state': d.get('state'),
                'city': d.get('city'),
                'siteZip': d.get('siteZip'),
                'longitude': d.get('longitude'),
                'latitude': d.get('latitude'),
                'type': d.get('type'),
                'installerCode': d.get('installerCode'),
                'mapLink': d.get('mapLink'),
            })
    
    if rows:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f'✓ 项目信息: {output_path} ({len(rows)} 条记录)')


def export_designs(data_list: List[Dict], output_path: Path):
    """导出设计方案信息"""
    rows = []
    for data in data_list:
        if 'data' in data and 'designs' in data['data']:
            project_id = data['data'].get('id')
            for design in data['data']['designs']:
                rows.append({
                    'projectId': project_id,
                    'designId': design.get('id'),
                    'designType': design.get('designType'),
                    'designName': design.get('designName'),
                    'systemSize': design.get('systemSize'),
                    'upfrontInvestmentMin': design.get('upfrontInvestmentMin'),
                    'upfrontInvestment': design.get('upfrontInvestment'),
                    'upfrontInvestmentMax': design.get('upfrontInvestmentMax'),
                    'subsidy': design.get('subsidy'),
                    'annualBillSavingsMin': design.get('annualBillSavingsMin'),
                    'annualBillSavings': design.get('annualBillSavings'),
                    'annualBillSavingsMax': design.get('annualBillSavingsMax'),
                    'irr': design.get('irr'),
                    'paybackPeriodMin': design.get('paybackPeriodMin'),
                    'paybackPeriod': design.get('paybackPeriod'),
                    'paybackPeriodMax': design.get('paybackPeriodMax'),
                    'batteryCapacity': design.get('batteryCapacity'),
                    'selfConsumptionMin': design.get('selfConsumptionMin'),
                    'selfConsumption': design.get('selfConsumption'),
                    'selfConsumptionMax': design.get('selfConsumptionMax'),
                })
    
    if rows:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f'✓ 设计方案: {output_path} ({len(rows)} 条记录)')


def export_panel_locations_from_payload(data_list: List[Dict], output_path: Path):
    """从 payload 文件导出面板位置信息"""
    rows = []
    for data in data_list:
        project_id = data.get('projectId')
        gis_time_id = data.get('gisTimeId')
        gis_date = data.get('gisDate')
        
        if 'panelLocationInfos' in data:
            for idx, panel in enumerate(data['panelLocationInfos']):
                rows.append({
                    'projectId': project_id,
                    'gisTimeId': gis_time_id,
                    'gisDate': gis_date,
                    'panelIndex': idx,
                    'aspect': panel.get('aspect'),
                    'slope': panel.get('slope'),
                    'startX': panel.get('start', [None, None, None])[0],
                    'startY': panel.get('start', [None, None, None])[1],
                    'startZ': panel.get('start', [None, None, None])[2],
                    'endX': panel.get('end', [None, None, None])[0],
                    'endY': panel.get('end', [None, None, None])[1],
                    'endZ': panel.get('end', [None, None, None])[2],
                    'centerX': panel.get('center', [None, None, None])[0],
                    'centerY': panel.get('center', [None, None, None])[1],
                    'centerZ': panel.get('center', [None, None, None])[2],
                    'positionsCount': len(panel.get('positions', [])) // 3,
                })
    
    if rows:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f'✓ 面板位置 (payload): {output_path} ({len(rows)} 条记录)')


def export_panel_locations_from_layout(data_list: List[Dict], output_path: Path):
    """从 layout 中导出面板位置和发电量信息"""
    rows = []
    for data in data_list:
        if 'data' not in data or 'designs' not in data['data']:
            continue
            
        project_id = data['data'].get('id')
        
        for design in data['data']['designs']:
            design_id = design.get('id')
            design_name = design.get('designName')
            
            # 解析 layout
            layout = parse_nested_json(design.get('layout'))
            if not layout or 'panelLocationInfos' not in layout:
                continue
            
            install_panel_count = layout.get('installPanelCount')
            
            for idx, panel in enumerate(layout['panelLocationInfos']):
                row = {
                    'projectId': project_id,
                    'designId': design_id,
                    'designName': design_name,
                    'installPanelCount': install_panel_count,
                    'panelIndex': idx,
                    'aspect': panel.get('aspect'),
                    'slope': panel.get('slope'),
                    'positionsCount': len(panel.get('positions', [])) // 3,
                }
                
                # 添加发电量信息
                if 'generationPowerVO' in panel:
                    gen_power = panel['generationPowerVO']
                    row['calStatus'] = gen_power.get('calStatus')
                    row['yearPower'] = gen_power.get('yearPower')
                    
                    # 月度发电量
                    monthly_power = gen_power.get('monthlyPowerList', [])
                    for month_idx, power in enumerate(monthly_power, 1):
                        row[f'month{month_idx}Power'] = power
                
                rows.append(row)
    
    if rows:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f'✓ 面板位置与发电量 (layout): {output_path} ({len(rows)} 条记录)')


def export_monthly_generation(data_list: List[Dict], output_path: Path):
    """导出月度发电量汇总"""
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
            
            # 汇总所有面板的月度发电量
            monthly_totals = [0] * 12
            year_total = 0
            
            for panel in layout['panelLocationInfos']:
                if 'generationPowerVO' in panel:
                    gen_power = panel['generationPowerVO']
                    monthly_power = gen_power.get('monthlyPowerList', [])
                    
                    for i, power in enumerate(monthly_power):
                        if i < 12:
                            monthly_totals[i] += power
                    
                    year_total += gen_power.get('yearPower', 0)
            
            row = {
                'projectId': project_id,
                'designId': design_id,
                'designName': design_name,
                'yearTotal': year_total,
            }
            
            for month_idx, total in enumerate(monthly_totals, 1):
                row[f'month{month_idx}'] = total
            
            rows.append(row)
    
    if rows:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f'✓ 月度发电量汇总: {output_path} ({len(rows)} 条记录)')


def main():
    base_dir = Path(__file__).parent
    sample_dir = base_dir / 'sample'
    output_dir = base_dir / 'output'
    
    print('=== 开始导出 CSV 文件 ===\n')
    
    # 加载所有 view/preview 文件（包含完整数据）
    view_files = [
        sample_dir / 'creat_battery_view.json',
        sample_dir / 'creat_newsys_preview.json',
    ]
    
    view_data = []
    for file_path in view_files:
        if file_path.exists():
            view_data.append(load_json(file_path))
    
    # 加载所有 payload 文件
    payload_files = [
        sample_dir / 'creat_battery_payload.json',
        sample_dir / 'creat_newsys_payload.json',
    ]
    
    payload_data = []
    for file_path in payload_files:
        if file_path.exists():
            payload_data.append(load_json(file_path))
    
    # 导出各类 CSV
    export_project_info(view_data, output_dir / '项目信息.csv')
    export_designs(view_data, output_dir / '设计方案.csv')
    export_panel_locations_from_payload(payload_data, output_dir / '面板位置_payload.csv')
    export_panel_locations_from_layout(view_data, output_dir / '面板位置与发电量_layout.csv')
    export_monthly_generation(view_data, output_dir / '月度发电量汇总.csv')
    
    print('\n=== CSV 导出完成 ===')


if __name__ == '__main__':
    main()
