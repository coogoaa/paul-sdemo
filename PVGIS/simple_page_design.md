# PVGIS 简单页面设计方案

> 基于 roi_calculator.html 风格的单文件实现方案  
> 更新时间：2025-10-19

## 一、页面概览

### 设计原则
- **单文件部署**：HTML + CSS + JS 全部内联，便于快速部署
- **风格统一**：完全继承 `roi_calculator.html` 的深色主题与组件样式
- **渐进增强**：优先实现核心功能，后续迭代扩展
- **用户友好**：提供示例数据、实时校验、清晰的错误提示

### 功能范围
- ✅ 三个核心工具：PVcalc、seriescalc、printhorizon
- ✅ Tab 切换界面
- ✅ 参数输入与校验
- ✅ 图表可视化（Chart.js）
- ✅ Loading 状态与错误处理
- ❌ 暂不支持：CSV 导出、地图选点、地址搜索

---

## 二、页面结构设计

### 2.1 HTML 结构

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PVGIS 光伏性能模拟器</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
  <style>/* 样式代码 */</style>
</head>
<body>
  <div class="wrap">
    <h1>PVGIS 光伏性能模拟器 <span class="version">v1.0</span></h1>
    
    <!-- Tab 导航 -->
    <div class="tabs">
      <button class="tab active" data-tool="PVcalc">系统性能</button>
      <button class="tab" data-tool="seriescalc">小时序列</button>
      <button class="tab" data-tool="printhorizon">地平线</button>
    </div>
    
    <div class="card">
      <!-- 通用输入区 -->
      <div class="section">
        <h2>位置信息</h2>
        <div class="row">
          <div class="col-3">
            <label>纬度 (lat)</label>
            <input id="lat" type="number" step="0.01" placeholder="例如: 39.9" />
            <span class="hint">范围: -90 ~ 90</span>
          </div>
          <div class="col-3">
            <label>经度 (lon)</label>
            <input id="lon" type="number" step="0.01" placeholder="例如: 116.4" />
            <span class="hint">范围: -180 ~ 180</span>
          </div>
          <div class="col-3">
            <button class="btn-example">填充示例（北京）</button>
          </div>
        </div>
      </div>
      
      <div class="sep"></div>
      
      <!-- 工具专属输入区（动态切换） -->
      <div class="section tool-params" id="params-PVcalc">
        <h2>系统参数</h2>
        <!-- PVcalc 参数 -->
      </div>
      
      <div class="section tool-params hidden" id="params-seriescalc">
        <h2>序列参数</h2>
        <!-- seriescalc 参数 -->
      </div>
      
      <div class="section tool-params hidden" id="params-printhorizon">
        <h2>地平线参数</h2>
        <p class="muted">此工具无需额外参数</p>
      </div>
      
      <div class="sep"></div>
      
      <!-- 计算按钮 -->
      <div class="actions">
        <button class="btn" id="calculate">
          <span class="btn-text">计算</span>
          <span class="btn-loading hidden">计算中...</span>
        </button>
        <span class="muted">点击"计算"后将调用 PVGIS API 并展示结果</span>
      </div>
      
      <div class="sep"></div>
      
      <!-- 结果展示区 -->
      <div class="results hidden" id="results">
        <!-- 动态渲染结果 -->
      </div>
      
      <!-- 错误提示区 -->
      <div class="error hidden" id="error">
        <strong>错误：</strong><span id="error-message"></span>
      </div>
    </div>
    
    <div class="footer">
      <strong>数据来源：</strong>PVGIS (European Commission Joint Research Centre)<br>
      <strong>免责声明：</strong>本工具提供的数据仅供参考，实际发电量可能因现场条件而异
    </div>
  </div>
  
  <script>/* JavaScript 代码 */</script>
</body>
</html>
```

### 2.2 CSS 样式（继承 roi_calculator.html）

```css
body {
  font-family: Inter, system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial;
  margin: 0;
  padding: 24px;
  background: #0b1220;
  color: #e5e7eb;
}

