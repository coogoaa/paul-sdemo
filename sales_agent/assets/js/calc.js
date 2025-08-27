// 计算逻辑模块
window.Calculator = {
    
    // 计算屋顶最大容量
    calculateMaxCapacity(roofArea, complexity = 'simple') {
        const config = window.AppConfig.calculation;
        const factor = config.roofFactors[complexity] || config.roofFactors.simple;
        
        // 计算最大面板数量
        const maxPanels = Math.floor((roofArea * factor) / config.panelArea);
        
        // 计算最大系统容量 (kW)
        const maxCapacity = maxPanels * config.panelPower;
        
        return {
            maxPanels: maxPanels,
            maxCapacity: maxCapacity,
            usableArea: roofArea * factor,
            factor: factor
        };
    },
    
    // 根据方案计算系统配置
    calculatePlanConfig(maxCapacity, plan) {
        const config = window.AppConfig.calculation;
        
        // 计算该方案的系统容量
        const systemCapacity = maxCapacity * plan.capacityRatio;
        const panelCount = Math.floor(systemCapacity / config.panelPower);
        
        // 计算逆变器功率 (容配比 1:1.1)
        const inverterPower = systemCapacity * 1.1;
        
        return {
            systemCapacity: systemCapacity,
            panelCount: panelCount,
            inverterPower: inverterPower,
            hasBattery: plan.hasBattery,
            batteryCapacity: plan.batteryCapacity || 0
        };
    },
    
    // 计算经济效益
    calculateEconomicBenefits(systemConfig, userProfile = 'standard') {
        const config = window.AppConfig.calculation;
        
        // 获取用户年用电量
        const annualConsumption = config.userProfiles[userProfile] || config.userProfiles.standard;
        
        // 计算年发电量
        const annualGeneration = systemConfig.systemCapacity * config.sunHours * 365;
        
        // 计算自用率和自用电量
        const selfUseRate = systemConfig.hasBattery ? 
            config.selfUseRateWithBattery : config.selfUseRateNoBattery;
        const annualSelfUse = Math.min(annualGeneration * selfUseRate, annualConsumption);
        
        // 计算上网电量
        const annualFeedIn = annualGeneration - annualSelfUse;
        
        // 计算节省金额
        const savingsFromSelfUse = annualSelfUse * config.gridPrice;
        const incomeFromFeedIn = annualFeedIn * config.feedInPrice;
        const totalAnnualSavings = savingsFromSelfUse + incomeFromFeedIn;
        
        return {
            annualGeneration: Math.round(annualGeneration),
            annualSelfUse: Math.round(annualSelfUse),
            annualFeedIn: Math.round(annualFeedIn),
            selfUseRate: Math.round(selfUseRate * 100),
            savingsFromSelfUse: Math.round(savingsFromSelfUse),
            incomeFromFeedIn: Math.round(incomeFromFeedIn),
            totalAnnualSavings: Math.round(totalAnnualSavings),
            paybackPeriod: 0 // 将在计算价格后更新
        };
    },
    
    // 计算系统价格
    calculateSystemPrice(systemConfig, plan) {
        const config = window.AppConfig.calculation;
        
        // 基础硬件成本
        let hardwareCost = plan.basePrice + (systemConfig.systemCapacity * plan.pricePerKw);
        
        // 电池成本
        if (systemConfig.hasBattery && plan.batteryPrice) {
            hardwareCost += systemConfig.batteryCapacity * plan.batteryPrice;
        }
        
        // 辅材及安装费
        const installationCost = 1500 + (systemConfig.systemCapacity * 150);
        
        // 总成本
        const totalCost = hardwareCost + installationCost;
        
        // 价格区间 (±10%)
        const priceVariation = config.priceVariation;
        const minPrice = Math.round(totalCost * (1 - priceVariation));
        const maxPrice = Math.round(totalCost * (1 + priceVariation));
        
        return {
            hardwareCost: Math.round(hardwareCost),
            installationCost: Math.round(installationCost),
            totalCost: Math.round(totalCost),
            minPrice: minPrice,
            maxPrice: maxPrice,
            priceRange: `$${minPrice.toLocaleString()} - $${maxPrice.toLocaleString()}`
        };
    },
    
    // 计算政府补贴
    calculateSubsidy(systemCapacity) {
        const subsidyConfig = window.AppConfig.subsidy;
        
        if (!subsidyConfig.enabled) {
            return 0;
        }
        
        // 基础补贴 + 容量补贴
        const calculatedSubsidy = subsidyConfig.baseAmount + 
            (systemCapacity * subsidyConfig.perKwAmount);
        
        // 不超过最大补贴金额
        return Math.min(calculatedSubsidy, subsidyConfig.maxAmount);
    },
    
    // 计算投资回收期
    calculatePaybackPeriod(totalCost, annualSavings, subsidy = 0) {
        const netCost = totalCost - subsidy;
        if (annualSavings <= 0) return 0;
        
        return Math.round((netCost / annualSavings) * 10) / 10; // 保留1位小数
    },
    
    // 综合计算方案
    calculateCompletePlan(roofArea, complexity, plan, userProfile = 'standard') {
        try {
            // 1. 计算最大容量
            const maxCapacityResult = this.calculateMaxCapacity(roofArea, complexity);
            
            // 2. 计算方案配置
            const systemConfig = this.calculatePlanConfig(maxCapacityResult.maxCapacity, plan);
            
            // 3. 计算经济效益
            const economicBenefits = this.calculateEconomicBenefits(systemConfig, userProfile);
            
            // 4. 计算价格
            const pricing = this.calculateSystemPrice(systemConfig, plan);
            
            // 5. 计算补贴
            const subsidy = this.calculateSubsidy(systemConfig.systemCapacity);
            
            // 6. 计算投资回收期
            const paybackPeriod = this.calculatePaybackPeriod(
                pricing.totalCost, 
                economicBenefits.totalAnnualSavings, 
                subsidy
            );
            
            // 更新经济效益中的投资回收期
            economicBenefits.paybackPeriod = paybackPeriod;
            
            return {
                success: true,
                roofAnalysis: maxCapacityResult,
                systemConfig: systemConfig,
                economicBenefits: economicBenefits,
                pricing: pricing,
                subsidy: Math.round(subsidy),
                plan: plan
            };
            
        } catch (error) {
            console.error('Calculation error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    },
    
    // 验证输入参数
    validateInputs(roofArea, complexity, plan) {
        const errors = [];
        
        if (!roofArea || roofArea <= 0) {
            errors.push('屋顶面积必须大于0');
        }
        
        if (roofArea < window.AppConfig.ui.thresholds.minRoofArea) {
            errors.push(`屋顶面积过小（最小${window.AppConfig.ui.thresholds.minRoofArea}m²）`);
        }
        
        if (roofArea > window.AppConfig.ui.thresholds.maxRoofArea) {
            errors.push(`屋顶面积过大（最大${window.AppConfig.ui.thresholds.maxRoofArea}m²）`);
        }
        
        if (!['flat', 'simple', 'complex'].includes(complexity)) {
            errors.push('屋顶复杂度参数无效');
        }
        
        if (!plan || !plan.id) {
            errors.push('方案参数无效');
        }
        
        return {
            isValid: errors.length === 0,
            errors: errors
        };
    },
    
    // 格式化数字显示
    formatNumber(value, type = 'number') {
        if (typeof value !== 'number' || isNaN(value)) {
            return '0';
        }
        
        switch (type) {
            case 'currency':
                return `$${value.toLocaleString()}`;
            case 'percentage':
                return `${value}%`;
            case 'kwh':
                return `${value.toLocaleString()} kWh`;
            case 'kw':
                return `${value.toFixed(1)} kW`;
            case 'years':
                return `${value} 年`;
            default:
                return value.toLocaleString();
        }
    },
    
    // 获取用户画像建议
    suggestUserProfile(roofArea, hasHighEnergyFeatures = false) {
        if (hasHighEnergyFeatures) {
            return roofArea > 200 ? 'ultraHigh' : 'highConsumption';
        }
        
        if (roofArea < 50) return 'basic';
        if (roofArea < 100) return 'standard';
        if (roofArea < 200) return 'highConsumption';
        return 'ultraHigh';
    },
    
    // 获取屋顶复杂度建议（模拟LLM判断）
    suggestRoofComplexity(roofArea) {
        // 简化的复杂度判断逻辑（实际应该由LLM视觉分析）
        if (roofArea < 80) return 'simple';
        if (roofArea > 300) return 'complex';
        return Math.random() > 0.7 ? 'complex' : 'simple'; // 模拟随机判断
    }
};

// 调试模式下暴露到全局
if (window.AppConfig && window.AppConfig.debug.enabled) {
    window.debugCalculator = window.Calculator;
}
