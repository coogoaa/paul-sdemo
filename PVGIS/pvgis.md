# PVGIS 非交互式 API 集成方案

> 基于 [PVGIS API 官方文档](https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/getting-started-pvgis/api-non-interactive-service_en)  
> 更新时间：2025-10-19

## 一、API 基础信息

### 1.1 入口版本
- **推荐版本**：`https://re.jrc.ec.europa.eu/api/v5_3/tool_name?param1=value1&...`
- **旧版本**：`https://re.jrc.ec.europa.eu/api/v5_2/...`（限期支持）
- **HTTP 方法**：仅支持 `GET`
- **速率限制**：30 次/秒/IP；超限返回 `429 Too Many Requests`
- **过载处理**：服务器会短暂停顿重试（150-200ms），超时返回 `529 Site is overloaded`

### 1.2 可用工具列表
| 工具名 | 用途 | 最小必填参数 |
|--------|------|-------------|
| `PVcalc` | 并网/跟踪系统性能评估 | `lat`, `lon`, `peakpower`, `loss` |
| `SHScalc` | 离网系统设计 | `lat`, `lon`, `peakpower`, `batterysize`, `consumptionday`, `cutoff` |
| `MRcalc` | 月度辐照统计 | `lat`, `lon`, 至少一个输出项（如 `horirrad=1`） |
| `DRcalc` | 日辐照统计 | `lat`, `lon`, `month`, 至少一个输出项（如 `global=1`） |
| `seriescalc` | 小时序列辐照/发电 | `lat`, `lon` |
| `tmy` | 典型气象年数据 | `lat`, `lon` |
| `printhorizon` | 地平线剖面 | `lat`, `lon` |

### 1.3 通用输出控制
- **outputformat**：
  - `json`（推荐，便于集成）
  - `csv`（带元数据）
  - `basic`（纯数据，无元数据）
  - `epw`（仅 `tmy` 支持，Energy Plus 格式）
- **browser**：
  - `browser=0`：流式输出
  - `browser=1`：文件下载

### 1.4 CORS 约束
**重要**：PVGIS 不允许浏览器直接 AJAX 调用（CORS 策略限制），必须通过后端代理转发。

---

## 二、核心工具参数详解

### 2.1 PVcalc（并网/跟踪系统）

#### 必填参数
- `lat`：纬度（-90 ~ 90）
- `lon`：经度（-180 ~ 180）
- `peakpower`：系统峰值功率（kWp）
- `loss`：系统损耗（%，包括线损、逆变器损耗、温度损耗等）

#### 重要可选参数（互斥关系）
- **固定倾角系统**：
  - `angle`：倾角（0-90°）
  - `aspect`：方位角（-180 ~ 180°，0=正南，-90=东，90=西）
  - `optimalinclination=1`：自动优化倾角（忽略 `angle`）
  - `optimalangles=1`：自动优化倾角+方位（忽略 `angle` 和 `aspect`）

- **跟踪系统**：
  - `vertical_axis=1`：垂直轴跟踪
  - `verticalaxisangle`：垂直轴倾角
  - `vertical_optimum=1`：自动优化垂直轴倾角
  - `inclined_axis=1`：倾斜轴跟踪
  - `inclinedaxisangle`：倾斜轴倾角
  - `inclined_optimum=1`：自动优化倾斜轴倾角

#### 示例请求
```
https://re.jrc.ec.europa.eu/api/v5_3/PVcalc?lat=45&lon=8&peakpower=1&loss=14&outputformat=json
```

---

### 2.2 seriescalc（小时序列）

#### 必填参数
- `lat`：纬度
- `lon`：经度

#### 可选参数
- `angle`：倾角（默认 0，水平面）
- `aspect`：方位角（默认 0，正南）
- `startyear`：起始年份
- `endyear`：结束年份
- `pvcalculation=1`：计算 PV 发电量（需配合 `peakpower`、`loss` 等参数）

#### 示例请求
```
https://re.jrc.ec.europa.eu/api/v5_3/seriescalc?lat=45&lon=8&outputformat=json
```

---

### 2.3 printhorizon（地平线剖面）

