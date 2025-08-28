# Solar Sales Demo 页面逻辑说明（generated-page-v1.3_en.html）

本文面向非技术同学，系统性讲清当前演示页面（`sales_agent_v1.1/generated-page-v1.3_en.html`）的界面结构、交互流程、数据来源与常见问题排查。阅读后，你可以独立理解页面各步骤如何联动，尤其是 Step 4（预算面板）的工作方式。

---

## 1. 页面结构总览

页面按“步骤”分块，每个步骤用一个带 `data-step="N"` 的容器来表示：
- Step 1：采集基础信息
- Step 2：屋顶图片/区域确认
- Step 3：AI 分析（等待/过渡）
- Step 4：3D 模型 + 方案推荐 + 预算面板（本次重点）
- Step 5/6/6A：进一步的方案展示、对比与引导
- Step 7：留资弹窗（Refine info 按钮会打开）

页面有统一的工具函数与状态：
- `state`：存放运行时状态，例如当前选中的方案 `state.scheme`、模型旋转角度等。
- `showStep(n)`：切换显示第 n 步。
- `showToast(message, type, duration)`：底部中间吐司提醒（英文）。
- `addUserMsg()/addBotMsg()`：在聊天区域添加用户/助手消息（用于演示流程感）。

---

## 2. Step 4 模块概览（重点）

Step 4 由三部分组成：
1) 3D 模型展示区（只做视效，真实 3D 由 `<model-viewer>` 提供）
2) 方案横向卡片条（4 个方案按钮）
3) 预算面板（Budget quote range）

关键 DOM ID/类名：
- 3D 容器：外层设定高度为 `20vh`，位于标题 “Your 3D roof model” 下。
- 方案条容器：`#schemesStrip4`
- 方案按钮：`.scheme-card-mini`，每个按钮有 `data-scheme`（`smart`/`efficient`/`independence`/`ultimate`）
- 预算面板容器：`#s4BudgetPanel`
- 预算面板字段：`#s4BudgetRange`、`#s4SizeRange`、`#s4PaybackRange`、`#s4SelfUseRange`、`#s4AnnualSaveRange`
- 面板底部按钮：`#s4CopyBtn`、`#s4ShareBtn`、`#s4RefineBtn`（或在逻辑里用通用选择器获取）

---

## 3. 方案与预算是如何计算出来的？

页面内置了“方案配置”和“区间计算”两类函数：
- `getSchemeConfig(key)`：根据方案 key 返回该方案的基本参数，比如：
  - `name`（方案名称）
  - `panels`（面板数量）
  - `battery`（是否含电池）
  - `sizeKW`（系统容量，单位 kW）
  - `selfUse`（自用率的基准值/区间）
  - `saving`（年省电费基准值）
  - `roi`（回本周期）
  - `subsidy`（可能的政府补贴，用于 Step 7 文案）

- `computeRangesFromConf(conf)`：根据传入的 `conf`（即方案配置），计算更具体的“区间值”，包括：
  - 预算区间 `r.budget.low/high`
  - 回本周期区间 `r.roi.low/high`
  - 自用率区间 `r.selfUse.low/high`
  - 年省电费区间 `r.saving.low/high`

这些区间值将被用于展示在 Step 4 的预算面板中。

---

## 4. 刷新预算面板的核心函数

- `applyValuePresentation(conf)`：用于在多个步骤中更新显示（包括 Step 6/6A 等）。现在它会调用 `updateS4BudgetPanel(conf)`，确保 Step 4 面板同步。
- `updateS4BudgetPanel(conf)`（本次新增/强化）：
  1. 调用 `computeRangesFromConf(conf)` 拿到区间 `r`；
  2. 将 `r` 的结果填入以下元素：
     - `#s4BudgetRange`：预算区间（货币格式）；
     - `#s4SizeRange`：系统容量（kW）+ 面板数 + 是否含电池；
     - `#s4PaybackRange`：回本年限区间；
     - `#s4SelfUseRange`：自用率百分比区间；
     - `#s4AnnualSaveRange`：年省电费区间（货币格式）。
  3. 给 `#s4BudgetPanel` 添加一个短暂高亮（`ring-emerald-300`），提示用户“数据已更新”。
  4. 绑定/兜底 Copy、Share、Refine 三个按钮的点击事件（见第 6 节）。
  5. 打印调试日志：`console.debug('[Step4] updateS4BudgetPanel', { scheme: state.scheme, conf })`，便于排查。

---

## 5. 用户如何切换方案？（事件流）

为了保证“点击卡片必然生效”，页面提供了三层保障：

