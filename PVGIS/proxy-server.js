const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = 3001;

// 中间件
app.use(express.json());
app.use(express.static(__dirname)); // 提供静态文件服务

// 简单的内存缓存
const cache = new Map();
const CACHE_TTL = 3600000; // 1小时

// 速率限制（简单实现）
const requestQueue = [];
let processing = false;

async function processQueue() {
  if (processing || requestQueue.length === 0) return;
  
  processing = true;
  const { resolve, reject, url } = requestQueue.shift();
  
  try {
    const response = await axios.get(url, { timeout: 30000 });
    resolve(response.data);
  } catch (error) {
    reject(error);
  } finally {
    processing = false;
    // 确保不超过 30 次/秒
    setTimeout(() => processQueue(), 34); // ~30 次/秒
  }
}

function queueRequest(url) {
  return new Promise((resolve, reject) => {
    requestQueue.push({ resolve, reject, url });
    processQueue();
  });
}

// PVGIS 代理端点
app.post('/api/pvgis/proxy', async (req, res) => {
  const { tool, params } = req.body;
  
  console.log(`📡 收到请求: ${tool}`, params);
  
  try {
    // 构建缓存键
    const cacheKey = `${tool}:${JSON.stringify(params)}`;
    
    // 检查缓存
    const cached = cache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
      console.log('✅ 命中缓存');
      return res.json({
        success: true,
        data: cached.data,
        cached: true,
        timestamp: new Date().toISOString()
      });
    }
    
    // 构建 PVGIS URL
    const baseURL = 'https://re.jrc.ec.europa.eu/api/v5_3';
    const queryString = new URLSearchParams(params).toString();
    const url = `${baseURL}/${tool}?${queryString}`;
    
    console.log(`🔗 调用 PVGIS: ${url}`);
    
    // 通过队列调用（速率限制）
    const data = await queueRequest(url);
    
    // 存入缓存
    cache.set(cacheKey, {
      data,
      timestamp: Date.now()
    });
    
    console.log('✅ 请求成功');
    
    res.json({
      success: true,
      data,
      cached: false,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('❌ 请求失败:', error.message);
    
    res.status(502).json({
      success: false,
      message: error.response?.data?.message || error.message || '请求 PVGIS 失败'
    });
  }
});

// 健康检查
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    cacheSize: cache.size,
    queueLength: requestQueue.length
  });
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`🚀 PVGIS 代理服务器运行在 http://localhost:${PORT}`);
  console.log(`📄 打开浏览器访问: http://localhost:${PORT}/pvgis_simulator.html`);
});