#### 必填参数
- `lat`：纬度
- `lon`：经度

#### 示例请求
```
https://re.jrc.ec.europa.eu/api/v5_3/printhorizon?lat=45&lon=8&outputformat=json
```

---

## 三、简单页面方案设计

### 3.1 范围确认
- ✅ **核心工具**：`PVcalc` + `seriescalc` + `printhorizon`
- ✅ **地理输入**：手动输入经纬度（暂不集成地图/地址搜索）
- ❌ **下载能力**：暂不支持 CSV/EPW 导出（后续迭代）
- ✅ **UI 风格**：与 `roi_calculator.html` 保持一致（深色主题、卡片布局、Inter 字体）

### 3.2 页面结构

#### 布局框架
```
┌─────────────────────────────────────────┐
│  PVGIS 光伏性能模拟器  v1.0             │
├─────────────────────────────────────────┤
│  [Tab: 系统性能] [小时序列] [地平线]    │
├─────────────────────────────────────────┤
│  通用输入区                              │
│  ┌─────────────────────────────────┐   │
│  │ 纬度 lat  │ 经度 lon  │ [计算] │   │
│  └─────────────────────────────────┘   │
├─────────────────────────────────────────┤
│  工具专属输入区（根据 Tab 动态切换）     │
│  ┌─────────────────────────────────┐   │
│  │ [PVcalc]: 峰值功率、损耗、倾角等│   │
│  │ [seriescalc]: 年份范围、倾角等  │   │
│  │ [printhorizon]: 无额外参数      │   │
│  └─────────────────────────────────┘   │
├─────────────────────────────────────────┤
│  结果展示区                              │
│  ┌─────────────────────────────────┐   │
│  │ [PVcalc]: KPI卡片 + 月度柱状图  │   │
│  │ [seriescalc]: 小时折线图        │   │
│  │ [printhorizon]: 极坐标地平线图  │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

#### Tab 1: 系统性能（PVcalc）
**输入字段**：
- 通用：`lat`, `lon`
- 专属：`peakpower`（kWp）, `loss`（%）, `angle`（°）, `aspect`（°）
- 快捷选项：☑ `optimalangles`（自动优化倾角+方位）

**输出展示**：
- **KPI 卡片**（4个）：
  - 年度发电量（kWh）
  - 月均发电量（kWh）
  - 年度辐照（kWh/m²）
  - 性能比 PR（%）
- **月度柱状图**：横轴=月份，纵轴=发电量（kWh）
- **详情表格**（可折叠）：月度明细数据

#### Tab 2: 小时序列（seriescalc）
**输入字段**：
- 通用：`lat`, `lon`
- 专属：`angle`（°）, `aspect`（°）
- 可选：`startyear`, `endyear`（默认最近一年）

**输出展示**：
- **小时折线图**：
  - 横轴：时间（日期-小时）
  - 纵轴：辐照（W/m²）或发电量（W）
  - 支持缩放、tooltip 显示详细数值
- **统计摘要**：最大值、最小值、平均值、总计

#### Tab 3: 地平线（printhorizon）
**输入字段**：
- 通用：`lat`, `lon`

**输出展示**：
- **极坐标地平线图**：
  - 径向轴：方位角（0-360°）
  - 角度轴：高度角（0-90°）
  - 曲线：地平线轮廓
- **数据表格**（可折叠）：方位角-高度角数值列表

### 3.3 UI 样式规范（继承 roi_calculator.html）

#### 颜色方案
```css
背景色：#0b1220（深蓝黑）
卡片背景：#0f172a（深灰蓝）
边框：#1f2937（中灰）
输入框背景：#0b1220
输入框边框：#334155
文字主色：#e5e7eb（浅灰）
文字次色：#94a3b8（中灰）
标题色：#f9fafb（近白）
按钮色：#2563eb（蓝色）
成功色：#10b981（绿色）
警告色：#ef4444（红色）
```

#### 组件样式
- **卡片**：`border-radius: 12px`, `padding: 20px`
- **输入框**：`border-radius: 8px`, `padding: 10px 12px`, `font-size: 14px`
- **按钮**：`border-radius: 8px`, `padding: 10px 14px`, `font-weight: 600`
- **KPI 卡片**：`border-radius: 10px`, `padding: 14px`
  - 标题：`font-size: 12px`, `color: #94a3b8`
  - 数值：`font-size: 22px`, `font-weight: 700`, `color: #f8fafc`