- A. 按钮自身监听：每个 `.scheme-card-mini` 都有内联 `onclick="window.selectScheme4('key')"`，直接调用全局方法（最强兜底）。
- B. 容器事件委托：对 `#schemesStrip4` 添加了 `click` 事件委托，点击卡片内部任意元素都会触发。
- C. 初始化监听：在 `bindStep4()` 中，原生地为每个按钮也添加了 `addEventListener('click', ...)`（作为正常路径）。

全局方法 `window.selectScheme4(key)` 会：
1. 读取 `getSchemeConfig(key)` 得到 `conf`；
2. 设置 `state.scheme = key`；
3. 调用 `applyValuePresentation(conf)` 和 `updateS4BudgetPanel(conf)`；
4. 弹出 `showToast('Switched: xxx', 'info')`（轻提示）。

这样不管是点击卡片、还是在控制台直接调用 `window.selectScheme4('ultimate')`，预算面板都会立刻更新。

---

## 6. 预算面板底部三个按钮（Copy / Share / Refine）

- Copy：
  - 优先用 `navigator.clipboard.writeText(buildShareText(conf))` 复制分享文案到剪贴板；
  - 成功/失败均有英文吐司：`Quote copied` / `Copy failed`。

- Share：
  - 若支持 `navigator.share`，会调起系统原生分享（文案同上）；
  - 否则自动降级为复制到剪贴板，提示 `Copied share content`；
  - 用户取消分享时提示 `Share canceled`。

- Refine info：
  - 打开留资弹窗 `openLeadModal(conf.subsidy)`，并在聊天区追加说明性文案（强调补贴额度仅供参考）。

所有吐司均为英文且高对比度，展示时长约 1.4 秒。

---

## 7. 3D 模型区域说明

- 采用 `<model-viewer>` 组件，仅用于展示效果；
- 高度已调为 `20vh`，以腾出空间给预算面板；
- 支持拖拽旋转（顶部有 “Drag to rotate” 标签），禁用缩放；
- 该区域与预算计算无直接耦合，仅作可视化承载。

---

## 8. 常见问题与排查

- 问：点击方案卡片，预算不变？
  - 先看控制台是否有日志：`[Step4] scheme selected:` 与 `[Step4] updateS4BudgetPanel`；
  - 若无日志，可能是点击事件被滚动/遮挡吞掉；页面已加“内联 onclick”和“事件委托”双兜底，通常强制刷新（禁用缓存）即可；
  - 也可以直接在控制台执行 `window.selectScheme4('ultimate')` 验证逻辑链路是否正常。

- 问：复制/分享没有反应？
  - 桌面浏览器和 HTTPS 环境下，`navigator.clipboard`/`navigator.share` 行为会有所限制；
  - 页面已处理失败/降级场景，并通过吐司反馈。

- 问：金额单位或格式不对？
  - 当前使用通用货币格式（如 `$12,345`）；
  - 如需改为 AUD 本地化（`A$` 或 `AUD`），可以在 `formatCurrency()` 里统一调整。

---

## 9. 开发者参考（函数索引）

- `getSchemeConfig(key)`：返回方案配置。
- `computeRangesFromConf(conf)`：根据配置计算预算/回本/自用率/年省区间。
- `applyValuePresentation(conf)`：跨步骤刷新展示，会调用 Step 4 刷新函数。
- `updateS4BudgetPanel(conf)`：仅负责刷新 Step 4 预算面板的 DOM 与按钮绑定。
- `showToast(message, type, duration)`：底部吐司。
- `openLeadModal(subsidy)`：打开留资弹窗。
- `buildShareText(conf)`：生成复制/分享用文案。

文件路径：`sales_agent_v1.1/generated-page-v1.3_en.html`

---

## 10. 快速操作指南（给业务/演示同学）

1. 打开页面，完成 Step 1–3 的基础输入；
2. 进入 Step 4：
   - 左侧是 3D 模型（可拖拽旋转），下方有 4 个方案卡片；
   - 点击不同方案卡片，预算面板会立即更新为该方案的：预算区间、系统容量/面板数/是否含电池、回本年限、自用率、年省电费；
   - 若点击无变化，刷新页面（禁用缓存），或在控制台执行 `window.selectScheme4('smart')` 等命令；
3. 在预算面板底部，可点击：
   - Copy（复制报价文案）
   - Share（调用系统分享或复制降级）
   - Refine info（打开留资弹窗）

到这里，你已经能完整演示 Step 4 的核心价值：基于多方案的预算区间对比与一键分享/留资。
