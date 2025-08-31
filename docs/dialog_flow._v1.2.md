# 对话流程 v1.2（合并展示卡、超大面积留资、去除截图上传）

本版本在 `docs/dialog_flow._v1.1.md` 基础上做三项关键改动：
- 合并 S5_3D_RENDER、S6_PROPOSAL_SELECT、S7_VALUE_PRESENT 为单一「方案互动卡」进行展示与交互。
- 面积过大（阈值见下）不再进入普通流程，直接进入专属留资卡。
- 全面取消用户上传屋顶截图的功能与文案。

---

## 0. 目标与原则
- 60 秒内给出可信方案，降低路径复杂度，提升转化率。
- 保持降级可用（3D 失败降级 2D），但不影响核心转化链路。

---

## 1. 状态机总览（v1.2）

```
START
  -> S1_WELCOME
  -> S2_ADDRESS_INPUT
    -> (ok) S3_MAP_CONFIRM
    -> (invalid) F1_ADDRESS_FALLBACK
  -> S4_AI_ANALYSIS
    -> (timeout) F4_ANALYSIS_TIMEOUT  → 继续保守参数
  -> S5_COMPOSITE_CARD   # 合并渲染/方案/价值展示
    -> (3D fail) F2_COMPOSITE_DEGRADE # 卡内降级为2D
    -> (choose lead) S8_LEAD_FORM
  -> S8_LEAD_FORM
  -> END

# 特殊分支（面积异常在 S3 阶段确认后即处理）
S3_MAP_CONFIRM
  -> (area < MIN_AREA) F3_IMAGE_FALLBACK_SMALL   # 仅重圈选/转留资，无截图上传
  -> (area > MAX_AREA) L1_LARGE_AREA_LEAD       # 直接进入专属留资卡
```

- 建议阈值：`MIN_AREA=20 m²`，`MAX_AREA=450 m²`（可配置）。

---

## 2. 意图与槽位（与 v1.1 保持一致，去除上传相关）

- I_ADDRESS_PROVIDE：`full_address`, `geo_point`, `addr_quality`
- I_MAP_CONFIRM：`roof_polygon`, `scale`, `roof_type`
- I_EXISTING_PV：`has_pv`, `pv_est_kw?`
- I_SWITCH_PLAN：`plan_id` in {smart_save, high_eff, independence, ultimate}
- I_OPEN_DETAILS：`section` in {energy, tariff, solar_hours, fit}
- I_SUBMIT_LEAD：`name`, `phone_or_email`, `best_time`, `address_autofill`
- I_RETRY / I_HELP / I_CONTACT_HUMAN / I_IDLE_RESUME

> 已移除：`I_UPLOAD_IMAGE` 及所有相关入口。

---

## 3. 逐状态定义（v1.2）

### S1_WELCOME（欢迎）
- 话术：「你好！我是你的 AI 太阳能顾问。输入地址，60 秒看清自家潜力。」
- UI：地址输入框 + 定位按钮
- 转移：I_ADDRESS_PROVIDE(ok) → S2

### S2_ADDRESS_INPUT（地址解析）
- 动作：地理编码与质量分；失败 → F1_ADDRESS_FALLBACK
- 通过 → S3_MAP_CONFIRM

### S3_MAP_CONFIRM（圈选确认 + 面积规则）
- 动作：圈选 `roof_polygon`，计算 `area_projected`，判定复杂度。
- 话术：「请点击或框选您的屋顶范围，尽量只包含可安装区域。」
- UI：多边形编辑、撤销、放大镜（放大或缩小地图）；复杂度提示。
- 分支：
  - 面积 < MIN_AREA → F3_IMAGE_FALLBACK_SMALL（不支持上传，仅重圈选/留资）
  - 面积 > MAX_AREA → L1_LARGE_AREA_LEAD（专属留资卡）
  - 其他正常 → S4_AI_ANALYSIS

### S4_AI_ANALYSIS（分析动画）
- 面积、日照、复杂度、设施、楼层（Solar API → StreetView → 默认值）。
- 成功 → S5_COMPOSITE_CARD；超时 → F4_ANALYSIS_TIMEOUT（保守参数继续）。

### S5_COMPOSITE_CARD（合并展示卡：渲染 + 方案 + 价值）
- 说明：原 S5+S6+S7 合并为单卡，减少跳转与上下文切换。
- 卡体结构：
  1) 模型区域：优先 3D，失败自动降级 2D（F2_COMPOSITE_DEGRADE）
  2) 方案选择：4 档方案卡（点击切换，模型与参数同步刷新）
  3) 价值呈现：预计年节省、发电量、自用率、上网收益等
  4) 操作区：查看详情、复制估算、获取补贴与完整报价（进入留资）
- 关键话术（卡内）：
  - 「可用面积约 X m²，理论最大 Y kW。选择方案查看节省与收益。」
  - 「预计年节省 ¥X,XXX（含上网收益）。条件与假设可展开查看。」