h1 {
  font-size: 20px;
  margin: 0 0 16px;
  color: #f9fafb;
}

.version {
  font-size: 12px;
  color: #64748b;
}

.wrap {
  max-width: 1100px;
  margin: 0 auto;
}

.card {
  background: #0f172a;
  border: 1px solid #1f2937;
  border-radius: 12px;
  padding: 20px;
}

/* Tab 导航 */
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.tab {
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 10px 16px;
  color: #94a3b8;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.tab:hover {
  background: #1e293b;
  border-color: #475569;
}

.tab.active {
  background: #2563eb;
  border-color: #2563eb;
  color: #fff;
}

/* 表单布局 */
.row {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 12px;
}

.col-2 { grid-column: span 2; }
.col-3 { grid-column: span 3; }
.col-6 { grid-column: span 6; }

label {
  display: block;
  font-size: 12px;
  color: #94a3b8;
  margin: 0 0 6px;
}

input, select {
  width: 100%;
  border: 1px solid #334155;
  background: #0b1220;
  color: #e5e7eb;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
}

.hint {
  display: block;
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

/* 按钮 */
.btn {
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 14px;
  font-weight: 600;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.btn:hover {
  background: #1d4ed8;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-example {
  background: #0b1220;
  border: 1px solid #334155;
  color: #94a3b8;
  border-radius: 8px;
  padding: 10px 14px;
  cursor: pointer;
  font-size: 12px;
}

/* KPI 卡片 */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-top: 12px;
}

.kpi {
  background: #0b1220;
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 14px;
}

.kpi h3 {
  margin: 0 0 6px;
  font-size: 12px;
  color: #94a3b8;
}

.kpi .value {
  font-size: 22px;
  font-weight: 700;
  color: #f8fafc;
}

/* 图表容器 */
.chart-container {
  position: relative;
  height: 300px;
  margin-top: 16px;
}

/* 工具类 */
.sep {
  height: 1px;
  background: #1f2937;
  margin: 16px 0;
}

.hidden {
  display: none !important;
}

.muted {
  color: #94a3b8;
  font-size: 12px;
}

.error {
  background: #7f1d1d;
  border: 1px solid #991b1b;
  border-radius: 8px;
  padding: 12px;
  color: #fecaca;
  margin-top: 16px;
}

.footer {
  margin-top: 16px;
  color: #64748b;
  font-size: 12px;
}
```

---

## 三、JavaScript 实现要点

### 3.1 状态管理

```javascript
const state = {
  currentTool: 'PVcalc',
  params: {
    common: { lat: null, lon: null },
    PVcalc: { peakpower: 1, loss: 14, angle: 35, aspect: 0, optimalangles: false },
    seriescalc: { angle: 0, aspect: 0 },
    printhorizon: {}
  },
  results: {},
  loading: false,
  error: null
};
```

### 3.2 Tab 切换逻辑

```javascript
function switchTool(toolName) {
  // 更新状态
  state.currentTool = toolName;
  
  // 更新 Tab 样式
  document.querySelectorAll('.tab').forEach(tab => {
    tab.classList.toggle('active', tab.dataset.tool === toolName);
  });
  
  // 切换参数区
  document.querySelectorAll('.tool-params').forEach(section => {
    section.classList.toggle('hidden', section.id !== `params-${toolName}`);
  });
  
  // 清空结果
  document.getElementById('results').classList.add('hidden');
  document.getElementById('error').classList.add('hidden');
}
```

### 3.3 参数校验

```javascript
function validateParams(tool, params) {
  const { lat, lon } = params.common;
  
  // 通用校验
  if (lat === null || lon === null) {
    return { valid: false, message: '请输入纬度和经度' };
  }
  if (lat < -90 || lat > 90) {
    return { valid: false, message: '纬度范围: -90 ~ 90' };
  }
  if (lon < -180 || lon > 180) {
    return { valid: false, message: '经度范围: -180 ~ 180' };
  }
  
  // 工具专属校验
  if (tool === 'PVcalc') {
    const { peakpower, loss } = params.PVcalc;
    if (peakpower <= 0) {
      return { valid: false, message: '峰值功率必须大于 0' };
    }
    if (loss < 0 || loss > 100) {
      return { valid: false, message: '系统损耗范围: 0 ~ 100%' };
    }
  }
  
  return { valid: true };
}
```

### 3.4 API 调用（通过后端代理）

```javascript
async function callPVGIS(tool, params) {
  const response = await fetch('/api/pvgis/proxy', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tool, params })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || '请求失败');
  }
  
  return await response.json();
}
```

### 3.5 结果渲染

#### PVcalc 结果
```javascript
function renderPVcalcResults(data) {
  const totals = data.outputs.totals.fixed;
  const monthly = data.outputs.monthly.fixed;
  
  // 渲染 KPI 卡片
  const kpiHTML = `
    <div class="kpi-grid">
      <div class="kpi">
        <h3>年度发电量</h3>
        <div class="value">${totals.E_y.toFixed(0)} kWh</div>
      </div>
      <div class="kpi">
        <h3>月均发电量</h3>
        <div class="value">${totals.E_m.toFixed(0)} kWh</div>
      </div>
      <div class="kpi">
        <h3>年度辐照</h3>
        <div class="value">${totals['H(i)_y'].toFixed(0)} kWh/m²</div>
      </div>
      <div class="kpi">
        <h3>性能比 PR</h3>
        <div class="value">${(totals.E_y / (totals['H(i)_y'] * state.params.PVcalc.peakpower) * 100).toFixed(1)}%</div>
      </div>
    </div>
  `;
  
  // 渲染月度柱状图
  const chartHTML = `
    <div class="chart-container">
      <canvas id="monthlyChart"></canvas>
    </div>
  `;
  
  document.getElementById('results').innerHTML = kpiHTML + chartHTML;
  document.getElementById('results').classList.remove('hidden');
  
  // 绘制图表
  const ctx = document.getElementById('monthlyChart').getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: monthly.map(m => `${m.month}月`),
      datasets: [{
        label: '月度发电量 (kWh)',
        data: monthly.map(m => m.E_m),
        backgroundColor: '#2563eb'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
}
```

#### seriescalc 结果
```javascript
function renderSeriesResults(data) {
  const hourly = data.outputs.hourly;
  
  // 提取时间和辐照数据
  const times = hourly.map(h => h.time);
  const radiation = hourly.map(h => h['G(i)']);
  
  const chartHTML = `
    <h2>小时辐照序列</h2>
    <div class="chart-container" style="height: 400px;">
      <canvas id="seriesChart"></canvas>
    </div>
  `;
  
  document.getElementById('results').innerHTML = chartHTML;
  document.getElementById('results').classList.remove('hidden');
  
  // 绘制折线图
  const ctx = document.getElementById('seriesChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: times,
      datasets: [{
        label: '辐照 (W/m²)',
        data: radiation,
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37, 99, 235, 0.1)',
        fill: true,
        pointRadius: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true }
      },
      scales: {
        x: { display: false },
        y: { beginAtZero: true }
      }
    }
  });
}
```

#### printhorizon 结果
```javascript
function renderHorizonResults(data) {
  const profile = data.outputs.horizon_profile;
  
  const chartHTML = `
    <h2>地平线剖面</h2>
    <div class="chart-container" style="height: 400px;">
      <canvas id="horizonChart"></canvas>
    </div>
  `;
  
  document.getElementById('results').innerHTML = chartHTML;
  document.getElementById('results').classList.remove('hidden');
  
  // 绘制极坐标图
  const ctx = document.getElementById('horizonChart').getContext('2d');
  new Chart(ctx, {
    type: 'radar',
    data: {
      labels: profile.map(p => `${p.A}°`),
      datasets: [{
        label: '高度角 (°)',
        data: profile.map(p => p.H_hor),
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37, 99, 235, 0.2)'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          beginAtZero: true,
          max: 90
        }
      }
    }
  });
}
```

---

## 四、用户体验优化

### 4.1 示例数据填充
```javascript
const examples = {
  '北京': { lat: 39.9, lon: 116.4 },
  '上海': { lat: 31.2, lon: 121.5 },
  '广州': { lat: 23.1, lon: 113.3 },
  '成都': { lat: 30.7, lon: 104.1 }
};

