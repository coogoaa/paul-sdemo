// 对话流程控制模块
window.Flows = {
    
    // 执行步骤逻辑
    executeStep(step, data = {}) {
        console.log(`Executing step: ${step}`, data);
        
        switch (step) {
            case 'WELCOME':
                this.handleWelcome();
                break;
            case 'ADDRESS':
                this.handleAddress();
                break;
            case 'MAP_CONFIRM':
                this.handleMapConfirm(data);
                break;
            case 'ANALYZING':
                this.handleAnalyzing();
                break;
            case 'MODEL_3D':
                this.handleModel3D();
                break;
            case 'PLANS':
                this.handlePlans();
                break;
            case 'VALUE':
                this.handleValue();
                break;
            case 'LEAD_FORM':
                this.handleLeadForm();
                break;
            case 'DONE':
                this.handleDone();
                break;
            default:
                console.warn(`Unknown step: ${step}`);
        }
    },
    
    // 处理欢迎步骤
    handleWelcome() {
        // UI 已在初始化时处理
        console.log('Welcome step handled');
    },
    
    // 处理地址输入步骤
    handleAddress() {
        // UI 已处理地址输入界面
        console.log('Address step handled');
    },
    
    // 处理地图确认步骤
    handleMapConfirm(data) {
        window.UI.addMessage('bot', window.AppConfig.messages.addressConfirm);
        window.UI.switchVisualContent('mapContent');
        
        // 初始化地图
        if (!window.MockMap.map) {
            window.MockMap.init();
        }
        
        // 定位地址
        const address = window.AppState.getSessionData('userAddress');
        if (address) {
            const located = window.MockMap.locateAddress(address);
            if (!located) {
                // 地址定位失败，触发兜底
                window.AppState.triggerFallback('address_not_found', 
                    window.AppConfig.messages.fallbacks.addressNotFound);
            }
        }
    },
    
    // 处理分析步骤
    handleAnalyzing() {
        window.UI.switchVisualContent('analysisContent');
        window.UI.showAnalysisAnimation();
        
        // 模拟分析过程
        setTimeout(() => {
            this.performAnalysis();
        }, window.AppConfig.ui.analysisStepDelay * 3);
    },
    
    // 执行分析计算
    performAnalysis() {
        const roofArea = window.AppState.getSessionData('roofArea');
        
        // 模拟屋顶复杂度判断
        const complexity = window.Calculator.suggestRoofComplexity(roofArea);
        window.AppState.updateSessionData('roofComplexity', complexity);
        
        // 模拟高能耗设施检测
        const hasHighEnergyFeatures = Math.random() > 0.7; // 30%概率有游泳池等
        window.AppState.updateSessionData('hasHighEnergyFeatures', hasHighEnergyFeatures);
        
        // 确定用户画像
        const userProfile = window.Calculator.suggestUserProfile(roofArea, hasHighEnergyFeatures);
        window.AppState.updateSessionData('userProfile', userProfile);
        
        // 计算最大容量
        const maxCapacityResult = window.Calculator.calculateMaxCapacity(roofArea, complexity);
        window.AppState.updateSessionData('maxCapacity', maxCapacityResult.maxCapacity);
        
        console.log('Analysis completed:', {
            roofArea,
            complexity,
            hasHighEnergyFeatures,
            userProfile,
            maxCapacity: maxCapacityResult.maxCapacity
        });
        
        // 埋点
        if (window.Analytics) {
            window.Analytics.track(window.AppConfig.analytics.events.ANALYSIS_COMPLETE, {
                roofArea,
                complexity,
                maxCapacity: maxCapacityResult.maxCapacity
            });
        }
        
        // 继续到3D模型步骤
        // window.AppState.transitionTo('MODEL_3D') 已在动画完成后调用
    },
    
    // 处理3D模型步骤
    handleModel3D() {
        window.UI.addMessage('bot', window.AppConfig.messages.modelReady);
        window.UI.switchVisualContent('modelContent');
        
        // 初始化3D场景
        setTimeout(() => {
            try {
                window.Mock3D.init();
                
                // 埋点
                if (window.Analytics) {
                    window.Analytics.track(window.AppConfig.analytics.events.MODEL_RENDERED);
                }
                
                // 3秒后自动进入方案步骤
                setTimeout(() => {
                    window.AppState.transitionTo('PLANS');
                }, 3000);
                
            } catch (error) {
                console.error('3D initialization failed:', error);
                window.AppState.triggerFallback('render_failed', 
                    window.AppConfig.messages.fallbacks.renderFailed);
            }
        }, 500);
    },
    
    // 处理方案步骤
    handlePlans() {
        window.UI.addMessage('bot', window.AppConfig.messages.plansReady);
        window.UI.switchVisualContent('plansContent');
        
        // 计算所有方案
        this.calculateAllPlans();
    },
    
    // 计算所有方案
    calculateAllPlans() {
        const roofArea = window.AppState.getSessionData('roofArea');
        const complexity = window.AppState.getSessionData('roofComplexity');
        const userProfile = window.AppState.getSessionData('userProfile');
        
        const allPlansData = [];
        
        window.AppConfig.plans.forEach(plan => {
            const result = window.Calculator.calculateCompletePlan(
                roofArea, complexity, plan, userProfile
            );
            
            if (result.success) {
                allPlansData.push(result);
            }
        });
        
        // 保存计算结果
        window.AppState.updateSessionData('allPlansData', allPlansData);
        
        // 渲染方案卡片
        window.UI.renderPlanCards(allPlansData);
        
        // 默认选择第一个方案
        if (allPlansData.length > 0) {
            setTimeout(() => {
                window.UI.selectPlan(allPlansData[0].plan.id);
            }, 500);
        }
    },
    
    // 处理价值展示步骤
    handleValue() {
        const selectedPlanId = window.AppState.getSessionData('selectedPlan');
        const allPlansData = window.AppState.getSessionData('allPlansData');
        
        const selectedPlanData = allPlansData.find(p => p.plan.id === selectedPlanId);
        
        if (selectedPlanData) {
            // 更新价值显示
            this.updateValueDisplay(selectedPlanId);
            
            // 显示价值消息
            const message = window.AppConfig.messages.valuePresentation.replace(
                '${amount}', 
                window.Calculator.formatNumber(selectedPlanData.economicBenefits.totalAnnualSavings, 'currency')
            );
            window.UI.addMessage('bot', message);
            
            // 埋点
            if (window.Analytics) {
                window.Analytics.track(window.AppConfig.analytics.events.VALUE_VIEWED, {
                    planId: selectedPlanId,
                    annualSavings: selectedPlanData.economicBenefits.totalAnnualSavings
                });
            }
            
            // 3秒后显示留资转化消息
            setTimeout(() => {
                this.showLeadConversion(selectedPlanData);
            }, 3000);
        }
    },
    
    // 更新价值显示
    updateValueDisplay(planId) {
        const allPlansData = window.AppState.getSessionData('allPlansData');
        const planData = allPlansData.find(p => p.plan.id === planId);
        
        if (planData) {
            window.UI.updateValueDisplay(planData);
            
            // 更新3D模型
            if (window.Mock3D.scene) {
                window.Mock3D.updatePlan(planId);
            }
        }
    },
    
    // 显示留资转化
    showLeadConversion(planData) {
        const subsidyAmount = planData.subsidy;
        const message = window.AppConfig.messages.leadConversion.replace(
            '${subsidy}', 
            window.Calculator.formatNumber(subsidyAmount, 'currency')
        );
        
        window.UI.addMessage('bot', message);
        
        // 显示留资按钮
        const leadButtonHtml = `
            <div class="lead-conversion-actions">
                <button class="btn btn-primary btn-full" onclick="window.Flows.openLeadForm(${subsidyAmount})">
                    立即获取完整报告
                </button>
            </div>
        `;
        
        window.UI.elements.chatInputArea.innerHTML = leadButtonHtml;
    },
    
    // 打开留资表单
    openLeadForm(subsidyAmount = 0) {
        window.AppState.transitionTo('LEAD_FORM');
        window.UI.showLeadForm(subsidyAmount);
    },
    
    // 处理留资表单步骤
    handleLeadForm() {
        // UI 已处理表单显示
        console.log('Lead form step handled');
    },
    
    // 处理完成步骤
    handleDone() {
        window.UI.addMessage('bot', '感谢您的信任！我们将尽快与您联系。');
        console.log('Flow completed');
    },
    
    // 处理兜底情况
    handleFallback(type, reason) {
        console.log(`Handling fallback: ${type}`, reason);
        
        let fallbackMessage = '';
        
        switch (type) {
            case 'address_not_found':
                fallbackMessage = window.AppConfig.messages.fallbacks.addressNotFound;
                break;
            case 'image_not_clear':
                fallbackMessage = window.AppConfig.messages.fallbacks.imageNotClear;
                break;
            case 'area_too_big':
                fallbackMessage = window.AppConfig.messages.fallbacks.areaTooBig;
                break;
            case 'area_too_small':
                fallbackMessage = window.AppConfig.messages.fallbacks.areaTooSmall;
                break;
            case 'render_failed':
                fallbackMessage = window.AppConfig.messages.fallbacks.renderFailed;
                // 直接跳转到方案步骤
                setTimeout(() => {
                    window.AppState.transitionTo('PLANS');
                }, 2000);
                break;
            default:
                fallbackMessage = '遇到了一些技术问题，让我们的专业顾问为您提供帮助。';
        }
        
        window.UI.showFallbackMessage(type, fallbackMessage);
    },
    
    // 处理用户响应超时
    handleTimeout() {
        const timeoutMessage = window.AppConfig.messages.fallbacks.timeout;
        window.UI.addMessage('bot', timeoutMessage);
        
        // 显示快速留资选项
        const timeoutActions = `
            <div class="timeout-actions">
                <button class="btn btn-primary" onclick="window.Flows.openLeadForm()">
                    获取专业顾问支持
                </button>
                <button class="btn btn-secondary" onclick="location.reload()">
                    重新开始
                </button>
            </div>
        `;
        
        window.UI.elements.chatInputArea.innerHTML = timeoutActions;
        
        // 埋点
        if (window.Analytics) {
            window.Analytics.track(window.AppConfig.analytics.events.FALLBACK_TRIGGERED, {
                type: 'timeout',
                sessionTime: Date.now() - window.AppState.sessionData.startTime
            });
        }
    },
    
    // 检查是否已有面板（模拟）
    checkExistingPanels() {
        // 模拟已有面板检测 - 实际应该由LLM视觉分析
        const hasExisting = Math.random() > 0.9; // 10%概率已有面板
        
        if (hasExisting) {
            window.AppState.updateSessionData('hasExistingPanels', true);
            this.handleExistingPanelsFlow();
            return true;
        }
        
        return false;
    },
    
    // 处理已有面板流程
    handleExistingPanelsFlow() {
        const message = '检测到您的屋顶已安装太阳能面板。我们为您推荐储能系统升级方案。';
        window.UI.addMessage('bot', message);
        
        // 显示储能升级选项
        const upgradeOptions = `
            <div class="upgrade-options">
                <button class="btn btn-primary" onclick="window.Flows.showBatteryUpgrade()">
                    查看储能升级方案
                </button>
                <button class="btn btn-secondary" onclick="window.Flows.continueAsNewInstall()">
                    按新装系统试算
                </button>
            </div>
        `;
        
        window.UI.elements.chatInputArea.innerHTML = upgradeOptions;
    },
    
    // 显示储能升级方案
    showBatteryUpgrade() {
        window.UI.addMessage('user', '查看储能升级方案');
        window.UI.addMessage('bot', '根据您的屋顶情况，我们推荐以下储能配置：');
        
        // 简化的储能方案
        const batteryOptions = [
            { capacity: '10 kWh', price: '$8,000 - $10,000', description: '满足基础夜间用电' },
            { capacity: '13.5 kWh', price: '$10,000 - $13,000', description: '应对高耗能设备' },
            { capacity: '20 kWh', price: '$15,000 - $18,000', description: '长时间备用电源' }
        ];
        
        let optionsHtml = '<div class="battery-options">';
        batteryOptions.forEach((option, index) => {
            optionsHtml += `
                <div class="battery-option card">
                    <div class="card-body">
                        <h4>${option.capacity} 储能系统</h4>
                        <p>${option.description}</p>
                        <div class="price">${option.price}</div>
                    </div>
                </div>
            `;
        });
        optionsHtml += '</div>';
        
        optionsHtml += `
            <div class="upgrade-actions">
                <button class="btn btn-primary" onclick="window.Flows.openLeadForm()">
                    获取详细储能方案
                </button>
            </div>
        `;
        
        window.UI.elements.chatInputArea.innerHTML = optionsHtml;
    },
    
    // 继续按新装处理
    continueAsNewInstall() {
        window.UI.addMessage('user', '按新装系统试算');
        window.AppState.updateSessionData('hasExistingPanels', false);
        window.AppState.transitionTo('ANALYZING');
    }
};

// 全局工具函数
window.Flows.utils = {
    // 格式化时间
    formatDuration(milliseconds) {
        const seconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(seconds / 60);
        
        if (minutes > 0) {
            return `${minutes}分${seconds % 60}秒`;
        }
        return `${seconds}秒`;
    },
    
    // 生成会话ID
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    },
    
    // 验证联系方式格式
    validateContact(contact) {
        // 简单的手机号或邮箱验证
        const phoneRegex = /^1[3-9]\d{9}$/;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        return phoneRegex.test(contact) || emailRegex.test(contact);
    }
};
