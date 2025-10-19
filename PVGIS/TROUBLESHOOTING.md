# 问题排查指南

## 问题 1：小时序列堆栈溢出

### 错误信息
```
Maximum call stack size exceeded
```

### 问题描述
- **场景**：切换到"小时序列" Tab，填入经纬度和参数，点击"计算"
- **现象**：页面显示错误提示，浏览器控制台报堆栈溢出
- **影响**：无法查看小时序列数据和图表

### 根本原因

**JavaScript 扩展运算符的限制**

小时序列包含 **8760 个数据点**（365天 × 24小时），使用扩展运算符会导致问题：

```javascript
// ❌ 错误写法（会堆栈溢出）
const radiation = [/* 8760 个数据 */];
const max = Math.max(...radiation);  // 相当于 Math.max(v1, v2, v3, ..., v8760)
```

**为什么会溢出？**

1. 扩展运算符 `...` 会将数组展开为函数参数
2. `Math.max(...radiation)` 相当于调用 `Math.max(v1, v2, v3, ..., v8760)`
3. JavaScript 函数调用栈有大小限制（通常约 10,000-50,000 个参数）
4. 8760 个参数接近或超过某些浏览器的限制

### 解决方案

**使用 `reduce` 方法替代扩展运算符**

```javascript
// ✅ 正确写法（不会溢出）
const max = radiation.reduce((a, b) => Math.max(a, b), -Infinity);
const min = radiation.reduce((a, b) => Math.min(a, b), Infinity);
```

**原理**：
- `reduce` 是迭代方法，每次只处理两个值
- 不会一次性展开所有参数
- 调用栈深度固定，不受数组大小影响

### 修复代码对比

#### 修复前（第 390-391 行）
```javascript
const max = Math.max(...radiation);  // ❌ 堆栈溢出
const min = Math.min(...radiation);  // ❌ 堆栈溢出
```

#### 修复后（第 391-392 行）
```javascript
const max = radiation.reduce((a, b) => Math.max(a, b), -Infinity);  // ✅ 正常
const min = radiation.reduce((a, b) => Math.min(a, b), Infinity);   // ✅ 正常
```

### 验证步骤

1. **重启服务器**
   ```bash
   pkill -f "node proxy-server.js"
   npm start
   ```

2. **刷新浏览器**（强制刷新）
   - Mac: `Cmd + Shift + R`
   - Windows: `Ctrl + Shift + R`

3. **测试小时序列**
   - 切换到"小时序列" Tab
   - 使用默认墨尔本坐标
   - 点击"计算"
   - 应该正常显示 KPI 和折线图

### 预期结果

**成功显示**：
```
小时辐照序列

┌──────────────┬──────────────┬──────────────┬──────────────┐
│ 最大值       │ 平均值       │ 最小值       │ 总计         │
│ 1000 W/m²   │ 200 W/m²    │ 0 W/m²      │ 1800 kWh/m² │
└──────────────┴──────────────┴──────────────┴──────────────┘

[折线图显示全年 8760 小时的辐照数据]
```

---

## 问题 2：CORS 错误

### 错误信息
```
Access to fetch at 'https://re.jrc.ec.europa.eu/...' from origin 'http://localhost:3001' has been blocked by CORS policy
```

### 问题描述
- **场景**：直接从浏览器调用 PVGIS API
- **现象**：网络请求被浏览器拦截
- **影响**：无法获取数据

### 解决方案

**使用后端代理**（已实现）

前端不直接调用 PVGIS，而是通过本地代理：
```javascript
// ✅ 正确：通过代理
fetch('/api/pvgis/proxy', {
  method: 'POST',
  body: JSON.stringify({ tool, params })
})

// ❌ 错误：直接调用（会被 CORS 拦截）
fetch('https://re.jrc.ec.europa.eu/api/v5_3/PVcalc?...')
```

---

## 问题 3：参数校验失败

### 错误信息
```
纬度范围: -90 ~ 90
经度范围: -180 ~ 180
峰值功率必须大于 0
系统损耗范围: 0 ~ 100%
```

### 解决方案

**检查输入参数**：
- 纬度：-90 ~ 90
- 经度：-180 ~ 180
- 峰值功率：> 0
- 系统损耗：0 ~ 100

