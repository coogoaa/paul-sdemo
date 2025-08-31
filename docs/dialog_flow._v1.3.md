# 对话流程 v1.3（分享与保存优化、统一链接策略、初始化与表单校验加固）

本版本在 `docs/dialog_flow._v1.2.md` 基础上，聚焦于分享流程、保存图片能力与链接策略统一，同时修复初始化问题并加固表单验证体验，旨在提高分享转化与留资完成率。

---

## 0. 目标与原则
- 分享即转化：统一分享与复制口径，减少用户困惑，提升二次传播与回流。
- 保存即素材：提供真实的“保存预算卡图片”能力，便于用户转发与存档。
- 入口稳定：初始化鲁棒，关键按钮（Step 1、Step 4/6A）始终可用。
- 表单合规：三选二规则与同意勾选，postcode 预填与校验。

---

## 1. 与 v1.2 的差异摘要（v1.3 变更点）
- 统一分享与复制的 URL 源为 `location.href`（当前页面地址）。
  - 弹窗 `openShareModal()` 每次打开都会覆盖 `#shareUrlText`，避免占位 URL 外泄。
  - 卡片“Copy”复制“报价摘要文本 + URL”；弹窗“Copy link”仅复制 URL；弹窗“Share”通过 Web Share API 分享“摘要 + URL”。
- 恢复并升级“Save image”为真实导出功能：使用 `html2canvas` 将 Step 4 的预算卡 `#s4BudgetPanel` 导出为 PNG 文件（含时间戳与方案名）。
- 修复初始化：新增全局 `refreshIcons()`；以 `DOMContentLoaded` 触发 `boot()`，避免 Step 1 按钮与输入失效。
- 线索采集（Lead）与 STC：沿用三选二（姓名/电话/邮箱）策略，并对 postcode 进行 4 位校验；postcode 优先从地址或地图解析提取。

> 注：v1.2 中合并卡（S5_COMPOSITE_CARD）的状态机与主要链路不变，本次主要聚焦 Step 4/6A 的分享、保存与留资触达。

---

## 2. 状态机总览（承接 v1.2，不改变主干）
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
    -> (share/save) SHARE_DIALOG / SAVE_IMAGE
    -> (choose lead) S8_LEAD_FORM
  -> S8_LEAD_FORM
  -> END

# 特殊分支（面积异常在 S3 阶段确认后即处理）
S3_MAP_CONFIRM
  -> (area < MIN_AREA) F3_IMAGE_FALLBACK_SMALL
  -> (area > MAX_AREA) L1_LARGE_AREA_LEAD
```
- 阈值建议：`MIN_AREA=20 m²`，`MAX_AREA=450 m²`（可配置）。

---

## 3. 分享/复制/保存（v1.3 新策略）
- Share 弹窗（SHARE_DIALOG）：
  - 展示：分享卡预览 + 说明文案 + 当前页面 URL（每次打开均覆盖）。
  - 行为：
    - Share：调用 Web Share API 分享“报价摘要文本 + URL”；失败时回退到复制。
    - Copy link：仅复制当前页面 URL。
    - Learn STC：打开 STC 说明/引导。
    - Contact installer：进入留资表单（S8_LEAD_FORM）。
- Copy（卡片上的 Copy）：
  - 复制“报价摘要文本 + 当前页面 URL”。
- Save image（真实导出）：
  - 使用 `html2canvas` 将 `#s4BudgetPanel` 导出 PNG，文件名包含方案与时间戳。
  - 兼容性：若涉及跨域图片需 CORS；纯文本/本地元素可直接导出。

---

## 4. Step 1 初始化与可用性（修复点）
- 新增全局 `refreshIcons()`，避免初始化期间引用报错。
- 通过 `document.addEventListener('DOMContentLoaded', () => boot())` 确保绑定顺序正确。
- 地址输入 ≥6 字符启用按钮，点击后进入 S2/S3 正常链路。

---

## 5. 留资与校验（沿用并明确化）
- 表单字段：`name`, `phone`, `email`, `postcode`, `consent`。
- 通过条件（三选二）：
  - Name + Phone；或 Name + Email；
  - 若 Name 为空，则必须 Phone + Email。
- 校验：
  - Name：1–40 字符，排除特殊符号。
  - Phone：AU 号码；支持 +61；做长度与前缀软校验（可放行但标记复核）。
  - Email：标准邮箱格式。
  - Postcode：4 位数字；优先从地址文本或地图解析中提取并预填。
  - Consent：必勾选（隐私/授权）。

---

## 6. 时序与超时（承接 v1.2）
- 地址解析：3s → F1
- 分析阶段：8s → F4（保守参数继续）
- 合并卡渲染：5s → F2（卡内降级 2D）
- 无交互：30–45s → F7（留资卡）

---

## 7. 合规与提示（承接 v1.2）
- 所有金额均为估算；最终以安装商现场勘察为准。
- 留资表单需含隐私政策与同意勾选。
- 面积过大场景提示可涉及商业用电策略。

---

## 8. 事件埋点（v1.3 补充）
- 分享/复制/保存：
  - `s4_share_open`, `share_native_success|fallback_copy`, `share_copy_link`, `s4_save_image`
- 其它沿用 v1.2：
  - 路径：`address_input_success`, `map_confirm_success`, `analysis_success|timeout`, `composite_card_view`, `plan_card_click`, `value_detail_open`, `lead_form_view|submit|success|abandon`
  - 兜底：`fallback_address`, `fallback_composite_degrade`, `fallback_small_area`, `lead_large_area`, `fallback_analysis`, `fallback_form`, `fallback_idle`
- 关键参数：`scheme`, `roof_area`, `complexity`, `pmax_kw`, `est_saving_year`, `addr_quality`, `retry_count`

---

## 9. UI 与文案片段（更新点）
- Share 弹窗文案：鼓励分享给家人朋友；展示当前页面链接；提示可获取更精确报价或了解 STC；引导“Contact installer”。
- Save image：按钮文案保持“Save image”，点击即下载 PNG（Toast：Image saved / Save failed）。
- 卡片 Copy：Toast：Quote copied / Copy failed。

---

## 10. 迁移与兼容
- 若需将分享 URL 指向独立 H5 落地页：
  - 在 `openShareModal()` 与 `buildShareText()` 中统一替换 URL 源；保留 UTM 追踪参数。
- 字体资源缺失（Inter 404）不影响流程；建议补齐或移除。

---

## 11. 测试检查清单（v1.3）
- Step 1 输入与按钮在刷新后可用；输入 ≥6 字符启用按钮；点击进入 S2/S3。
- Step 4/6A：
  - Share 弹窗每次开启均显示当前页面 URL；Share/Copy link 可用；Contact installer/ Learn STC 正常。
  - Save image 点击后导出 `#s4BudgetPanel` PNG，命名含方案与时间戳。
- Lead 表单：三选二与 postcode/consent 校验生效；提交成功后埋点正确。
- 无交互 30–45s 触发留资提示。
