#!/usr/bin/env python3
"""
解析 sample 目录下的 JSON 文件
对于 creat_newsys_preview.json，会解析嵌套的 layout 字段
"""

import json
import os
from pathlib import Path


def parse_json_file(file_path):
    """读取并解析 JSON 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_nested_layout(layout_str):
    """解析嵌套的 layout JSON 字符串"""
    if not layout_str:
        return None
    try:
        return json.loads(layout_str)
    except json.JSONDecodeError:
        return None


def process_creat_newsys_preview(data):
    """处理 creat_newsys_preview.json，解析嵌套的 layout"""
    if 'data' in data and 'designs' in data['data']:
        for design in data['data']['designs']:
            if 'layout' in design and design['layout']:
                # 解析嵌套的 layout JSON 字符串
                design['layout_parsed'] = parse_nested_layout(design['layout'])
    
    # 同时解析 rowLayout 字段
    if 'data' in data and 'rowLayout' in data['data']:
        data['data']['rowLayout_parsed'] = parse_nested_layout(data['data']['rowLayout'])
    
    return data


def process_creat_battery_view(data):
    """处理 creat_battery_view.json，解析嵌套的 rowLayout"""
    if 'data' in data and 'rowLayout' in data['data']:
        data['data']['rowLayout_parsed'] = parse_nested_layout(data['data']['rowLayout'])
    return data


def main():
    # 定义路径
    base_dir = Path(__file__).parent
    sample_dir = base_dir / 'sample'
    output_dir = base_dir / 'output'
    
    # 创建输出目录
    output_dir.mkdir(exist_ok=True)
    
    # 定义要处理的文件
    files_to_process = [
        ('creat_battery_payload.json', None),
        ('creat_battery_view.json', process_creat_battery_view),
        ('creat_newsys_payload.json', None),
        ('creat_newsys_preview.json', process_creat_newsys_preview),
    ]
    
    # 处理每个文件
    for filename, processor in files_to_process:
        input_path = sample_dir / filename
        output_path = output_dir / f'parsed_{filename}'
        
        print(f'正在处理: {filename}')
        
        # 读取 JSON
        data = parse_json_file(input_path)
        
        # 如果有特定的处理器，则应用
        if processor:
            data = processor(data)
        
        # 写入输出文件（格式化输出，便于阅读）
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f'✓ 已输出到: {output_path}')
    
    print('\n所有文件处理完成！')


if __name__ == '__main__':
    main()
