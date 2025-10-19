# PVGIS 光伏性能模拟器

基于 PVGIS API 的光伏系统性能评估工具，支持系统性能计算、小时序列分析和地平线剖面查询。

## 功能特性

- ✅ **系统性能评估**（PVcalc）：计算年度/月度发电量、辐照、性能比
- ✅ **小时序列分析**（seriescalc）：逐小时辐照数据与可视化
- ✅ **地平线剖面**（printhorizon）：方位角-高度角曲线
- ✅ **深色主题 UI**：与 roi_calculator.html 风格统一
- ✅ **后端代理**：解决 CORS 限制，集成速率限制与缓存

## 快速开始

### 1. 安装依赖

```bash
cd PVGIS
npm install
```

### 2. 启动服务器

```bash
npm start
```

服务器将运行在 `http://localhost:3001`

### 3. 打开浏览器

访问 `http://localhost:3001/pvgis_simulator.html`

## 使用说明

### 系统性能（PVcalc）

1. 输入纬度和经度（或点击"填充示例"）
2. 设置系统参数：
   - 峰值功率（kWp）
   - 系统损耗（%）
   - 倾角和方位角（或勾选"自动优化"）
3. 点击"计算"查看结果

**输出**：
- 年度发电量、月均发电量、年度辐照、标准差
- 月度发电量柱状图

### 小时序列（seriescalc）

1. 输入纬度和经度
2. 设置倾角和方位角（可选）
3. 点击"计算"查看结果

**输出**：
- 最大值、平均值、最小值、总计
- 全年逐小时辐照折线图

### 地平线（printhorizon）

1. 输入纬度和经度
2. 点击"计算"查看结果

**输出**：
- 地平线剖面极坐标图

## 技术栈

### 前端
- 原生 HTML/CSS/JavaScript
- Chart.js 3.9.1（图表库）
- Inter 字体

### 后端
- Node.js + Express
- Axios（HTTP 客户端）
- 内存缓存（TTL: 1小时）
- 速率限制（~30 次/秒）

## API 端点

### POST /api/pvgis/proxy

代理 PVGIS API 请求

**请求体**：
```json
{
  "tool": "PVcalc",
  "params": {
    "lat": 39.9,
    "lon": 116.4,
    "peakpower": 1,
    "loss": 14,
    "outputformat": "json"
  }
}
```

**响应**：
```json
{
  "success": true,
  "data": { /* PVGIS 原始响应 */ },
  "cached": false,
  "timestamp": "2025-10-19T14:30:00Z"
}
```

### GET /api/health

健康检查

**响应**：
```json
{
  "status": "ok",
  "cacheSize": 5,
  "queueLength": 0
}
```

## 文件结构

```
PVGIS/
├── pvgis_simulator.html    # 前端页面（单文件）
├── proxy-server.js          # 后端代理服务器
├── package.json             # 依赖配置
├── pvgis.md                 # API 集成方案文档
├── simple_page_design.md    # 页面设计方案文档
└── README.md                # 本文件
```

## 注意事项

1. **CORS 限制**：PVGIS 不允许浏览器直接调用，必须通过后端代理
2. **速率限制**：PVGIS API 限制 30 次/秒，代理服务器已实现队列机制
3. **缓存策略**：相同参数的请求会命中缓存（1小时有效期）
4. **数据准确性**：PVGIS 数据基于卫星图像与气候模型，存在 ±5-10% 误差

## 开发模式

使用 nodemon 自动重启：

```bash
npm run dev
```

## 部署建议

### 生产环境

1. **后端**：部署到云服务器（AWS/Azure/阿里云）
2. **前端**：可与后端同域部署，或单独托管到 Netlify/Vercel
3. **缓存**：生产环境建议使用 Redis 替代内存缓存
4. **监控**：集成日志记录与错误追踪（Winston + Sentry）

### Docker 部署

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 3001
CMD ["node", "proxy-server.js"]
```

## 后续迭代

- [ ] 支持 CSV/EPW 导出
- [ ] 集成地图选点（Leaflet）
- [ ] 支持地址搜索（Geocoding API）
- [ ] 添加 MRcalc/DRcalc/tmy 工具
- [ ] 支持批量计算（多坐标）
- [ ] 参数预设保存（localStorage）

## 参考资源

- [PVGIS 官方文档](https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis_en)
- [PVGIS API 文档](https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/getting-started-pvgis/api-non-interactive-service_en)
- [Chart.js 文档](https://www.chartjs.org/docs/latest/)

## 许可证

MIT