**墨尔本示例**：
```
纬度：-37.830795
经度：145.042134
峰值功率：8.8 kWp
系统损耗：14%
```

---

## 问题 4：网络超时

### 错误信息
```
请求 PVGIS 失败
timeout of 30000ms exceeded
```

### 可能原因
1. PVGIS 服务器响应慢
2. 网络连接问题
3. 服务器过载

### 解决方案

1. **等待重试**：PVGIS 服务器可能暂时过载
2. **检查网络**：确保可以访问 `re.jrc.ec.europa.eu`
3. **查看日志**：服务器控制台会显示详细错误

---

## 问题 5：图表不显示

### 可能原因
1. Chart.js CDN 加载失败
2. 数据格式错误
3. Canvas 元素未找到

### 排查步骤

1. **检查浏览器控制台**
   ```
   F12 或 Cmd+Option+I
   查看 Console 和 Network 标签
   ```

2. **检查 Chart.js 加载**
   ```javascript
   // 在控制台输入
   typeof Chart
   // 应该返回 "function"
   ```

3. **检查数据格式**
   - PVcalc: `data.outputs.totals.fixed`
   - seriescalc: `data.outputs.hourly`
   - printhorizon: `data.outputs.horizon_profile`

---

## 问题 6：缓存问题

### 现象
- 修改参数后结果不变
- 服务器日志显示"命中缓存"

### 解决方案

**清除缓存**：
```bash
# 方法 1：重启服务器（清除内存缓存）
pkill -f "node proxy-server.js"
npm start

# 方法 2：等待缓存过期（1小时）

# 方法 3：修改参数（避免缓存键相同）
```

---

## 调试技巧

### 1. 查看服务器日志
```bash
# 服务器会输出详细日志
📡 收到请求: PVcalc { lat: -37.83, lon: 145.04, ... }
🔗 调用 PVGIS: https://...
✅ 请求成功
✅ 命中缓存
```

### 2. 浏览器控制台
```javascript
// 查看错误
console.error

// 查看网络请求
Network 标签 -> 查看 /api/pvgis/proxy

// 查看响应数据
Response 标签 -> 查看 JSON 数据
```

### 3. 测试 API 端点
```bash
# 健康检查
curl http://localhost:3001/api/health

# 测试代理
curl -X POST http://localhost:3001/api/pvgis/proxy \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "PVcalc",
    "params": {
      "lat": -37.83,
      "lon": 145.04,
      "peakpower": 8.8,
      "loss": 14,
      "outputformat": "json"
    }
  }'
```

---

## 性能优化建议

### 1. 小时序列数据降采样

如果 8760 个点渲染太慢，可以降采样：

```javascript
// 每 4 小时取一个点（减少到 2190 个点）
const sampledData = hourly.filter((_, i) => i % 4 === 0);
```

### 2. 图表优化

```javascript
// Chart.js 配置优化
options: {
  animation: false,  // 禁用动画
  parsing: false,    // 禁用数据解析
  normalized: true   // 数据已归一化
}
```

### 3. 虚拟滚动

对于超大数据集，考虑使用虚拟滚动库（如 react-window）

---

## 常见问题 FAQ

### Q1: 为什么墨尔本的方位角是 0°？
A: 南半球太阳从北方经过，所以 0°（正北）是最佳朝向。

### Q2: 峰值功率为什么是只读的？
A: 峰值功率由"单块功率 × 数量"自动计算，不需要手动输入。

### Q3: 系统损耗 14% 是怎么来的？
A: 这是 PVGIS 的默认值，包括线缆、逆变器、温度等综合损耗。

### Q4: 小时序列数据是哪一年的？
A: PVGIS 返回的是"典型气象年"（TMY）数据，综合了多年的气象数据。

### Q5: 为什么年度发电量有波动？
A: PVGIS 使用不同年份的卫星数据，每次请求可能返回略有不同的结果（±2-5%）。

---

## 联系支持

如果问题仍未解决，请提供：
1. 错误信息截图
2. 浏览器控制台日志
3. 服务器控制台日志
4. 输入的坐标和参数
5. 浏览器版本和操作系统

---

**最后更新**：2025-10-19  
**版本**：v1.1
