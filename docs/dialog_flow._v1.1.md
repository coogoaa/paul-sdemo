# 对话流程 v1.1（细化状态机与兜底策略）

本版本在 `docs/dialog_flow.md` 基础上细化：
- 状态机（State/Intent/Slot/Transition）
- 每步话术与 UI/组件
- 全量兜底矩阵与恢复流程
- 事件埋点与数据结构

适配场景：H5 智能太阳能顾问（Chat + 交互卡片 + 3D 模型）。

---

## 0. 术语与目标
- 目标（Primary）：获取高质量留资，便于后续上门勘察与成单。
- 次目标（Secondary）：60 秒内输出可信初步方案与收益区间，建立信任。
- 术语：
  - Intent：用户意图识别（如提供地址、确认屋顶、切换方案等）。
  - Slot：意图所需的关键槽位（如详细地址、屋顶多边形、已有面板=是/否）。
  - State：对话状态节点，决定当前 UI 与话术。

---

## 1. 状态机总览

```
START
  -> S1_WELCOME
  -> S2_ADDRESS_INPUT
    -> (ok) S3_MAP_CONFIRM
    -> (invalid) F1_ADDRESS_FALLBACK
  -> S4_AI_ANALYSIS
  -> S5_3D_RENDER
    -> (fail) F2_RENDER_FALLBACK
  -> S6_PROPOSAL_SELECT
  -> S7_VALUE_PRESENT
  -> S8_LEAD_FORM
  -> END
```

横向分支在各状态穿插：
- B_A 层数判断策略（Solar API/StreetView/默认值）
- B_B 屋顶复杂度 → 可用面积系数 F_combined
- B_C 是否已有面板 → 新装/储能升级路径
- B_D 高能耗设施（泳池/球场） → 用户画像与推荐容量调整
- B_E 容量与报价区间计算

---

## 2. 意图与槽位（Intents & Slots）

- I_ADDRESS_PROVIDE
  - Slots：`full_address`(string), `geo_point`(lat,lng), `addr_quality`(0-1)
- I_MAP_CONFIRM
  - Slots：`roof_polygon`(pixel[]), `scale`(m/pixel), `roof_type`(flat/simple/complex)
- I_EXISTING_PV
  - Slots：`has_pv`(bool), `pv_est_kw`(optional)
- I_SWITCH_PLAN
  - Slots：`plan_id` in {smart_save, high_eff, independence, ultimate}
- I_OPEN_DETAILS
  - Slots：`section` in {energy, tariff, solar_hours, fit}
- I_SUBMIT_LEAD
  - Slots：`name`, `phone_or_email`, `best_time`, `address_autofill`
- I_RETRY / I_HELP / I_UPLOAD_IMAGE / I_CONTACT_HUMAN
- I_IDLE_RESUME（超时后恢复）

---

## 3. 逐状态详细定义

### S1_WELCOME（欢迎）
- 目标：建立价值承诺，促使填写地址。
- 话术：
  - 「你好！我是你的 AI 太阳能顾问。输入地址，60 秒看清自家太阳能潜力。」
- UI：地址输入框 + 定位按钮（可选）。
- 转移：
  - on I_ADDRESS_PROVIDE(ok) → S2_ADDRESS_INPUT
  - on idle(30s) → 提醒卡 + 一键留资快捷卡（见兜底）

### S2_ADDRESS_INPUT（地址解析）
- 动作：地理编码，质量分（`addr_quality`）。
- 成功条件：lat/lng 返回、质量分≥阈值。
- 话术：
  - 「已定位到您提供的位置，下一步请在地图上圈选屋顶区域。」
- UI：卫星图 + 点击/框选工具，按钮「已选好」。
- 转移：
  - ok → S3_MAP_CONFIRM
  - invalid/低质 → F1_ADDRESS_FALLBACK

### S3_MAP_CONFIRM（屋顶圈选与确认）
- 动作：SAM 分割/辅助，输出 `roof_polygon` + `scale`。
- 旁路：若识别已有面板，触发 I_EXISTING_PV。
- 话术：
  - 「请点击或框选您的屋顶范围，尽量只包含可安装区域。」
- UI：多边形编辑、撤销、放大镜（放大或缩小地图）；提示复杂度选择。
- 转移：
  - ok → S4_AI_ANALYSIS
  - 面积异常/图像不清 → F3_IMAGE_FALLBACK

### S4_AI_ANALYSIS（AI 分析动画）
- 动作：面积、日照、复杂度、设施识别；楼层判定策略（B_A）。
- 话术：
  - 「正在分析屋顶面积 / 日照情况 / 高能耗设施…即将生成专属方案。」
- UI：进度动画（3-5s），可跳过按钮。
- 转移：
  - 完成 → S5_3D_RENDER
  - 分析失败（服务超时）→ F4_ANALYSIS_TIMEOUT

