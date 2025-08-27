// 应用入口文件
window.App = {
    initialized: false,
    
    // 初始化应用
    init() {
        if (this.initialized) {
            console.warn('App already initialized');
            return;
        }
        
        console.log('Initializing Solar Agent App...');
        
        try {
            // 检查依赖
            this.checkDependencies();
            
            // 初始化分析模块
            this.initAnalytics();
            
            // 设置错误处理
            this.setupErrorHandling();
            
            // 设置用户活动监听
            this.setupActivityMonitoring();
            
            // 标记为已初始化
            this.initialized = true;
            
            console.log('App initialized successfully');
            
            // 埋点：应用启动
            if (window.Analytics) {
                window.Analytics.track(window.AppConfig.analytics.events.PAGE_LOAD, {
                    timestamp: Date.now(),
                    userAgent: navigator.userAgent,
                    viewport: {
                        width: window.innerWidth,
                        height: window.innerHeight
                    }
                });
            }
            
        } catch (error) {
            console.error('App initialization failed:', error);
            this.handleInitializationError(error);
        }
    },
    
    // 检查依赖
    checkDependencies() {
        const requiredModules = [
            'AppConfig', 'AppState', 'Calculator', 'UI', 'Flows', 'MockMap', 'Mock3D'
        ];
        
        const missingModules = requiredModules.filter(module => !window[module]);
        
        if (missingModules.length > 0) {
            throw new Error(`Missing required modules: ${missingModules.join(', ')}`);
        }
        
        // 检查外部依赖
        if (typeof L === 'undefined') {
            console.warn('Leaflet not loaded, map functionality will be limited');
        }
        
        if (typeof THREE === 'undefined') {
            console.warn('Three.js not loaded, 3D functionality will be limited');
        }
    },
    
    // 初始化分析模块
    initAnalytics() {
        window.Analytics = {
            track(event, data = {}) {
                if (!window.AppConfig.analytics.enabled) return;
                
                const eventData = {
                    event: event,
                    timestamp: Date.now(),
                    sessionId: this.getSessionId(),
                    ...data
                };
                
                // 控制台输出（调试模式）
                if (window.AppConfig.debug.enabled) {
                    console.log('Analytics:', eventData);
                }
                
                // 这里可以扩展到真实的分析服务
                // 例如：Google Analytics, Mixpanel 等
            },
            
            getSessionId() {
                if (!this._sessionId) {
                    this._sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                }
                return this._sessionId;
            }
        };
    },
    
    // 设置错误处理
    setupErrorHandling() {
        // 全局错误捕获
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            
            if (window.Analytics) {
                window.Analytics.track(window.AppConfig.analytics.events.ERROR_OCCURRED, {
                    message: event.error.message,
                    filename: event.filename,
                    lineno: event.lineno,
                    colno: event.colno
                });
            }
            
            // 显示用户友好的错误信息
            this.showUserError('系统遇到了一些问题，请刷新页面重试。');
        });
        
        // Promise 错误捕获
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            
            if (window.Analytics) {
                window.Analytics.track(window.AppConfig.analytics.events.ERROR_OCCURRED, {
                    type: 'promise_rejection',
                    reason: event.reason
                });
            }
        });
    },
    
    // 设置用户活动监听
    setupActivityMonitoring() {
        let lastActivity = Date.now();
        let timeoutId = null;
        
        const resetTimeout = () => {
            lastActivity = Date.now();
            
            if (timeoutId) {
                clearTimeout(timeoutId);
            }
            
            timeoutId = setTimeout(() => {
                // 用户无响应超时
                if (window.Flows && window.AppState.currentStep !== 'DONE') {
                    window.Flows.handleTimeout();
                }
            }, window.AppConfig.ui.thresholds.responseTimeout);
        };
        
        // 监听用户活动
        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
            document.addEventListener(event, resetTimeout, true);
        });
        
        // 初始设置
        resetTimeout();
    },
    
    // 显示用户错误信息
    showUserError(message) {
        // 创建错误提示
        const errorDiv = document.createElement('div');
        errorDiv.className = 'global-error';
        errorDiv.innerHTML = `
            <div class="error-content">
                <span class="error-icon">⚠️</span>
                <span class="error-message">${message}</span>
                <button class="error-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // 添加样式
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #f56565;
            color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            max-width: 400px;
        `;
        
        document.body.appendChild(errorDiv);
        
        // 5秒后自动移除
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 5000);
    },
    
    // 处理初始化错误
    handleInitializationError(error) {
        const errorMessage = `
            <div style="text-align: center; padding: 50px; color: #666;">
                <h2>应用初始化失败</h2>
                <p>请刷新页面重试，或联系技术支持。</p>
                <button onclick="location.reload()" style="margin-top: 20px; padding: 10px 20px; background: #38b2ac; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    刷新页面
                </button>
                <details style="margin-top: 20px; text-align: left;">
                    <summary>技术详情</summary>
                    <pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; overflow: auto;">${error.stack}</pre>
                </details>
            </div>
        `;
        
        document.body.innerHTML = errorMessage;
    },
    
    // 重启应用
    restart() {
        console.log('Restarting app...');
        
        // 重置状态
        if (window.AppState) {
            window.AppState.reset();
        }
        
        // 重置UI
        if (window.UI) {
            window.UI.reset();
        }
        
        // 重置地图
        if (window.MockMap) {
            window.MockMap.reset();
        }
        
        // 重置3D
        if (window.Mock3D) {
            window.Mock3D.reset();
        }
        
        console.log('App restarted');
    },
    
    // 获取应用状态
    getStatus() {
        return {
            initialized: this.initialized,
            currentStep: window.AppState ? window.AppState.currentStep : 'UNKNOWN',
            sessionData: window.AppState ? window.AppState.getSessionSummary() : null,
            timestamp: Date.now()
        };
    },
    
    // 调试工具
    debug: {
        // 跳转到指定步骤
        goToStep(step) {
            if (window.AppState && window.AppState.STEPS[step]) {
                window.AppState.currentStep = step;
                window.AppState.onStateChange('DEBUG', step, { debug: true });
            }
        },
        
        // 设置模拟数据
        setMockData(data) {
            Object.keys(data).forEach(key => {
                window.AppState.updateSessionData(key, data[key]);
            });
        },
        
        // 获取所有计算结果
        getAllCalculations() {
            const roofArea = window.AppState.getSessionData('roofArea') || 100;
            const results = {};
            
            window.AppConfig.plans.forEach(plan => {
                results[plan.id] = window.Calculator.calculateCompletePlan(
                    roofArea, 'simple', plan, 'standard'
                );
            });
            
            return results;
        },
        
        // 触发兜底测试
        testFallback(type) {
            window.AppState.triggerFallback(type, 'Debug test');
        }
    }
};

// DOM 加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 延迟初始化，确保所有模块都已加载
    setTimeout(() => {
        window.App.init();
    }, 100);
});

// 调试模式下暴露到全局
if (window.AppConfig && window.AppConfig.debug.enabled) {
    window.debugApp = window.App;
    
    // 添加调试快捷键
    document.addEventListener('keydown', function(e) {
        // Ctrl+Shift+D 打开调试面板
        if (e.ctrlKey && e.shiftKey && e.key === 'D') {
            console.log('=== Solar Agent Debug Info ===');
            console.log('App Status:', window.App.getStatus());
            console.log('State:', window.AppState);
            console.log('Session Data:', window.AppState.sessionData);
            console.log('Config:', window.AppConfig);
        }
    });
}
