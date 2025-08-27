// 3D 模型占位模块 (Three.js 简化模型)
window.Mock3D = {
    scene: null,
    camera: null,
    renderer: null,
    controls: null,
    houseGroup: null,
    panelsGroup: null,
    batteryGroup: null,
    animationId: null,
    
    // 初始化 3D 场景
    init() {
        const container = document.getElementById('threejsContainer');
        if (!container) {
            console.error('3D container not found');
            return;
        }
        
        try {
            this.setupScene(container);
            this.createHouse();
            this.setupLighting();
            this.setupControls();
            this.bindEvents();
            this.startAnimation();
            
            console.log('3D scene initialized');
        } catch (error) {
            console.error('3D initialization failed:', error);
            this.handleRenderFailure();
        }
    },
    
    // 设置场景
    setupScene(container) {
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        // 创建场景
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xf0f0f0);
        
        // 创建相机
        this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        this.camera.position.set(10, 8, 10);
        this.camera.lookAt(0, 0, 0);
        
        // 创建渲染器
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(width, height);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        container.appendChild(this.renderer.domElement);
    },
    
    // 创建房屋模型
    createHouse() {
        this.houseGroup = new THREE.Group();
        
        // 获取会话数据
        const roofArea = window.AppState.getSessionData('roofArea') || 100;
        const complexity = window.AppState.getSessionData('roofComplexity') || 'simple';
        
        // 根据屋顶面积计算房屋尺寸
        const houseSize = Math.sqrt(roofArea / 2); // 简化计算
        const houseWidth = houseSize;
        const houseDepth = houseSize;
        const houseHeight = 3; // 固定高度
        
        // 创建墙体
        this.createWalls(houseWidth, houseDepth, houseHeight);
        
        // 创建屋顶
        this.createRoof(houseWidth, houseDepth, houseHeight, complexity);
        
        // 添加到场景
        this.scene.add(this.houseGroup);
        
        // 创建面板组和电池组
        this.panelsGroup = new THREE.Group();
        this.batteryGroup = new THREE.Group();
        this.scene.add(this.panelsGroup);
        this.scene.add(this.batteryGroup);
    },
    
    // 创建墙体
    createWalls(width, depth, height) {
        const wallMaterial = new THREE.MeshLambertMaterial({ color: 0xcccccc });
        
        // 前墙
        const frontWall = new THREE.BoxGeometry(width, height, 0.2);
        const frontWallMesh = new THREE.Mesh(frontWall, wallMaterial);
        frontWallMesh.position.set(0, height/2, depth/2);
        frontWallMesh.castShadow = true;
        this.houseGroup.add(frontWallMesh);
        
        // 后墙
        const backWallMesh = frontWallMesh.clone();
        backWallMesh.position.set(0, height/2, -depth/2);
        this.houseGroup.add(backWallMesh);
        
        // 左墙
        const sideWall = new THREE.BoxGeometry(0.2, height, depth);
        const leftWallMesh = new THREE.Mesh(sideWall, wallMaterial);
        leftWallMesh.position.set(-width/2, height/2, 0);
        leftWallMesh.castShadow = true;
        this.houseGroup.add(leftWallMesh);
        
        // 右墙
        const rightWallMesh = leftWallMesh.clone();
        rightWallMesh.position.set(width/2, height/2, 0);
        this.houseGroup.add(rightWallMesh);
    },
    
    // 创建屋顶
    createRoof(width, depth, height, complexity) {
        const roofMaterial = new THREE.MeshLambertMaterial({ color: 0x8b4513 });
        
        if (complexity === 'flat') {
            // 平屋顶
            const roofGeometry = new THREE.BoxGeometry(width, 0.2, depth);
            const roofMesh = new THREE.Mesh(roofGeometry, roofMaterial);
            roofMesh.position.set(0, height + 0.1, 0);
            roofMesh.receiveShadow = true;
            this.houseGroup.add(roofMesh);
        } else {
            // 坡屋顶
            const roofGeometry = new THREE.ConeGeometry(Math.max(width, depth) * 0.7, 2, 4);
            const roofMesh = new THREE.Mesh(roofGeometry, roofMaterial);
            roofMesh.position.set(0, height + 1, 0);
            roofMesh.rotation.y = Math.PI / 4;
            roofMesh.receiveShadow = true;
            this.houseGroup.add(roofMesh);
        }
    },
    
    // 设置光照
    setupLighting() {
        // 环境光
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        
        // 方向光 (太阳光)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);
        
        // 地面
        const groundGeometry = new THREE.PlaneGeometry(50, 50);
        const groundMaterial = new THREE.MeshLambertMaterial({ color: 0x90ee90 });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        this.scene.add(ground);
    },
    
    // 设置控制器
    setupControls() {
        // 简化的轨道控制器 (不依赖 OrbitControls)
        this.setupSimpleControls();
    },
    
    // 简化的控制器实现
    setupSimpleControls() {
        const container = this.renderer.domElement;
        let isMouseDown = false;
        let mouseX = 0;
        let mouseY = 0;
        let targetRotationX = 0;
        let targetRotationY = 0;
        let currentRotationX = 0;
        let currentRotationY = 0;
        
        container.addEventListener('mousedown', (e) => {
            isMouseDown = true;
            mouseX = e.clientX;
            mouseY = e.clientY;
        });
        
        container.addEventListener('mousemove', (e) => {
            if (!isMouseDown) return;
            
            const deltaX = e.clientX - mouseX;
            const deltaY = e.clientY - mouseY;
            
            targetRotationY += deltaX * 0.01;
            targetRotationX += deltaY * 0.01;
            
            // 限制垂直旋转
            targetRotationX = Math.max(-Math.PI/3, Math.min(Math.PI/3, targetRotationX));
            
            mouseX = e.clientX;
            mouseY = e.clientY;
        });
        
        container.addEventListener('mouseup', () => {
            isMouseDown = false;
        });
        
        // 滚轮缩放
        container.addEventListener('wheel', (e) => {
            e.preventDefault();
            const scale = e.deltaY > 0 ? 1.1 : 0.9;
            this.camera.position.multiplyScalar(scale);
            
            // 限制缩放范围
            const distance = this.camera.position.length();
            if (distance < 5) {
                this.camera.position.normalize().multiplyScalar(5);
            } else if (distance > 50) {
                this.camera.position.normalize().multiplyScalar(50);
            }
        });
        
        // 在动画循环中应用旋转
        this.updateControls = () => {
            currentRotationX += (targetRotationX - currentRotationX) * 0.1;
            currentRotationY += (targetRotationY - currentRotationY) * 0.1;
            
            const radius = this.camera.position.length();
            this.camera.position.x = radius * Math.sin(currentRotationY) * Math.cos(currentRotationX);
            this.camera.position.y = radius * Math.sin(currentRotationX);
            this.camera.position.z = radius * Math.cos(currentRotationY) * Math.cos(currentRotationX);
            this.camera.lookAt(0, 0, 0);
        };
    },
    
    // 绑定事件
    bindEvents() {
        // 重置视角按钮
        const resetBtn = document.getElementById('resetView');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.resetView();
            });
        }
        
        // 窗口大小变化
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    },
    
    // 重置视角
    resetView() {
        this.camera.position.set(10, 8, 10);
        this.camera.lookAt(0, 0, 0);
    },
    
    // 处理窗口大小变化
    handleResize() {
        const container = document.getElementById('threejsContainer');
        if (!container) return;
        
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    },
    
    // 开始动画循环
    startAnimation() {
        const animate = () => {
            this.animationId = requestAnimationFrame(animate);
            
            if (this.updateControls) {
                this.updateControls();
            }
            
            this.renderer.render(this.scene, this.camera);
        };
        
        animate();
    },
    
    // 停止动画
    stopAnimation() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    },
    
    // 更新方案显示
    updatePlan(planId) {
        const plan = window.AppConfig.plans.find(p => p.id === planId);
        if (!plan) return;
        
        // 清除现有面板和电池
        this.clearPanels();
        this.clearBatteries();
        
        // 获取计算结果
        const roofArea = window.AppState.getSessionData('roofArea') || 100;
        const complexity = window.AppState.getSessionData('roofComplexity') || 'simple';
        
        const calculationResult = window.Calculator.calculateCompletePlan(
            roofArea, complexity, plan
        );
        
        if (calculationResult.success) {
            // 添加太阳能面板
            this.addSolarPanels(calculationResult.systemConfig.panelCount);
            
            // 添加电池 (如果有)
            if (calculationResult.systemConfig.hasBattery) {
                this.addBatteries(calculationResult.systemConfig.batteryCapacity);
            }
        }
    },
    
    // 添加太阳能面板
    addSolarPanels(panelCount) {
        const panelMaterial = new THREE.MeshLambertMaterial({ color: 0x1a1a2e });
        const panelGeometry = new THREE.BoxGeometry(1.7, 0.05, 1.1); // 标准面板尺寸
        
        const gridSize = Math.ceil(Math.sqrt(panelCount));
        const spacing = 2;
        
        for (let i = 0; i < panelCount; i++) {
            const row = Math.floor(i / gridSize);
            const col = i % gridSize;
            
            const panel = new THREE.Mesh(panelGeometry, panelMaterial);
            panel.position.set(
                (col - gridSize/2) * spacing,
                4, // 屋顶上方
                (row - gridSize/2) * spacing
            );
            panel.castShadow = true;
            
            this.panelsGroup.add(panel);
        }
        
        console.log(`Added ${panelCount} solar panels`);
    },
    
    // 添加电池
    addBatteries(capacity) {
        const batteryMaterial = new THREE.MeshLambertMaterial({ color: 0x666666 });
        const batteryGeometry = new THREE.BoxGeometry(0.6, 1.5, 0.3);
        
        const batteryCount = Math.ceil(capacity / 5); // 每个电池5kWh
        
        for (let i = 0; i < batteryCount; i++) {
            const battery = new THREE.Mesh(batteryGeometry, batteryMaterial);
            battery.position.set(
                -8 + i * 0.8, // 房屋侧面
                0.75,
                0
            );
            battery.castShadow = true;
            
            this.batteryGroup.add(battery);
        }
        
        console.log(`Added ${batteryCount} batteries (${capacity} kWh)`);
    },
    
    // 清除面板
    clearPanels() {
        while (this.panelsGroup.children.length > 0) {
            this.panelsGroup.remove(this.panelsGroup.children[0]);
        }
    },
    
    // 清除电池
    clearBatteries() {
        while (this.batteryGroup.children.length > 0) {
            this.batteryGroup.remove(this.batteryGroup.children[0]);
        }
    },
    
    // 处理渲染失败
    handleRenderFailure() {
        const container = document.getElementById('threejsContainer');
        if (container) {
            container.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 100%; flex-direction: column; color: #666;">
                    <h3>3D 模型加载失败</h3>
                    <p>您的设备可能不支持 3D 渲染，但这不影响方案计算。</p>
                    <button class="btn btn-primary" onclick="window.AppState.transitionTo('PLANS')">查看方案</button>
                </div>
            `;
        }
        
        // 触发兜底
        window.AppState.triggerFallback('render_failed', '3D渲染失败');
    },
    
    // 重置 3D 场景
    reset() {
        this.clearPanels();
        this.clearBatteries();
        this.resetView();
    },
    
    // 销毁 3D 场景
    destroy() {
        this.stopAnimation();
        
        if (this.renderer) {
            this.renderer.dispose();
            const container = document.getElementById('threejsContainer');
            if (container && this.renderer.domElement) {
                container.removeChild(this.renderer.domElement);
            }
        }
        
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
    }
};