### S5_3D_RENDER（3D 初次呈现）
- 动作：构建 3D 屋顶与墙体，默认屋顶坡度 23°，楼层按 B_A。
- 话术：
  - 「已为你生成 3D 模型。可用面积约 X m²，理论最大容量约 Y kW。」
- UI：模型视角控制、标尺图层。
- 转移：
  - ok → S6_PROPOSAL_SELECT
  - 渲染失败 → F2_RENDER_FALLBACK

### S6_PROPOSAL_SELECT（方案互动）
- 动作：计算容量档位和价格区间（B_E），考虑复杂度与设施（B_B/B_D）。
- 话术：
  - 「为你准备了 4 个方案。点击卡片，3D 模型与电池墙会同步变化。」
- UI：四卡方案、切换动画、详细假设侧栏。
- 转移：
  - on I_SWITCH_PLAN → 保持本状态（刷新模型/数值）
  - on I_OPEN_DETAILS → 展开对应详单
  - 用户选择继续 → S7_VALUE_PRESENT

### S7_VALUE_PRESENT（价值呈现）
- 话术：
  - 「在当前方案下，预计年节省约 ¥X,XXX，含上网收益。下方可查看详细计算与假设。」
- UI：动态数字、曲线/条形图（发电量、自用率、账单下降）。
- 转移：
  - 用户点击「获取补贴与完整报价」→ S8_LEAD_FORM
  - 犹豫/展开更多细节 → 留在本状态

### S8_LEAD_FORM（留资）
- 字段：`name`, `phone_or_email`, `best_time`, `address_autofill`（只读）。
- 话术：
  - 「预计你还能申请约 ¥X,XXX 的补贴。留下联系方式，完整报告立即发送。」
- 校验：手机号/邮箱格式、本地化提示。
- 成功：END（toast：已发送/稍后顾问联系）。
- 失败：F5_FORM_FALLBACK（重试/人工）

---

## 4. 关键分支细化（与 v1.0 对齐并量化）

- 楼层判断 B_A：
  1) Solar API 高度→楼层（优先）
  2) Street View 正面图 → LLM 判定 1/2 层（次优）
  3) 片区默认楼层（回退）+ 标注“估算”，在 S7 文案说明区显示来源。

- 屋顶复杂度 B_B → 可用面积系数 F_combined：
  - flat: 0.80；simple: 0.50；complex: 0.35（在侧栏显示“复杂度系数”）

- 是否已有面板 B_C：
  - 无 → 新装四方案
  - 有 → 切到储能升级建议（不给具体报价，仅收益区间 + 下一步勘探）

- 高能耗设施 B_D：
  - 命中（泳池/球场）→ 用户画像上调，推荐容量与自用率假设提高
  - 未命中 → 默认画像

- 容量/报价 B_E：
  - N_max = (A_roof_proj × F_combined) / 1.9
  - P_max = N_max × 0.45 kW
  - 依据 P_max 给 3-4 档容量与报价区间（±10% 浮动）

---

## 5. 兜底矩阵（Fallbacks）

- F1_ADDRESS_FALLBACK（地址无效/低质）
  - 触发：地理编码失败/`addr_quality` < 阈值/地点偏差过大。
  - 话术：
    - A: 「没找到该地址，能否换个写法或发送附近地标？」
    - B: 「也可跳过自动定位，拖动地图到您家附近位置。」
  - 行动：按钮「重试定位 / 手动拖动 / 联系人工评估（留资）」
  - 恢复：成功后回 S2 或 S3；连续3次失败→弹出留资卡。

- F2_RENDER_FALLBACK（3D 渲染失败）
  - 降级：切 2D 平面示意 + 参数列表；保留方案互动与收益计算。
  - 话术：
    - 「模型生成异常，不影响方案计算。我们继续看配置与收益吧。」
  - 恢复：后台重试成功→无感刷新 3D；若仍失败→保持 2D 并引导留资。

- F3_IMAGE_FALLBACK（卫星图像不清/圈选异常）
  - 触发：屋顶多边形无效、面积 <20m² 或 >450m²、影像模糊。
  - 话术：
    - 「需要更清晰的屋顶图。可放大后重圈选，或上传自家屋顶截图。」
  - 行动：按钮「重新圈选 / 上传截图 / 人工免费评估（留资）」

- F4_ANALYSIS_TIMEOUT（分析超时）
  - 话术：
    - 「分析超时了，我会以保守参数继续计算，同时后台继续尝试。」
  - 行动：进入 S5 但以默认系数；弹出提示「结果为估算值」。

- F5_FORM_FALLBACK（表单提交失败）
  - 话术：
    - 「网络有点慢，请再试一次，或选择稍后由顾问联系你。」
  - 行动：按钮「重试 / WhatsApp/短信联系 / 拨打电话」

