

##### **3.2 运营后台能力建设**

###### **3.2.1 线上数据自助批量导出**
*   **现状:** 运营和产品团队无法自主获取线上数据，依赖开发手动导出，效率低下。
*   **需求:**
    1.  **功能界面:**
        *   在运营后台创建一个“数据导出”页面。
        *   提供一个日期范围选择器，允许用户根据**项目创建时间**筛选数据。
        *   提供一个“导出CSV”按钮。
    2.  **导出字段:**
        *   导出的 CSV 文件需包含以下字段，其中“新增”字段为本次 3.1.2 需求中增加的字段。

| 字段名 (建议) | 描述 |
| :--- | :--- |
| `project_id` | 项目 ID |
| `initial_address` | 用户输入的原始地址 |
| `analysis_formatted_address` | **(新增)** 实际进行 AI 分析的地址 |
| `analysis_coordinates` | **(新增)** 实际进行 AI 分析的坐标 (经纬度) |
| `map_link` | 提交 AI 分析后绘制边框的地图地址 |
| `sketch_map_link` | 提供给 GS 创建项目的地图 |
| `type` | 新建系统或储能扩容 |
| `design_id` | 方案设计ID |
| `design_type` | 对应的方案 (e.g., The Rebate Maximiser) |
| `system_size_kw` | 方案生成的系统容量 (kW) |
| `upfront_investment_max` | 方案投入金额-高值 (AUD) |
| `upfront_investment_min` | 方案投入金额-低值 (AUD) |
| `upfront_investment_base` | 方案投入金额-计算基准值 (AUD) |
| `subsidy` | 补贴金额 (AUD) |
| `annual_bill_savings_max` | 年度节省-高值 (AUD) |
| `annual_bill_savings_min` | 年度节省-低值 (AUD) |
| `annual_bill_savings_base` | 年度节省-计算基准值 (AUD) |
| `irr_percent` | 内部收益率 IRR (%) |
| `payback_period_max_years` | 回本周期-高值 (年) |
| `payback_period_min_years` | 回本周期-低值 (年) |
| `payback_period_base_years` | 回本周期-计算基准值 (年) |
| `battery_capacity_kwh` | 电池可用容量 (kWh) |
| `self_consumption_max_percent` | 自用率-高值 (%) |
| `self_consumption_min_percent` | 自用率-低值 (%) |
| `self_consumption_base_percent` | 自用率-计算基准值 (%) |
| `rendering_link` | 3D 房屋截图链接 |
| `card_link` | 分享卡片链接 |
| `user_name` | 留资姓名 |
| `email` | 留资邮箱 |
| `phone` | 留资电话 |
| `postcode` | 留资邮编 |
| `sketch_project_link` | GS项目链接 |
| `sketch_project_link` | GS项目链接 |

--
建议增加的筛选维度
线索类型 (Lead Type)
为什么需要： 这是最重要的业务分类维度。运营人员经常需要分析不同来源的线索质量和转化情况。例如，“正常流程留资”的数量和质量，直接反映了产品核心流程的健康度；而“兜底留资”的占比则能反映出AI识别的瓶颈在哪里。
如何实现： 一个简单的下拉菜单，包含以下选项：
全部类型 (默认)
初步提案 (Preliminary Proposal - 正常流程)
高价值线索 (High-Value Lead - 大面积)
未来机会 (Future Opportunity - 非澳地址)
需人工评估 (Manual Assessment - 其他兜底)
实用场景：
快速筛选出所有“高价值线索”进行重点跟进。
定期分析“需人工评估”的线索，找出共性问题，反哺产品优化。
留资状态 (Conversion Status)
为什么需要： 这是衡量最终业务成果的核心维度。运营人员需要快速区分哪些访问最终转化为了有效线索，哪些只是“游客”。
如何实现： 一个简单的下拉菜单，包含以下选项：
全部状态 (默认)
已留资 (Converted)
未留资 (Not Converted)
实用场景：
筛选“已留资”的数据，交付给销售团队或进行后续分析。
筛选“未留资”的数据，分析用户在哪个环节放弃，例如，查看他们的analysis_formatted_address和选择的design_type，可能会发现某些区域或某些方案类型的吸引力不足。
最终的筛选区设计 (建议)
综合来看，运营后台“数据导出”页面的筛选区可以设计成这样，非常简洁直观：
筛选器	类型	描述
项目创建时间	日期范围选择器	从 [YYYY-MM-DD] 到 [YYYY-MM-DD]
线索类型	下拉菜单	全部类型, 初步提案, 高价值线索, ...
留资状态	下拉菜单	全部状态, 已留资, 未留资
[ 搜索 / 筛选 ] [ 导出 CSV ]
————