- 转移：
  - on I_SWITCH_PLAN / I_OPEN_DETAILS → 卡内刷新，不离开状态
  - on 获取补贴/完整报价 → S8_LEAD_FORM

### S8_LEAD_FORM（留资）
- 字段：`name`, `phone_or_email`, `best_time`, `address_autofill`
- 成功 → END；失败 → F5_FORM_FALLBACK

---

## 4. 兜底与专属留资

- F1_ADDRESS_FALLBACK（地址无效/低质）
  - 文案：
    - 「没找到该地址，能否换个写法或发送附近地标？」
    - 「也可跳过自动定位，拖动地图到您家附近位置。」
  - 行动：重试定位 / 手动拖动 / 人工评估（留资）

- F2_COMPOSITE_DEGRADE（合并卡内渲染降级）
  - 降级：3D → 2D 平面示意与参数列表；不影响方案与价值展示。
  - 文案：「模型生成异常，不影响方案计算，我们继续看配置与收益。」

- F3_IMAGE_FALLBACK_SMALL（面积过小或圈选异常）
  - 触发：面积 < MIN_AREA，或多边形无效。
  - 文案：「可安装面积可能偏小。请放大后重新圈选，或交由顾问免费复核。」
  - 行动：重新圈选 / 人工免费评估（留资）
  - 注意：不提供任何截图上传选项。

- L1_LARGE_AREA_LEAD（超大面积专属留资卡）
  - 触发：面积 > MAX_AREA。
  - 文案：
    - 「该屋顶面积较大，建议由高级顾问定制专属方案，可叠加商业用电策略。」
  - 卡体：
    - 优势要点（定制方案、并网策略、补贴核算）
    - 一键留资表单（最简字段 + 备注：可勾选“商业/工况”）
  - 提交 → END；若返回 → 回到 S3 允许重圈选。

- F4_ANALYSIS_TIMEOUT（分析超时）
  - 文案：「分析超时了，我会以保守参数继续计算，稍后自动刷新。」
  - 行动：进入 S5_COMPOSITE_CARD，以默认系数标注“估算”。

- F5_FORM_FALLBACK（表单提交失败）
  - 文案：「网络有点慢，请再试一次，或稍后由顾问联系你。」
  - 行动：重试 / 外部联系（WhatsApp/短信/拨打）

- F7_IDLE_RECOVERY（长时间无响应）
  - N 秒无交互（建议 30-45s）弹「稍后发送报告」留资卡。

---

## 5. 计算口径与分支（与 v1.1 保持一致）
- 复杂度系数 F_combined：flat 0.80 / simple 0.50 / complex 0.35
- N_max = (A_roof_proj × F_combined) / 1.9
- P_max = N_max × 0.45 kW
- 高能耗设施（泳池/球场）命中则上调画像与自用率假设
- 是否已有面板：有 → 优先给出储能升级收益区间

---

## 6. 事件埋点（v1.2 调整）
- 路径事件：
  - `address_input_success`, `map_confirm_success`
  - `segmentation_success`, `analysis_success|timeout`
  - `composite_card_view`（进入 S5 合并卡）
  - `plan_card_click`（plan_id）
  - `value_detail_open`（section）
  - `lead_form_view`, `lead_form_submit`, `lead_submit_success`, `lead_form_abandon`
- 兜底事件：
  - `fallback_address`, `fallback_composite_degrade`, `fallback_small_area`, `lead_large_area`, `fallback_analysis`, `fallback_form`, `fallback_idle`
- 关键参数：`roof_area`, `complexity`, `has_pv`, `pmax_kw`, `plan_id`, `est_saving_year`, `addr_quality`, `retry_count`

---

## 7. UI 与文案片段（合并卡示例）
- 顶部：
  - 「可用面积约 X m²，理论最大 Y kW」（标注来源/估算）
- 中部：
  - 模型视图（3D/2D 自动降级），视角与图层控制
- 方案区：
  - 4 卡方案（点击切换），同步更新模型铺设与参数
- 价值区：
  - 「预计年节省 ¥X,XXX（含上网收益）」+ 展开详情
- CTA：
  - 「获取补贴与完整报价」→ S8_LEAD_FORM

---

## 8. 时序与超时策略（保持口径）
- 地址解析：3s → F1
- 分析阶段：8s → F4（保守参数继续）
- 合并卡渲染：5s → F2（卡内降级 2D）
- 无交互：30-45s → F7（留资卡）

---

## 9. 合规与提示
- 明确“估算”与“最终以现场勘察为准”。
- 表单需有隐私政策与同意勾选。
- 对面积超大场景，文案需提示“可能涉及商业用电策略”。

---

## 10. 与 v1.1 的差异摘要
- 合并 S5/S6/S7 为 `S5_COMPOSITE_CARD`，在一卡内完成渲染、方案互动与价值呈现。
- 面积过大新增 `L1_LARGE_AREA_LEAD` 专属留资卡，直接转化，不再进入普通路径。
- 全面移除上传屋顶截图的能力与文案，相关意图与兜底删除或改写。
