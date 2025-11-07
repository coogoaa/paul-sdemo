# JSON 解析结果说明

本目录包含了从 `sample` 目录解析的 JSON 文件。

## 文件列表

### 1. parsed_creat_battery_payload.json
- **来源**: `sample/creat_battery_payload.json`
- **说明**: 电池系统创建的 payload 数据
- **主要字段**:
  - `projectId`: 项目 ID (525)
  - `gisTimeId`: GIS 时间 ID
  - `gisDate`: GIS 日期
  - `mapLink`: 地图链接
  - `panelLocationInfos`: 面板位置信息数组
    - `positions`: 位置坐标数组
    - `aspect`: 朝向角度
    - `slope`: 倾斜角度
    - `start`: 起始点坐标
    - `end`: 结束点坐标
    - `center`: 中心点坐标
  - `gisMapType`: 地图类型 (metromap)

### 2. parsed_creat_battery_view.json
- **来源**: `sample/creat_battery_view.json`
- **说明**: 电池系统视图数据
- **主要字段**:
  - `code`: 响应代码 (200)
  - `data`: 数据对象
    - `id`: 项目 ID
    - `projectCode`: 项目代码 (UUID)
    - `address`: 地址
    - `countryCode`: 国家代码 (AU)
    - `state`: 州 (QLD)
    - `city`: 城市
    - `longitude`: 经度
    - `latitude`: 纬度
    - `rowLayout`: 行布局（JSON 字符串）
    - **`rowLayout_parsed`**: ✨ **已解析的行布局对象**
    - `designs`: 设计方案数组
      - `designType`: 设计类型 (0=maxValue, 1=mostPopular, 2=customFit)
      - `systemSize`: 系统大小 (kW)
      - `upfrontInvestment`: 前期投资
      - `subsidy`: 补贴
      - `annualBillSavings`: 年度账单节省
      - `irr`: 内部收益率
      - `paybackPeriod`: 回本周期
      - `batteryCapacity`: 电池容量
      - `selfConsumption`: 自用率

### 3. parsed_creat_newsys_payload.json
- **来源**: `sample/creat_newsys_payload.json`
- **说明**: 新系统创建的 payload 数据
- **结构**: 与 `creat_battery_payload.json` 类似
- **项目信息**: 
  - 项目 ID: 524
  - 地点: 16 Barrett St, Orana WA 6330, Australia

### 4. parsed_creat_newsys_preview.json ⭐
- **来源**: `sample/creat_newsys_preview.json`
- **说明**: 新系统预览数据（**包含嵌套 layout 解析**）
- **特殊处理**:
  - ✨ **`rowLayout_parsed`**: 解析后的行布局对象
  - ✨ **`designs[].layout_parsed`**: 每个设计方案的 layout 字段已被解析为对象
  
- **嵌套 layout 结构**:
  ```json
  {
    "projectId": 524,
    "gisTimeId": "4911",
    "gisDate": "20240327",
    "installPanelCount": 23,
    "panelLocationInfos": [
      {
        "positions": [...],
        "aspect": 237.60006713867188,
        "slope": 0.40142542123794556,
        "generationPowerVO": {
          "calStatus": true,
          "monthlyHourlyPowerList": [...],
          "monthlyPowerList": [...],
          "yearPower": 14.5,
          "dailyPowerList": [...]
        }
      }
    ]
  }
  ```

## 解析说明

### 嵌套 JSON 字符串处理

原始文件中的某些字段（如 `rowLayout` 和 `layout`）包含 JSON 字符串，已被解析为对象：

- **原始格式**: `"layout": "{\"projectId\":524,...}"`
- **解析后**: `"layout_parsed": { "projectId": 524, ... }`

### 主要改进

1. **可读性提升**: 嵌套的 JSON 字符串已被解析为结构化对象
2. **易于访问**: 可以直接访问嵌套字段，无需再次 JSON 解析
3. **保留原始数据**: 原始的字符串字段仍然保留，新增 `_parsed` 后缀字段

## 使用示例

```python
import json

# 读取解析后的文件
with open('parsed_creat_newsys_preview.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 直接访问解析后的 layout
for design in data['data']['designs']:
    if 'layout_parsed' in design:
        layout = design['layout_parsed']
        print(f"面板数量: {layout['installPanelCount']}")
        print(f"年发电量: {layout['panelLocationInfos'][0]['generationPowerVO']['yearPower']}")
```

## 字段说明

### 设计类型 (designType)
- `0`: maxValue - 最大价值方案
- `1`: mostPopular - 最受欢迎方案
- `2`: customFit - 定制方案

### 发电量数据 (generationPowerVO)
- `monthlyHourlyPowerList`: 每月每小时发电量（12个月 × 24小时）
- `monthlyPowerList`: 每月总发电量
- `yearPower`: 年度总发电量
- `dailyPowerList`: 每日发电量（365天）

### 财务指标
- `upfrontInvestment`: 前期投资金额
- `subsidy`: 政府补贴
- `annualBillSavings`: 年度电费节省
- `irr`: 内部收益率
- `paybackPeriod`: 回本周期（年）
- `selfConsumption`: 自用率（0-1之间）

## 生成时间

解析脚本: `parse_samples.py`
