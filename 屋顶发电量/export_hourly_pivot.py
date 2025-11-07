#!/usr/bin/env python3
"""
将小时发电量数据转换为透视表格式
行: 小时 (1-24)
列: 月份 (1-12)
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


def export_hourly_pivot_by_panel(data_list, output_dir):
    """为每个设计方案的每个面板导出小时发电量透视表"""
    
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
                
                if not monthly_hourly or len(monthly_hourly) != 12:
                    continue
                
                # 创建透视表数据
                # 行: 24小时, 列: 12个月
                pivot_data = []
                
                # 表头行
                header = ['小时辐射/月'] + [f'{i} 月' for i in range(1, 13)]
                pivot_data.append(header)
                
                # 数据行 (24小时)
                for hour in range(24):
                    row = [str(hour + 1)]  # 小时从1开始
                    for month_idx in range(12):
                        power = monthly_hourly[month_idx][hour]
                        row.append(str(power))
                    pivot_data.append(row)
                
                # 写入CSV文件
                filename = f'hourly_pivot_project{project_id}_{design_name}_panel{panel_idx}.csv'
                output_path = output_dir / filename
                
                with open(output_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(pivot_data)
                
                print(f'✓ {filename}')


def export_hourly_pivot_total(data_list, output_dir):
    """导出汇总的小时发电量透视表（所有面板求和）"""
    
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
            
            # 初始化汇总数组 (12月 × 24小时)
            total_hourly = [[0.0 for _ in range(24)] for _ in range(12)]
            
            # 累加所有面板的发电量
            for panel in layout['panelLocationInfos']:
                if 'generationPowerVO' not in panel:
                    continue
                
                gen_power = panel['generationPowerVO']
                monthly_hourly = gen_power.get('monthlyHourlyPowerList', [])
                
                if not monthly_hourly or len(monthly_hourly) != 12:
                    continue
                
                for month_idx in range(12):
                    for hour in range(24):
                        total_hourly[month_idx][hour] += monthly_hourly[month_idx][hour]
            
            # 创建透视表数据
            pivot_data = []
            
            # 表头行
            header = ['小时辐射/月'] + [f'{i} 月' for i in range(1, 13)]
            pivot_data.append(header)
            
            # 数据行 (24小时)
            for hour in range(24):
                row = [str(hour + 1)]  # 小时从1开始
                for month_idx in range(12):
                    power = total_hourly[month_idx][hour]
                    row.append(str(power))
                pivot_data.append(row)
            
            # 写入CSV文件
            filename = f'hourly_pivot_project{project_id}_{design_name}_total.csv'
            output_path = output_dir / filename
            
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(pivot_data)
            
            print(f'✓ {filename} (所有面板汇总)')


def main():
    base_dir = Path(__file__).parent
    sample_dir = base_dir / 'sample'
    output_dir = base_dir / 'output'
    
    print('=== 开始导出小时发电量透视表 ===\n')
    
    # 加载包含 layout 的文件
    view_files = [
        sample_dir / 'creat_battery_view.json',
        sample_dir / 'creat_newsys_preview.json',
    ]
    
    view_data = []
    for file_path in view_files:
        if file_path.exists():
            view_data.append(load_json(file_path))
    
    print('按面板导出:')
    export_hourly_pivot_by_panel(view_data, output_dir)
    
    print('\n汇总导出:')
    export_hourly_pivot_total(view_data, output_dir)
    
    print('\n=== 小时发电量透视表导出完成 ===')


if __name__ == '__main__':
    main()
