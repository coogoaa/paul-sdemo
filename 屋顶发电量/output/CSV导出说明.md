# CSV 导出说明

## 导出的 CSV 文件

已将 sample 目录的 JSON 数据按不同类别导出为 5 个 CSV 文件：

### 1. 项目信息.csv (2 条记录)
**说明**: 项目基本信息

**字段**:
- `id`: 项目 ID
- `projectCode`: 项目代码 (UUID)
- `address`: 地址
- `countryCode`: 国家代码
- `state`: 州/省
- `city`: 城市
- `siteZip`: 邮编
- `longitude`: 经度
- `latitude`: 纬度
- `type`: 项目类型 (1=新系统, 2=电池系统)
- `installerCode`: 安装商代码
- `mapLink`: 地图链接

**示例数据**:
| id | projectCode | address | state | city | type |
|----|-------------|---------|-------|------|------|
| 525 | f864a69d-... | 9RJ7+M54, Bundamba QLD 4304 | QLD | Bundamba | 2 |
| 524 | 31e97b81-... | 16 Barrett St, Orana WA 6330 | WA | Orana | 1 |

---

### 2. 设计方案.csv (6 条记录)
**说明**: 所有项目的设计方案详细信息

**字段**:
- `projectId`: 项目 ID
- `designId`: 设计方案 ID
- `designType`: 设计类型 (0=maxValue, 1=mostPopular, 2=customFit)
- `designName`: 设计名称
- `systemSize`: 系统大小 (kW)
- `upfrontInvestmentMin/Max`: 前期投资范围 ($)
- `upfrontInvestment`: 前期投资中值 ($)
- `subsidy`: 补贴金额 ($)
- `annualBillSavingsMin/Max`: 年度账单节省范围 ($)
- `annualBillSavings`: 年度账单节省中值 ($)
- `irr`: 内部收益率
- `paybackPeriodMin/Max`: 回本周期范围 (年)
- `paybackPeriod`: 回本周期中值 (年)
- `batteryCapacity`: 电池容量 (kWh)
- `selfConsumptionMin/Max`: 自用率范围 (0-1)
- `selfConsumption`: 自用率中值 (0-1)

**示例数据**:
| projectId | designName | systemSize | upfrontInvestment | paybackPeriod | batteryCapacity |
|-----------|------------|------------|-------------------|---------------|-----------------|
| 525 | customFit | 7.04 | 6858.76 | 3.75 | 11.11 |
| 525 | mostPopular | 7.04 | 8781.50 | 4.75 | 15.00 |
| 524 | customFit | 10.12 | 10752.21 | 5.25 | 8.03 |

---

### 3. 面板位置_payload.csv (10 条记录)
**说明**: 从 payload 文件提取的面板位置信息（原始布局数据）

**字段**:
- `projectId`: 项目 ID
- `gisTimeId`: GIS 时间 ID
- `gisDate`: GIS 日期
- `panelIndex`: 面板索引
- `aspect`: 朝向角度 (度)
- `slope`: 倾斜角度 (弧度)
- `startX/Y/Z`: 起始点坐标
- `endX/Y/Z`: 结束点坐标
- `centerX/Y/Z`: 中心点坐标
- `positionsCount`: 位置点数量

**用途**: 
- 3D 建模和可视化
- 面板布局分析
- 朝向和倾斜角度统计

---

### 4. 面板位置与发电量_layout.csv (9 条记录)
**说明**: 从设计方案的 layout 中提取的面板位置和发电量数据

**字段**:
- `projectId`: 项目 ID
- `designId`: 设计方案 ID
- `designName`: 设计名称
- `installPanelCount`: 安装面板总数
- `panelIndex`: 面板索引
- `aspect`: 朝向角度
- `slope`: 倾斜角度
- `positionsCount`: 位置点数量
- `calStatus`: 计算状态
- `yearPower`: 年度发电量 (kWh)
- `month1Power` ~ `month12Power`: 每月发电量 (kWh)

**用途**:
- 分析每个面板的发电性能
- 按朝向和倾斜角度分析发电效率
- 月度发电量趋势分析

**示例数据**:
| projectId | designName | panelIndex | aspect | yearPower | month1Power | month7Power |
|-----------|------------|------------|--------|-----------|-------------|-------------|
| 524 | customFit | 0 | 237.6 | 14.5 | 7.2 | 2.8 |

---

### 5. 月度发电量汇总.csv (3 条记录)
**说明**: 每个设计方案的月度发电量汇总（所有面板总和）

**字段**:
- `projectId`: 项目 ID
- `designId`: 设计方案 ID
- `designName`: 设计名称
- `yearTotal`: 年度总发电量 (kWh)
- `month1` ~ `month12`: 每月总发电量 (kWh)

**用途**:
- 快速查看项目整体发电量
- 季节性发电趋势分析
- 不同设计方案的发电量对比

**示例数据**:
| projectId | designName | yearTotal | month1 | month7 | month12 |
|-----------|------------|-----------|--------|--------|---------|
| 524 | customFit | 0 | 204.4 | 78.9 | 216.2 |

---

## 数据来源

### 源文件映射

| CSV 文件 | 数据来源 |
|----------|----------|
| 项目信息.csv | creat_battery_view.json, creat_newsys_preview.json |
| 设计方案.csv | creat_battery_view.json, creat_newsys_preview.json |
| 面板位置_payload.csv | creat_battery_payload.json, creat_newsys_payload.json |
| 面板位置与发电量_layout.csv | creat_newsys_preview.json (解析 layout 字段) |
| 月度发电量汇总.csv | creat_newsys_preview.json (汇总 layout 中的发电量) |

---

## 使用示例

### Python 读取
```python
import pandas as pd

# 读取项目信息
projects = pd.read_csv('项目信息.csv')
print(projects[['id', 'address', 'state', 'city']])

# 读取设计方案
designs = pd.read_csv('设计方案.csv')

# 按项目分组统计
summary = designs.groupby('projectId').agg({
    'systemSize': 'first',
    'paybackPeriod': 'mean',
    'batteryCapacity': 'mean'
})
print(summary)

# 读取月度发电量
monthly = pd.read_csv('月度发电量汇总.csv')

# 绘制发电量趋势
import matplotlib.pyplot as plt
months = [f'month{i}' for i in range(1, 13)]
for _, row in monthly.iterrows():
    plt.plot(range(1, 13), [row[m] for m in months], 
             label=f"{row['designName']}")
plt.legend()
plt.xlabel('月份')
plt.ylabel('发电量 (kWh)')
plt.show()
```

### Excel 分析
1. 打开 CSV 文件（使用 UTF-8 编码）
2. 创建数据透视表分析不同设计方案
3. 使用图表可视化月度发电量趋势
4. 计算投资回报率和财务指标

---

## 注意事项

1. **编码**: 所有 CSV 文件使用 UTF-8 编码
2. **数值精度**: 财务数据保留原始精度
3. **空值**: 某些字段可能为空（如 yearPower 在某些数据中为 0）
4. **坐标系统**: 位置坐标使用 3D 坐标系 (X, Y, Z)
5. **角度单位**: 
   - `aspect`: 度 (0-360)
   - `slope`: 弧度

---

## 生成脚本

脚本位置: `export_to_csv.py`

运行命令:
```bash
python3 export_to_csv.py
```

---

生成时间: 2025-11-07
