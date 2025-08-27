// UI 渲染和交互模块
window.UI = {
    
    // DOM 元素引用
    elements: {
        chatMessages: null,
        chatInputArea: null,
        visualContainer: null,
        progressSteps: null,
        progressFill: null,
        drawerOverlay: null,
        leadForm: null
    },
    
    // 初始化 UI
    init() {
        this.elements.chatMessages = document.getElementById('chatMessages');
        this.elements.chatInputArea = document.getElementById('chatInputArea');
        this.elements.visualContainer = document.getElementById('visualContainer');
        this.elements.progressSteps = document.querySelectorAll('.step');
        this.elements.progressFill = document.querySelector('.progress-fill');
        this.elements.drawerOverlay = document.getElementById('drawerOverlay');
        this.elements.leadForm = document.getElementById('leadForm');
        
        this.bindEvents();
        this.showWelcomeMessage();
    },
    
    // 绑定事件
    bindEvents() {
        // 留资表单事件
        if (this.elements.leadForm) {
            this.elements.leadForm.addEventListener('submit', this.handleLeadFormSubmit.bind(this));
        }
        
        // 抽屉关闭事件
        const drawerClose = document.getElementById('drawerClose');
        if (drawerClose) {
            drawerClose.addEventListener('click', this.closeDrawer.bind(this));
        }
        
        // 点击遮罩关闭抽屉
        if (this.elements.drawerOverlay) {
            this.elements.drawerOverlay.addEventListener('click', (e) => {
                if (e.target === this.elements.drawerOverlay) {
                    this.closeDrawer();
                }
            });
        }
    },
    
    // 显示欢迎消息
    showWelcomeMessage() {
        this.addMessage('bot', window.AppConfig.messages.welcome);
        this.showAddressInput();
    },
    
    // 添加聊天消息
    addMessage(type, content, options = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        
        if (options.typing) {
            this.typeWriter(bubbleDiv, content, options.callback);
        } else {
            bubbleDiv.innerHTML = content;
            if (options.callback) options.callback();
        }
        
        if (options.showTime !== false) {
            const timeDiv = document.createElement('div');
            timeDiv.className = 'message-time';
            timeDiv.textContent = new Date().toLocaleTimeString('zh-CN', {
                hour: '2-digit',
                minute: '2-digit'
            });
            bubbleDiv.appendChild(timeDiv);
        }
        
        messageDiv.appendChild(bubbleDiv);
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    },
    
    // 打字机效果
    typeWriter(element, text, callback, speed = window.AppConfig.ui.typingSpeed) {
        let i = 0;
        const timer = setInterval(() => {
            element.innerHTML = text.slice(0, i + 1);
            i++;
            if (i >= text.length) {
                clearInterval(timer);
                if (callback) callback();
            }
        }, speed);
    },
    
    // 滚动到底部
    scrollToBottom() {
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    },
    
    // 显示地址输入
    showAddressInput() {
        const inputHtml = `
            <div class="input-group">
                <input type="text" 
                       class="input-field" 
                       id="addressInput" 
                       placeholder="请输入您的家庭住址..."
                       autocomplete="street-address">
                <button class="btn btn-primary" id="submitAddress">开始分析</button>
            </div>
        `;
        
        this.elements.chatInputArea.innerHTML = inputHtml;
        
        const addressInput = document.getElementById('addressInput');
        const submitButton = document.getElementById('submitAddress');
        
        // 绑定事件
        addressInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleAddressSubmit();
            }
        });
        
        submitButton.addEventListener('click', this.handleAddressSubmit.bind(this));
        
        // 自动聚焦
        addressInput.focus();
    },
    
    // 处理地址提交
    handleAddressSubmit() {
        const addressInput = document.getElementById('addressInput');
        const address = addressInput.value.trim();
        
        if (!address) {
            this.showError('请输入有效的地址');
            return;
        }
        
        // 添加用户消息
        this.addMessage('user', address);
        
        // 更新状态
        window.AppState.updateSessionData('userAddress', address);
        
        // 埋点
        if (window.Analytics) {
            window.Analytics.track(window.AppConfig.analytics.events.ADDRESS_INPUT, {
                address: address
            });
        }
        
        // 清空输入区域
        this.elements.chatInputArea.innerHTML = '';
        
        // 转换到地图确认步骤
        window.AppState.transitionTo('MAP_CONFIRM');
    },
    
    // 显示错误消息
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        errorDiv.textContent = message;
        
        // 移除之前的错误消息
        const existingError = this.elements.chatInputArea.querySelector('.form-error');
        if (existingError) {
            existingError.remove();
        }
        
        this.elements.chatInputArea.appendChild(errorDiv);
        
        // 3秒后自动移除
        setTimeout(() => {
            errorDiv.remove();
        }, 3000);
    },
    
    // 更新步骤进度
    updateStep(step) {
        const stepOrder = Object.keys(window.AppState.STEPS);
        const currentIndex = stepOrder.indexOf(step);
        
        this.elements.progressSteps.forEach((stepEl, index) => {
            stepEl.classList.remove('active', 'completed');
            
            if (index < currentIndex) {
                stepEl.classList.add('completed');
            } else if (index === currentIndex) {
                stepEl.classList.add('active');
            }
        });
    },
    
    // 更新进度条
    updateProgress(percentage) {
        if (this.elements.progressFill) {
            this.elements.progressFill.style.width = `${percentage}%`;
        }
    },
    
    // 切换可视化内容
    switchVisualContent(contentId) {
        const allContents = this.elements.visualContainer.querySelectorAll('.visual-content');
        allContents.forEach(content => {
            content.classList.remove('active');
        });
        
        const targetContent = document.getElementById(contentId);
        if (targetContent) {
            targetContent.classList.add('active');
        }
    },
    
    // 显示分析动画
    showAnalysisAnimation() {
        this.switchVisualContent('analysisContent');
        
        const steps = ['step1', 'step2', 'step3'];
        const progressBar = document.getElementById('analysisProgress');
        
        let currentStep = 0;
        const animateStep = () => {
            if (currentStep < steps.length) {
                const stepElement = document.getElementById(steps[currentStep]);
                stepElement.classList.add('completed');
                stepElement.querySelector('.step-icon').textContent = '✓';
                
                // 更新进度条
                const progress = ((currentStep + 1) / steps.length) * 100;
                progressBar.style.width = `${progress}%`;
                
                currentStep++;
                setTimeout(animateStep, window.AppConfig.ui.analysisStepDelay);
            } else {
                // 分析完成，转换到3D模型
                setTimeout(() => {
                    window.AppState.transitionTo('MODEL_3D');
                }, 1000);
            }
        };
        
        // 开始动画
        setTimeout(animateStep, 500);
    },
    
    // 渲染方案卡片
    renderPlanCards(plans, selectedPlanId = null) {
        const plansGrid = document.getElementById('plansGrid');
        if (!plansGrid) return;
        
        plansGrid.innerHTML = '';
        
        plans.forEach(planData => {
            const card = document.createElement('div');
            card.className = `card plan-card ${planData.plan.id === selectedPlanId ? 'selected' : ''}`;
            card.dataset.planId = planData.plan.id;
            
            card.innerHTML = `
                <div class="card-body">
                    <div class="plan-title">${planData.plan.name}</div>
                    <div class="plan-description">${planData.plan.description}</div>
                    <div class="plan-specs">
                        <div class="plan-spec">
                            <span class="plan-spec-label">系统容量</span>
                            <span class="plan-spec-value">${planData.systemConfig.systemCapacity.toFixed(1)} kW</span>
                        </div>
                        <div class="plan-spec">
                            <span class="plan-spec-label">面板数量</span>
                            <span class="plan-spec-value">${planData.systemConfig.panelCount} 块</span>
                        </div>
                        ${planData.systemConfig.hasBattery ? `
                        <div class="plan-spec">
                            <span class="plan-spec-label">储能电池</span>
                            <span class="plan-spec-value">${planData.systemConfig.batteryCapacity} kWh</span>
                        </div>
                        ` : ''}
                    </div>
                    <div class="plan-price">${planData.pricing.priceRange}</div>
                </div>
            `;
            
            // 绑定点击事件
            card.addEventListener('click', () => {
                this.selectPlan(planData.plan.id);
            });
            
            plansGrid.appendChild(card);
        });
    },
    
    // 选择方案
    selectPlan(planId) {
        // 更新UI选中状态
        const allCards = document.querySelectorAll('.plan-card');
        allCards.forEach(card => {
            card.classList.remove('selected');
            if (card.dataset.planId === planId) {
                card.classList.add('selected');
            }
        });
        
        // 更新状态
        window.AppState.updateSessionData('selectedPlan', planId);
        
        // 埋点
        if (window.Analytics) {
            window.Analytics.track(window.AppConfig.analytics.events.PLAN_SELECTED, {
                planId: planId
            });
        }
        
        // 触发3D模型更新和价值计算
        if (window.Mock3D) {
            window.Mock3D.updatePlan(planId);
        }
        
        if (window.Flows) {
            window.Flows.updateValueDisplay(planId);
        }
    },
    
    // 更新价值显示
    updateValueDisplay(calculatedData) {
        const valueAmount = document.getElementById('valueAmount');
        const valueDetails = document.getElementById('valueDetails');
        
        if (valueAmount) {
            this.animateValue(valueAmount, calculatedData.economicBenefits.totalAnnualSavings, 'currency');
        }
        
        if (valueDetails) {
            valueDetails.innerHTML = `
                <div class="value-detail-grid">
                    <div class="value-detail">
                        <span class="detail-label">年发电量</span>
                        <span class="detail-value">${window.Calculator.formatNumber(calculatedData.economicBenefits.annualGeneration, 'kwh')}</span>
                    </div>
                    <div class="value-detail">
                        <span class="detail-label">自用率</span>
                        <span class="detail-value">${calculatedData.economicBenefits.selfUseRate}%</span>
                    </div>
                    <div class="value-detail">
                        <span class="detail-label">投资回收期</span>
                        <span class="detail-value">${calculatedData.economicBenefits.paybackPeriod} 年</span>
                    </div>
                    <div class="value-detail">
                        <span class="detail-label">政府补贴</span>
                        <span class="detail-value">${window.Calculator.formatNumber(calculatedData.subsidy, 'currency')}</span>
                    </div>
                </div>
            `;
        }
    },
    
    // 数字动画
    animateValue(element, targetValue, format = 'number') {
        const startValue = 0;
        const duration = window.AppConfig.ui.valueCounterDuration;
        const startTime = Date.now();
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // 使用缓动函数
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = startValue + (targetValue - startValue) * easeOutQuart;
            
            element.textContent = window.Calculator.formatNumber(Math.round(currentValue), format);
            element.classList.add('updating');
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.classList.remove('updating');
            }
        };
        
        animate();
    },
    
    // 显示留资抽屉
    showLeadForm(subsidyAmount = 0) {
        const subsidyElement = document.getElementById('subsidyAmount');
        if (subsidyElement) {
            subsidyElement.textContent = window.Calculator.formatNumber(subsidyAmount, 'currency');
        }
        
        this.elements.drawerOverlay.classList.add('active');
        
        // 埋点
        if (window.Analytics) {
            window.Analytics.track(window.AppConfig.analytics.events.LEAD_FORM_OPENED, {
                subsidyAmount: subsidyAmount
            });
        }
        
        // 聚焦第一个输入框
        setTimeout(() => {
            const firstInput = this.elements.leadForm.querySelector('input');
            if (firstInput) firstInput.focus();
        }, 300);
    },
    
    // 关闭抽屉
    closeDrawer() {
        this.elements.drawerOverlay.classList.remove('active');
    },
    
    // 处理留资表单提交
    handleLeadFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(this.elements.leadForm);
        const leadData = {
            name: formData.get('name'),
            contact: formData.get('contact'),
            preferredTime: formData.get('preferredTime'),
            address: window.AppState.getSessionData('userAddress'),
            selectedPlan: window.AppState.getSessionData('selectedPlan'),
            sessionSummary: window.AppState.getSessionSummary()
        };
        
        // 简单验证
        if (!leadData.name || !leadData.contact) {
            this.showError('请填写必填信息');
            return;
        }
        
        // 模拟提交
        console.log('Lead form submitted:', leadData);
        
        // 埋点
        if (window.Analytics) {
            window.Analytics.track(window.AppConfig.analytics.events.LEAD_FORM_SUBMITTED, leadData);
        }
        
        // 显示成功消息
        this.showSubmitSuccess();
        
        // 转换到完成状态
        window.AppState.transitionTo('DONE');
    },
    
    // 显示提交成功
    showSubmitSuccess() {
        const successHtml = `
            <div class="success-message">
                <h3>提交成功！</h3>
                <p>我们的专业顾问将在24小时内与您联系，为您提供详细的太阳能方案和准确报价。</p>
                <button class="btn btn-primary" onclick="location.reload()">重新开始</button>
            </div>
        `;
        
        this.elements.drawerOverlay.querySelector('.drawer-body').innerHTML = successHtml;
    },
    
    // 重置UI
    reset() {
        this.elements.chatMessages.innerHTML = '';
        this.elements.chatInputArea.innerHTML = '';
        this.switchVisualContent('welcomeContent');
        this.updateStep('WELCOME');
        this.updateProgress(0);
        this.closeDrawer();
    },
    
    // 显示兜底消息
    showFallbackMessage(type, message) {
        this.addMessage('bot', message);
        
        // 根据兜底类型显示不同的操作选项
        const fallbackActions = this.getFallbackActions(type);
        if (fallbackActions) {
            this.elements.chatInputArea.innerHTML = fallbackActions;
        }
    },
    
    // 获取兜底操作按钮
    getFallbackActions(type) {
        switch (type) {
            case 'address_not_found':
                return `
                    <div class="fallback-actions">
                        <button class="btn btn-secondary" onclick="window.UI.showAddressInput()">重新输入地址</button>
                        <button class="btn btn-primary" onclick="window.UI.showLeadForm()">联系专业顾问</button>
                    </div>
                `;
            case 'area_too_big':
            case 'area_too_small':
                return `
                    <div class="fallback-actions">
                        <button class="btn btn-primary" onclick="window.UI.showLeadForm()">获取人工评估</button>
                    </div>
                `;
            default:
                return `
                    <div class="fallback-actions">
                        <button class="btn btn-primary" onclick="window.UI.showLeadForm()">联系我们</button>
                    </div>
                `;
        }
    }
};

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    window.UI.init();
});