### 3.4 后端代理架构

#### 端点设计
```
POST /api/pvgis/proxy
Content-Type: application/json

{
  "tool": "PVcalc",
  "params": {
    "lat": 45,
    "lon": 8,
    "peakpower": 1,
    "loss": 14,
    "outputformat": "json"
  }
}
```

#### 响应格式
```json
{
  "success": true,
  "data": { /* PVGIS 原始 JSON 响应 */ },
  "cached": false,
  "timestamp": "2025-10-19T14:12:00Z"
}
```

#### 治理策略
- **速率限制**：本地队列，确保 ≤30 次/秒
- **重试机制**：
  - `429`：等待 1 秒后重试（最多 3 次）
  - `529`：指数退避（1s, 2s, 4s）
- **缓存**：
  - 键：`tool + JSON.stringify(params)`
  - TTL：1 小时（辐照数据变化缓慢）
- **错误处理**：
  - 参数校验失败：返回 `400` + 详细错误信息
  - PVGIS 服务异常：返回 `502` + 原始错误

---

## 四、技术栈建议

### 后端
- **语言**：Node.js (Express) 或 Python (Flask/FastAPI)
- **缓存**：Redis（生产）或内存缓存（开发）
- **限流**：`express-rate-limit` 或 `slowapi`
- **HTTP 客户端**：`axios` 或 `requests`

### 前端
- **框架**：原生 HTML/CSS/JS（与 roi_calculator.html 保持一致）
- **图表**：Chart.js 3.x
- **HTTP 客户端**：`fetch` API
- **样式**：内联 CSS（便于单文件部署）

---

## 五、开发计划

### 阶段 1：后端代理（优先级：高）
- [ ] 搭建 Express/Flask 代理服务
- [ ] 实现参数校验与转发逻辑
- [ ] 集成速率限制（30 次/秒）
- [ ] 实现缓存机制（Redis/内存）
- [ ] 错误处理与重试策略
- [ ] 单元测试（覆盖率 >80%）

### 阶段 2：前端页面（优先级：高）
- [ ] 创建 HTML 框架（继承 roi_calculator.html 样式）
- [ ] 实现 Tab 切换与表单动态渲染
- [ ] 集成 Chart.js 并实现三类图表
- [ ] 实现参数校验与错误提示
- [ ] 实现 Loading 状态与结果展示
- [ ] 响应式布局适配（移动端）

### 阶段 3：联调与优化（优先级：中）
- [ ] 使用真实坐标测试三个工具
- [ ] 性能优化（图表渲染、数据处理）
- [ ] 用户体验优化（tooltip、动画）
- [ ] 错误场景测试（无效坐标、服务超时等）

### 阶段 4：功能扩展（优先级：低）
- [ ] 支持 CSV/EPW 导出
- [ ] 集成地图选点（Leaflet/Mapbox）
- [ ] 支持地址搜索（Geocoding API）
- [ ] 支持 MRcalc/DRcalc/tmy 工具
- [ ] 支持批量计算（多坐标）

---

## 六、快速测试命令

```bash
# 测试 PVcalc
curl "https://re.jrc.ec.europa.eu/api/v5_3/PVcalc?lat=45&lon=8&peakpower=1&loss=14&outputformat=json"

# 测试 seriescalc
curl "https://re.jrc.ec.europa.eu/api/v5_3/seriescalc?lat=45&lon=8&outputformat=json"

# 测试 printhorizon
curl "https://re.jrc.ec.europa.eu/api/v5_3/printhorizon?lat=45&lon=8&outputformat=json"
```

---

## 七、参考资源

- [PVGIS 官方文档](https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis_en)
- [PVGIS API 文档](https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/getting-started-pvgis/api-non-interactive-service_en)
- [Chart.js 文档](https://www.chartjs.org/docs/latest/)
- [Express Rate Limit](https://github.com/express-rate-limit/express-rate-limit)
