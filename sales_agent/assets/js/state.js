// 状态管理和有限状态机
window.AppState = {
    // 当前状态
    currentStep: 'WELCOME',
    
    // 状态枚举
    STEPS: {
        WELCOME: 'WELCOME',
        ADDRESS: 'ADDRESS', 
        MAP_CONFIRM: 'MAP_CONFIRM',
        ANALYZING: 'ANALYZING',
        MODEL_3D: 'MODEL_3D',
        PLANS: 'PLANS',
        VALUE: 'VALUE',
        LEAD_FORM: 'LEAD_FORM',
        DONE: 'DONE'
    },
    
    // 会话数据
    sessionData: {
        userAddress: '',
        roofArea: 0,
        roofComplexity: 'simple', // 'flat', 'simple', 'complex'
        hasExistingPanels: false,
        hasHighEnergyFeatures: false, // 游泳池等
        userProfile: 'standard',
        maxCapacity: 0,
        selectedPlan: null,
        calculatedValues: {},
        startTime: Date.now(),
        interactions: []
    },
    
    // 状态转换规则
    transitions: {
        WELCOME: ['ADDRESS'],
        ADDRESS: ['MAP_CONFIRM', 'LEAD_FORM'], // 可直接跳转到留资（兜底）
        MAP_CONFIRM: ['ANALYZING', 'ADDRESS', 'LEAD_FORM'], // 可返回地址输入或兜底
        ANALYZING: ['MODEL_3D', 'LEAD_FORM'], // 分析失败可兜底
        MODEL_3D: ['PLANS', 'LEAD_FORM'],
        PLANS: ['VALUE', 'LEAD_FORM'],
        VALUE: ['LEAD_FORM'],
        LEAD_FORM: ['DONE'],
        DONE: []
    },
    
    // 状态切换方法
    canTransitionTo(targetStep) {
        const allowedTransitions = this.transitions[this.currentStep] || [];
        return allowedTransitions.includes(targetStep);
    },
    
    transitionTo(targetStep, data = {}) {
        if (!this.canTransitionTo(targetStep)) {
            console.warn(`Invalid transition from ${this.currentStep} to ${targetStep}`);
            return false;
        }
        
        const previousStep = this.currentStep;
        this.currentStep = targetStep;
        
        // 记录交互
        this.sessionData.interactions.push({
            timestamp: Date.now(),
            from: previousStep,
            to: targetStep,
            data: data
        });
        
        // 触发状态变化事件
        this.onStateChange(previousStep, targetStep, data);
        
        // 埋点
        if (window.Analytics) {
            window.Analytics.track(window.AppConfig.analytics.events.STEP_ENTER, {
                step: targetStep,
                previousStep: previousStep,
                sessionTime: Date.now() - this.sessionData.startTime
            });
        }
        
        return true;
    },
    
    // 状态变化回调
    onStateChange(from, to, data) {
        console.log(`State transition: ${from} -> ${to}`, data);
        
        // 更新UI
        if (window.UI) {
            window.UI.updateStep(to);
            window.UI.updateProgress(this.getStepProgress(to));
        }
        
        // 执行对应的流程逻辑
        if (window.Flows) {
            window.Flows.executeStep(to, data);
        }
    },
    
    // 获取步骤进度百分比
    getStepProgress(step) {
        const stepOrder = Object.keys(this.STEPS);
        const currentIndex = stepOrder.indexOf(step);
        return Math.round((currentIndex / (stepOrder.length - 1)) * 100);
    },
    
    // 更新会话数据
    updateSessionData(key, value) {
        if (key.includes('.')) {
            // 支持嵌套属性更新，如 'calculatedValues.yearlyGeneration'
            const keys = key.split('.');
            let obj = this.sessionData;
            for (let i = 0; i < keys.length - 1; i++) {
                if (!obj[keys[i]]) obj[keys[i]] = {};
                obj = obj[keys[i]];
            }
            obj[keys[keys.length - 1]] = value;
        } else {
            this.sessionData[key] = value;
        }
        
        console.log(`Session data updated: ${key} =`, value);
    },
    
    // 获取会话数据
    getSessionData(key) {
        if (key.includes('.')) {
            const keys = key.split('.');
            let obj = this.sessionData;
            for (const k of keys) {
                if (obj && typeof obj === 'object') {
                    obj = obj[k];
                } else {
                    return undefined;
                }
            }
            return obj;
        }
        return this.sessionData[key];
    },
    
    // 重置状态（用于重新开始）
    reset() {
        this.currentStep = 'WELCOME';
        this.sessionData = {
            userAddress: '',
            roofArea: 0,
            roofComplexity: 'simple',
            hasExistingPanels: false,
            hasHighEnergyFeatures: false,
            userProfile: 'standard',
            maxCapacity: 0,
            selectedPlan: null,
            calculatedValues: {},
            startTime: Date.now(),
            interactions: []
        };
        
        if (window.UI) {
            window.UI.reset();
        }
    },
    
    // 触发兜底流程
    triggerFallback(type, reason = '') {
        console.log(`Fallback triggered: ${type}`, reason);
        
        // 埋点记录兜底触发
        if (window.Analytics) {
            window.Analytics.track(window.AppConfig.analytics.events.FALLBACK_TRIGGERED, {
                type: type,
                reason: reason,
                currentStep: this.currentStep,
                sessionTime: Date.now() - this.sessionData.startTime
            });
        }
        
        // 根据兜底类型执行不同逻辑
        if (window.Flows) {
            window.Flows.handleFallback(type, reason);
        }
    },
    
    // 获取当前会话摘要
    getSessionSummary() {
        return {
            currentStep: this.currentStep,
            duration: Date.now() - this.sessionData.startTime,
            interactionCount: this.sessionData.interactions.length,
            roofArea: this.sessionData.roofArea,
            selectedPlan: this.sessionData.selectedPlan,
            calculatedValues: this.sessionData.calculatedValues
        };
    },
    
    // 检查是否可以进入下一步
    canProceed() {
        switch (this.currentStep) {
            case 'WELCOME':
                return true;
            case 'ADDRESS':
                return !!this.sessionData.userAddress;
            case 'MAP_CONFIRM':
                return this.sessionData.roofArea > 0;
            case 'ANALYZING':
                return this.sessionData.maxCapacity > 0;
            case 'MODEL_3D':
                return true;
            case 'PLANS':
                return !!this.sessionData.selectedPlan;
            case 'VALUE':
                return Object.keys(this.sessionData.calculatedValues).length > 0;
            default:
                return false;
        }
    },
    
    // 验证会话数据完整性
    validateSessionData() {
        const errors = [];
        
        if (!this.sessionData.userAddress) {
            errors.push('缺少用户地址');
        }
        
        if (this.sessionData.roofArea <= 0) {
            errors.push('屋顶面积无效');
        }
        
        if (this.sessionData.maxCapacity <= 0) {
            errors.push('最大容量计算错误');
        }
        
        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }
};

// 初始化状态管理
document.addEventListener('DOMContentLoaded', function() {
    console.log('State management initialized');
    
    // 如果是调试模式，暴露状态到全局
    if (window.AppConfig.debug.enabled) {
        window.debugState = window.AppState;
    }
});
