// 地图占位模块 (Leaflet + 卫星图)
window.MockMap = {
    map: null,
    selectedArea: null,
    drawingLayer: null,
    isDrawing: false,
    
    // 初始化地图
    init() {
        const mapContainer = document.getElementById('map');
        if (!mapContainer) {
            console.error('Map container not found');
            return;
        }
        
        const config = window.AppConfig.map;
        
        // 创建地图实例
        this.map = L.map('map', {
            center: config.defaultCenter,
            zoom: config.defaultZoom,
            minZoom: config.minZoom,
            maxZoom: config.maxZoom
        });
        
        // 添加卫星图瓦片层
        L.tileLayer(config.satelliteTileUrl, {
            attribution: config.attribution,
            maxZoom: config.maxZoom
        }).addTo(this.map);
        
        // 创建绘制层
        this.drawingLayer = L.layerGroup().addTo(this.map);
        
        // 绑定地图事件
        this.bindMapEvents();
        
        // 绑定控制按钮事件
        this.bindControlEvents();
        
        console.log('Map initialized');
    },
    
    // 绑定地图事件
    bindMapEvents() {
        // 点击事件 - 简化的屋顶选择
        this.map.on('click', (e) => {
            if (!this.isDrawing) {
                this.selectRoofAtPoint(e.latlng);
            }
        });
        
        // 右键开始绘制模式
        this.map.on('contextmenu', (e) => {
            e.originalEvent.preventDefault();
            this.toggleDrawingMode();
        });
    },
    
    // 绑定控制按钮事件
    bindControlEvents() {
        const zoomInBtn = document.getElementById('mapZoomIn');
        const zoomOutBtn = document.getElementById('mapZoomOut');
        const confirmBtn = document.getElementById('confirmRoof');
        
        if (zoomInBtn) {
            zoomInBtn.addEventListener('click', () => {
                this.map.zoomIn();
            });
        }
        
        if (zoomOutBtn) {
            zoomOutBtn.addEventListener('click', () => {
                this.map.zoomOut();
            });
        }
        
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => {
                this.confirmRoofSelection();
            });
        }
    },
    
    // 根据地址定位
    locateAddress(address) {
        // 模拟地址解析 - 实际应该调用 Geocoding API
        const mockCoordinates = this.getMockCoordinates(address);
        
        if (mockCoordinates) {
            this.map.setView(mockCoordinates, 18);
            
            // 添加地址标记
            const marker = L.marker(mockCoordinates)
                .addTo(this.map)
                .bindPopup(`定位地址: ${address}`)
                .openPopup();
            
            // 添加到绘制层以便后续清理
            this.drawingLayer.addLayer(marker);
            
            return true;
        } else {
            console.warn('Address not found:', address);
            return false;
        }
    },
    
    // 模拟地址坐标获取
    getMockCoordinates(address) {
        // 简化的地址匹配 - 实际应该调用 Google Geocoding API
        const mockAddresses = {
            '布里斯班': [-27.4698, 153.0251],
            '悉尼': [-33.8688, 151.2093],
            '墨尔本': [-37.8136, 144.9631],
            '珀斯': [-31.9505, 115.8605],
            '阿德莱德': [-34.9285, 138.6007]
        };
        
        // 检查是否包含已知城市名
        for (const [city, coords] of Object.entries(mockAddresses)) {
            if (address.includes(city)) {
                // 添加随机偏移模拟具体地址
                return [
                    coords[0] + (Math.random() - 0.5) * 0.01,
                    coords[1] + (Math.random() - 0.5) * 0.01
                ];
            }
        }
        
        // 默认返回布里斯班附近的随机位置
        return [
            -27.4698 + (Math.random() - 0.5) * 0.1,
            153.0251 + (Math.random() - 0.5) * 0.1
        ];
    },
    
    // 点击选择屋顶
    selectRoofAtPoint(latlng) {
        // 清除之前的选择
        this.clearSelection();
        
        // 创建模拟屋顶区域 (矩形)
        const roofBounds = this.generateMockRoofBounds(latlng);
        
        // 创建屋顶多边形
        this.selectedArea = L.polygon(roofBounds, {
            color: '#38b2ac',
            fillColor: '#38b2ac',
            fillOpacity: 0.3,
            weight: 2
        }).addTo(this.drawingLayer);
        
        // 计算面积
        const area = this.calculatePolygonArea(roofBounds);
        
        // 显示面积信息
        this.selectedArea.bindPopup(`
            <div>
                <strong>选中屋顶</strong><br>
                估算面积: ${area.toFixed(1)} m²<br>
                <small>点击"确认屋顶"继续</small>
            </div>
        `).openPopup();
        
        // 启用确认按钮
        const confirmBtn = document.getElementById('confirmRoof');
        if (confirmBtn) {
            confirmBtn.disabled = false;
        }
        
        // 更新会话数据
        window.AppState.updateSessionData('roofArea', area);
        
        console.log('Roof selected, area:', area);
    },
    
    // 生成模拟屋顶边界
    generateMockRoofBounds(center) {
        // 生成随机大小的矩形屋顶 (30-200 m²)
        const baseSize = 0.0001; // 大约10米的经纬度差
        const sizeMultiplier = 0.5 + Math.random() * 2; // 0.5-2.5倍
        
        const halfWidth = baseSize * sizeMultiplier;
        const halfHeight = baseSize * sizeMultiplier * (0.6 + Math.random() * 0.8); // 长宽比变化
        
        return [
            [center.lat - halfHeight, center.lng - halfWidth],
            [center.lat - halfHeight, center.lng + halfWidth],
            [center.lat + halfHeight, center.lng + halfWidth],
            [center.lat + halfHeight, center.lng - halfWidth]
        ];
    },
    
    // 计算多边形面积 (简化计算)
    calculatePolygonArea(bounds) {
        if (!bounds || bounds.length < 3) return 0;
        
        // 简化的面积计算 - 实际应该使用球面几何
        const latDiff = Math.abs(bounds[0][0] - bounds[2][0]);
        const lngDiff = Math.abs(bounds[0][1] - bounds[2][1]);
        
        // 大致转换为平方米 (1度纬度约111km)
        const areaM2 = latDiff * lngDiff * 111000 * 111000 * Math.cos(bounds[0][0] * Math.PI / 180);
        
        // 限制在合理范围内
        return Math.max(20, Math.min(500, areaM2));
    },
    
    // 切换绘制模式
    toggleDrawingMode() {
        this.isDrawing = !this.isDrawing;
        
        if (this.isDrawing) {
            this.map.getContainer().style.cursor = 'crosshair';
            this.showDrawingInstructions();
        } else {
            this.map.getContainer().style.cursor = '';
            this.hideDrawingInstructions();
        }
    },
    
    // 显示绘制说明
    showDrawingInstructions() {
        const popup = L.popup()
            .setLatLng(this.map.getCenter())
            .setContent('点击地图绘制屋顶轮廓<br><small>右键退出绘制模式</small>')
            .openOn(this.map);
    },
    
    // 隐藏绘制说明
    hideDrawingInstructions() {
        this.map.closePopup();
    },
    
    // 确认屋顶选择
    confirmRoofSelection() {
        if (!this.selectedArea) {
            window.UI.showError('请先在地图上选择屋顶区域');
            return;
        }
        
        const roofArea = window.AppState.getSessionData('roofArea');
        
        // 验证面积
        const validation = this.validateRoofArea(roofArea);
        if (!validation.isValid) {
            window.AppState.triggerFallback(validation.fallbackType, validation.message);
            return;
        }
        
        // 埋点
        if (window.Analytics) {
            window.Analytics.track(window.AppConfig.analytics.events.ROOF_SELECTED, {
                area: roofArea
            });
        }
        
        // 添加确认消息
        window.UI.addMessage('user', `已选择屋顶，面积约 ${roofArea.toFixed(1)} m²`);
        window.UI.addMessage('bot', window.AppConfig.messages.analyzing);
        
        // 转换到分析步骤
        window.AppState.transitionTo('ANALYZING');
    },
    
    // 验证屋顶面积
    validateRoofArea(area) {
        const thresholds = window.AppConfig.ui.thresholds;
        
        if (area < thresholds.minRoofArea) {
            return {
                isValid: false,
                fallbackType: 'area_too_small',
                message: window.AppConfig.messages.fallbacks.areaTooSmall
            };
        }
        
        if (area > thresholds.maxRoofArea) {
            return {
                isValid: false,
                fallbackType: 'area_too_big',
                message: window.AppConfig.messages.fallbacks.areaTooBig
            };
        }
        
        return { isValid: true };
    },
    
    // 清除选择
    clearSelection() {
        if (this.drawingLayer) {
            this.drawingLayer.clearLayers();
        }
        this.selectedArea = null;
        
        const confirmBtn = document.getElementById('confirmRoof');
        if (confirmBtn) {
            confirmBtn.disabled = true;
        }
    },
    
    // 重置地图
    reset() {
        if (this.map) {
            this.clearSelection();
            this.map.setView(window.AppConfig.map.defaultCenter, window.AppConfig.map.defaultZoom);
        }
    },
    
    // 销毁地图
    destroy() {
        if (this.map) {
            this.map.remove();
            this.map = null;
        }
    }
};

// 地图相关的工具函数
window.MockMap.utils = {
    // 距离计算
    calculateDistance(lat1, lng1, lat2, lng2) {
        const R = 6371e3; // 地球半径 (米)
        const φ1 = lat1 * Math.PI / 180;
        const φ2 = lat2 * Math.PI / 180;
        const Δφ = (lat2 - lat1) * Math.PI / 180;
        const Δλ = (lng2 - lng1) * Math.PI / 180;
        
        const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
                  Math.cos(φ1) * Math.cos(φ2) *
                  Math.sin(Δλ/2) * Math.sin(Δλ/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        
        return R * c;
    },
    
    // 边界框计算
    getBounds(coordinates) {
        if (!coordinates || coordinates.length === 0) return null;
        
        let minLat = coordinates[0][0];
        let maxLat = coordinates[0][0];
        let minLng = coordinates[0][1];
        let maxLng = coordinates[0][1];
        
        coordinates.forEach(coord => {
            minLat = Math.min(minLat, coord[0]);
            maxLat = Math.max(maxLat, coord[0]);
            minLng = Math.min(minLng, coord[1]);
            maxLng = Math.max(maxLng, coord[1]);
        });
        
        return [[minLat, minLng], [maxLat, maxLng]];
    }
};
