// 配置文件
window.AppConfig = {
    // 计算参数
    calculation: {
        panelArea: 1.9, // 单块面板面积 (m²)
        panelPower: 0.45, // 单块面板功率 (kW)
        sunHours: 4.18, // 年均等效日照小时
        gridPrice: 0.30, // 电网电价 (AUD/kWh)
        feedInPrice: 0.07, // 上网电价 (AUD/kWh)
        selfUseRateNoBattery: 0.30, // 无电池自用率
        selfUseRateWithBattery: 0.85, // 有电池自用率
        priceVariation: 0.10, // 报价浮动范围 (±10%)
        
        // 屋顶可用系数
        roofFactors: {
            flat: 0.80,     // 平面屋顶
            simple: 0.50,   // 简单屋顶 (2-4个大坡面)
            complex: 0.35   // 复杂屋顶 (多个小坡面、老虎窗等)
        },
        
        // 用户画像与年用电量 (kWh)
        userProfiles: {
            basic: 5000,      // 基础型
            standard: 7500,   // 标准型
            highConsumption: 10000,  // 高耗能型
            ultraHigh: 15000  // 超高能耗型
        }
    },
    
    // 方案配置
    plans: [
        {
            id: 'smart_saving',
            name: '智慧节省',
            description: '光伏面板（数量低配）+ 逆变器',
            capacityRatio: 0.4, // 相对于最大容量的比例
            hasBattery: false,
            batteryCapacity: 0,
            basePrice: 8000, // 基础价格 (AUD)
            pricePerKw: 1200 // 每kW价格 (AUD)
        },
        {
            id: 'high_efficiency',
            name: '高效能源',
            description: '光伏面板（数量高配）+ 逆变器',
            capacityRatio: 0.7,
            hasBattery: false,
            batteryCapacity: 0,
            basePrice: 12000,
            pricePerKw: 1200
        },
        {
            id: 'energy_independence',
            name: '能源独立',
            description: '光伏面板（数量高配）+ 混合逆变器 + 储能电池',
            capacityRatio: 0.7,
            hasBattery: true,
            batteryCapacity: 10, // kWh
            basePrice: 18000,
            pricePerKw: 1200,
            batteryPrice: 1000 // 每kWh电池价格
        },
        {
            id: 'ultimate_energy',
            name: '终极能源',
            description: '光伏面板（满配）+ 混合逆变器 + 大容量储能',
            capacityRatio: 1.0,
            hasBattery: true,
            batteryCapacity: 13.5,
            basePrice: 25000,
            pricePerKw: 1200,
            batteryPrice: 1000
        }
    ],
    
    // 地图配置
    map: {
        defaultCenter: [-27.4698, 153.0251], // 布里斯班坐标
        defaultZoom: 15,
        maxZoom: 20,
        minZoom: 10,
        // 卫星图瓦片源 (Esri World Imagery - 仅用于演示)
        satelliteTileUrl: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    },
    
    // UI 配置
    ui: {
        animationDuration: 300, // 动画持续时间 (ms)
        typingSpeed: 50, // 打字机效果速度 (ms/字符)
        analysisStepDelay: 1500, // 分析步骤间隔 (ms)
        valueCounterDuration: 2000, // 数字滚动持续时间 (ms)
        
        // 兜底阈值
        thresholds: {
            minRoofArea: 20, // 最小屋顶面积 (m²)
            maxRoofArea: 450, // 最大屋顶面积 (m²)
            responseTimeout: 30000 // 用户响应超时 (ms)
        }
    },
    
    // 文案配置
    messages: {
        welcome: "你好！我是你的 AI 太阳能顾问。输入地址，60 秒带你看清自家潜力。",
        addressConfirm: "我已定位到该区域，请在地图上点击你的屋顶（或拖动框选）。",
        analyzing: "正在分析屋顶面积 / 日照情况 / 高能耗设施…这就像魔法一样！",
        modelReady: "分析完成！这是为你生成的 3D 模型。你的屋顶可用性很不错，我们来看看方案吧。",
        plansReady: "我为你准备了 4 个配置档。点击任意卡片，3D 模型会实时变化。",
        valuePresentation: "在该方案下，预计年节省约 ${amount}（含上网收益）。下方可查看详细计算假设。",
        leadConversion: "你可能还可申请约 ${subsidy} 的政府补贴。想看包含补贴的最终价格吗？留下联系方式，我立刻把完整报告发给你。",
        
        // 兜底文案
        fallbacks: {
            addressNotFound: "没找到该地址，能否换一个写法或发送附近地标？",
            imageNotClear: "我需要更清晰的屋顶图来继续计算。你可以放大后重新圈选，或留下联系方式，我们提供人工免费评估。",
            areaTooBig: "您的屋顶面积较大，需要高级顾问进行定制化方案设计。",
            areaTooSmall: "检测到的屋顶面积较小，可能不具备安装价值。请重新圈选或联系我们进行人工评估。",
            renderFailed: "模型生成异常，不影响方案计算。",
            timeout: "需要帮助吗？点击下方按钮获取专业顾问支持。"
        }
    },
    
    // 补贴配置
    subsidy: {
        enabled: true,
        baseAmount: 3500, // 基础补贴金额 (AUD)
        perKwAmount: 200, // 每kW额外补贴 (AUD)
        maxAmount: 8000   // 最大补贴金额 (AUD)
    },
    
    // 埋点事件配置
    analytics: {
        enabled: true,
        events: {
            PAGE_LOAD: 'page_load',
            STEP_ENTER: 'step_enter',
            ADDRESS_INPUT: 'address_input',
            ROOF_SELECTED: 'roof_selected',
            ANALYSIS_COMPLETE: 'analysis_complete',
            MODEL_RENDERED: 'model_rendered',
            PLAN_SELECTED: 'plan_selected',
            VALUE_VIEWED: 'value_viewed',
            LEAD_FORM_OPENED: 'lead_form_opened',
            LEAD_FORM_SUBMITTED: 'lead_form_submitted',
            FALLBACK_TRIGGERED: 'fallback_triggered',
            ERROR_OCCURRED: 'error_occurred'
        }
    },
    
    // 开发模式配置
    debug: {
        enabled: true, // 开启调试模式
        skipAnimations: false, // 跳过动画
        mockData: true, // 使用模拟数据
        logLevel: 'info' // 日志级别: 'debug', 'info', 'warn', 'error'
    }
};