document.querySelector('.btn-example').addEventListener('click', () => {
  document.getElementById('lat').value = examples['北京'].lat;
  document.getElementById('lon').value = examples['北京'].lon;
});
```

### 4.2 Loading 状态
```javascript
function setLoading(loading) {
  state.loading = loading;
  const btn = document.getElementById('calculate');
  btn.disabled = loading;
  btn.querySelector('.btn-text').classList.toggle('hidden', loading);
  btn.querySelector('.btn-loading').classList.toggle('hidden', !loading);
}
```

### 4.3 错误提示
```javascript
function showError(message) {
  const errorDiv = document.getElementById('error');
  document.getElementById('error-message').textContent = message;
  errorDiv.classList.remove('hidden');
  
  // 3秒后自动隐藏
  setTimeout(() => {
    errorDiv.classList.add('hidden');
  }, 3000);
}
```

---

## 五、部署方案

### 5.1 前端部署
- **静态托管**：将 HTML 文件上传至 Netlify/Vercel
- **同域部署**：放在后端服务的 `public/` 目录

### 5.2 后端代理（Node.js + Express 示例）
```javascript
const express = require('express');
const axios = require('axios');
const app = express();

app.use(express.json());

app.post('/api/pvgis/proxy', async (req, res) => {
  const { tool, params } = req.body;
  
  try {
    // 构建 PVGIS URL
    const baseURL = 'https://re.jrc.ec.europa.eu/api/v5_3';
    const queryString = new URLSearchParams(params).toString();
    const url = `${baseURL}/${tool}?${queryString}`;
    
    // 调用 PVGIS API
    const response = await axios.get(url, { timeout: 30000 });
    
    res.json({
      success: true,
      data: response.data,
      cached: false,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(502).json({
      success: false,
      message: error.message
    });
  }
});

app.listen(3000, () => {
  console.log('PVGIS proxy running on port 3000');
});
```

---

## 六、测试清单

### 功能测试
- [ ] Tab 切换正常
- [ ] 参数校验生效
- [ ] 示例数据填充正确
- [ ] PVcalc 结果展示正常
- [ ] seriescalc 图表渲染正确
- [ ] printhorizon 极坐标图显示正常
- [ ] Loading 状态切换正常
- [ ] 错误提示显示正确

### 边界测试
- [ ] 无效经纬度（超出范围）
- [ ] 空参数提交
- [ ] 网络超时
- [ ] PVGIS 服务返回错误
- [ ] 极端数据（极地、赤道）

### 兼容性测试
- [ ] Chrome/Edge（最新版）
- [ ] Firefox（最新版）
- [ ] Safari（最新版）
- [ ] 移动端浏览器

---

## 七、后续迭代计划

### v1.1（短期）
- [ ] 添加更多示例城市
- [ ] 支持参数预设保存（localStorage）
- [ ] 优化图表交互（缩放、tooltip）
- [ ] 添加数据导出按钮（JSON）

### v1.2（中期）
- [ ] 集成地图选点（Leaflet）
- [ ] 支持 CSV 导出
- [ ] 添加 MRcalc/DRcalc 工具
- [ ] 支持多语言（英文）

### v2.0（长期）
- [ ] 批量计算（多坐标）
- [ ] 历史记录管理
- [ ] 结果对比功能
- [ ] 导出 PDF 报告