- F6_EXISTING_PV_UNSURE（已装面板识别不确定）
  - 话术：
    - 「可按两种方式快速估算：当作新装试算 或 仅做储能升级评估。」
  - 默认路径：先看储能升级收益，再引导留资。

- F7_IDLE_RECOVERY（长时间无响应）
  - 触发：N 秒（建议 30-45s）无交互。
  - 话术：
    - 「需要我把当前结果整理成报告稍后发你吗？」
  - 行动：一键留资卡；继续体验按钮「稍后再看」。

---

## 6. 每步可直接落地的话术与 UI 片段

- 步 1 欢迎（S1）
  - 话术：「你好！输入地址，60 秒看清自家太阳能潜力。」
  - UI：地址输入 + 定位按钮

- 步 2 地图确认（S3）
  - 话术：「我已定位到该区域，请点击/框选你的屋顶（可放大）。」
  - UI：圈选工具 +『已选好』

- 步 3 分析动画（S4）
  - 话术：「正在分析屋顶面积/日照/高能耗设施…」

- 步 4 3D 呈现（S5）
  - 话术：「这是你的 3D 模型。可用面积约 X m²，理论最大 Y kW。」

- 步 5 方案互动（S6）
  - 话术：「4 个配置档可切换，模型与电池墙会同步变化。」

- 步 6 价值呈现（S7）
  - 话术：「预计年节省 ¥X,XXX（含上网收益）。可展开详细计算假设。」

- 步 7 留资（S8）
  - 话术：「你或可申请约 ¥X,XXX 的补贴。留下联系方式获取完整报价。」

- 兜底示例（F3）
  - 话术：「需要更清晰的屋顶图。可放大重圈选，或上传截图/转人工评估。」

---

## 7. 计算假设（与 v1.0 一致）
- 面板面积：1.9 m²/片；单片功率：0.45 kW
- 可用面积系数：0.80 / 0.50 / 0.35（随屋顶复杂度）
- 年均等效小时：4.18；电价：0.30 AUD/kWh；上网电价：0.07 AUD/kWh
- 自用率：无电池 30%，有电池 85%

---

## 8. 事件埋点（Analytics）
- 核心转化：`lead_submit_success`
- 路径指标：
  - `address_input_success`, `map_confirm_success`
  - `segmentation_success`, `render_3d_success`
  - `plan_card_click`（含 plan_id）
  - `value_panel_open`（section）
  - `lead_form_view`, `lead_form_submit`, `lead_form_abandon`
- 兜底触发：`fallback_address`, `fallback_image`, `fallback_render`, `fallback_analysis`, `fallback_form`, `fallback_pv_unsure`, `fallback_idle`
- 关键参数：
  - `roof_area`, `complexity`, `has_pv`, `pool_detected`
  - `pmax_kw`, `plan_id`, `est_saving_year`
  - `addr_quality`, `retry_count`

---

## 9. 数据结构（前后端对接）

- 圈选结果（前端 → 后端）
```json
{
  "roof_polygon": [[x1,y1],[x2,y2],...],
  "scale": 0.12,
  "lat": -33.86,
  "lng": 151.21,
  "addr_text": "...",
  "addr_quality": 0.92
}
```

- 分析结果（后端 → 前端）
```json
{
  "area_projected_m2": 85.4,
  "complexity": "simple",
  "storeys": 2,
  "has_pv_detected": false,
  "high_load": {"pool": true, "tennis": false},
  "pmax_kw": 10.8,
  "plans": [
    {"id": "smart_save", "kw": 6.6, "price_range": [X1,Y1]},
    {"id": "high_eff", "kw": 8.2, "price_range": [X2,Y2]},
    {"id": "independence", "kw": 10.0, "price_range": [X3,Y3]},
    {"id": "ultimate", "kw": 12.0, "price_range": [X4,Y4]}
  ]
}
```

---

## 10. 时序与超时策略
- 地址解析：3s 超时 → F1 提示 + 继续手动拖动
- 分析阶段：8s 超时 → F4，进入保守参数
- 3D 渲染：5s 超时 → F2 降级 2D
- 用户无交互：30-45s → F7 弹留资卡

---

## 11. 安全与合规（简要）
- 明确“估算”与“最终以现场勘察为准”。
- 不承诺固定收益；表述为区间与假设条件已展示。
- 表单合规同意（勾选项）：允许联系与隐私政策链接。

---

## 12. 与 v1.0 的差异摘要
- 补齐状态机定义与显式转移条件。
- 充实兜底矩阵（触发条件/文案/恢复路径）。
- 增加时序与超时策略、数据结构与埋点字段，便于前后端联调与 A/B。

---

备注：本 v1.1 与 `docs/dialog_flow.md` 的计算与分支口径保持一致，可直接对照实现。