###### **3.2.2 核心参数配置界面化**
*   **现状:** 核心业务参数硬编码或存储在配置文件中，调整流程繁琐且风险高。
*   **需求:**
    1.  **功能界面:**
        *   在运营后台创建一个“参数配置”页面。
        *   将所有核心参数按照类别进行分组展示，提供清晰的参数名、描述、输入框和单位说明。
        *   提供“保存”和“恢复默认值”按钮。
        *   对输入值进行校验（如数字范围、格式等），并提供友好的错误提示。
    2.  **需配置的参数列表:**

        *   **GIS参数**
            *   `min_2D_area_filter_m2`: 最小屋顶面积过滤 (m²), 默认: 50
            *   `max_2D_area_filter_m2`: 最大屋顶面积过滤 (m²), 默认: 600

        *   **方案参数**
            *   `plan_c_capacity_factor`: 方案C 容量系数, 默认: 0.9
            *   `plan_c_target_sc_rate`: 方案C 目标自用率 (%), 默认: 50
            *   `dc_ac_ratio`: 容配比 (DC/AC), 默认: 1.5
            *   `rooftop_use_factor`: 屋顶理论最大容量使用系数, 默认: 0.7
            *   `baseline_self_consumption_rate`: 基线自用率 (无电池) (%), 默认: 30

        *   **设备参数**
            *   `battery_dod`: 电池放电深度 DoD (%), 默认: 90
            *   `battery_rte`: 电池往返效率 RTE (%), 默认: 95
            *   `panel_power_kw`: 标准化面板单元功率 (kW), 默认: 0.44
            *   `panel_first_year_degradation_rate`: 面板首年衰减率 (%), 默认: 0
            *   `panel_annual_degradation_rate`: 面板次年起衰减率 (%), 默认: 0.40
            *   `pv_system_efficiency`: 系统效率 (%), 默认: 85

        *   **成本参数**
            *   `panel_unit_price_per_kw`: 每kW面板税前报价 (AUD/kW), 默认: 540
            *   `inverter_unit_price_per_kw`: 每kW逆变器税前报价 (AUD/kW), 默认: 280
            *   `battery_unit_price_per_kwh`: 每kWh电池税前报价 (AUD/kWh), 默认: 865

        *   **经济参数**
            *   `grid_buy_rate`: 购电价 (AUD/kWh), 默认: 0.3
            *   `grid_sell_rate`: 售电/馈网价 (AUD/kWh), 默认: 0.07
            *   `daily_fixed_charge`: 日均固定费用 (AUD/day), 默认: 0.35
            *   `electricity_inflation_rate`: 电费膨胀率 (%), 默认: 3.97
            *   `cash_interest_rate`: 现金利率 (%), 默认: 1.36
            *   `existing_sc_rate`: 已有系统基线自用率 (%), 默认: 30
            *   `battery_replacement_year`: 更换电池的年限 (年), 默认: 10

        *   **前端展示参数 (后置参数)**
            *   `display_range_percent_self_consumption`: 自用率展示浮动范围 (%), 默认: 5
            *   `display_range_percent_annual_savings`: 年度节省浮动展示范围 (%), 默认: 5
            *   `display_range_percent_payback_period`: 回本周期浮动展示范围 (%), 默认: 5
            *   `display_range_percent_final_price`: 最终报价浮动展示范围 (%), 默认: 5

        *   **兜底参数**
            *   `yield_per_kw_per_year_fallback`: 每kW年发电量 (兜底用) (kWh/kW/yr), 默认: 1526
            *   `hourly_yield_profile_fallback`: 小时发电量兜底数据 (支持上传或编辑JSON/CSV格式的数据)。

        *   **映射数据 (Mapping Data)**
            *   `gs_power_mapping`: GS 功率映射表 (支持表格形式编辑)
            *   `gd_power_mapping`: GD 功率映射表 (支持表格形式编辑)
            *   `battery_expansion_mapping`: 储能扩容功率映射表 (支持表格形式编辑)

登录界面
一个简洁的登录页面，
输入框：用户名 (Username) / 邮箱 (Email)
输入框：密码 (Password)
按钮：登录 (Login)
账号权限由核心原则: 简单实用，最小化开发工作量，由开发团队统一管理账号。
账号创建与分配:
无注册模块: 不提供前台注册功能。
后台手动创建: 所有账号由开发人员通过后台命令行或数据库直接操作的方式创建和管理。
