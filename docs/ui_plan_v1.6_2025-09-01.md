# Solar Proposal UI/UX Plan — v1.6 (2025-09-01)

## Objectives
- Strengthen share and lead capture flows with clear, consistent UI.
- Add non-intrusive sharing dialog to System budget card (no Save image in dialog).
- Default scheme interaction: expand the user-selected scheme; if none, expand recommended; others collapsed.
- Refine info remains for improving assumptions, not the main lead capture entry.
- Introduce a lead-capture guidance card/modal containing Contact installer form (aligned with Refine info fields) and Learn STC.

## Key Decisions
- Share dialog (triggered from System budget Save image in Step 4/6):
  - Show preview image (share card.png), messaging to share with friends/family, H5 URL.
  - Actions: Share (Web Share API), Copy link. Do NOT show Save image in dialog.
  - Optional: QR to H5 page; disclaimer that numbers are estimates until installer assessment.
- Scheme interaction:
  - Default expand exactly one card: if user has chosen, expand that; otherwise expand recommended.
  - Keep other schemes collapsed with a light “compare more” affordance.
- STC and postcode:
  - Avoid repeated asks. Prefer collecting postcode in Refine info and store globally.
  - STC card reuses postcode; if missing, request postcode there (pre-filled if available; editable).
- Lead capture:
  - Provide Contact installer via form (fields align with Refine info and share validation). Place in a separate guidance card or follow-up modal, not in the initial scheme card.

## Copy Guidelines
- Share CTA copy on share cards: “Scan for your AI-powered solar proposal tailored just for you.”
- Dialog message: Encourage sharing; link to H5 tool; ask if the user wants more precise quotes or STC details; nudge to contact installer.
- Disclaimers: Estimates incl. tax; final price depends on installer site assessment, grid connection, and subsidy differences.

## Implementation Scope for v1.6
- Add a new Share Dialog component:
  - Image: sales_agent_v1.1/Pic/share card.png
  - Body text: share encouragement + H5 URL + prompts for precise quote / STC info
  - Buttons: Share, Copy link; links: Learn STC, Contact installer (opens lead form modal)
  - Exclude Save image from the dialog.
- System budget card (Step 4):
  - Bind Save image button to open the Share Dialog (instead of direct image export for v1.6 demo).
- Scheme interaction behavior:
  - Ensure only one scheme is expanded by default: selected or recommended. Others collapsed.
  - Keep a clear CTA: Get subsidy-inclusive quote.
- Lead-capture guidance card/modal:
  - Add a separate card/modal with Contact installer form and Learn STC link.
  - Form to align with Refine info fields and reuse validation.
- Data flow (lightweight):
  - Store postcode from Refine info; STC UI reads from it; if missing, STC UI asks once with prefill.

## Final Confirmations (2025-09-01)
- Placeholder H5 URL (with UTM):
  - https://example.com/h5?utm_source=share_card&utm_medium=web&utm_campaign=au_resi_pv_v1_6
- Lead-capture container: use modal (dialog) for Contact installer + Learn STC.
- Contact installer form: two-of-three required rule (Name / Phone / Email)
  - Pass rules:
    - Name + Phone, or Name + Email; if Name is empty, require Phone + Email.
  - Validation:
    - Name: 1–40 chars, no special symbols.
    - Phone: AU format, allow +61, length/prefix check (soft fallback allowed, flag for review).
    - Email: RFC-like format; optional disposable-domain blocklist (future).
    - Postcode: 4 digits (AU), prefilled if available; user-editable.
    - Consent checkbox required (privacy/contact authorization).
- Postcode preset behavior:
  - Prefer reading from map/address state; if address text exists, extract 4-digit postcode via regex.
  - If unavailable, leave blank and ask once in STC/lead modal; prefill and allow edits; write back to global state.
- Uploads (roof/bill photos, PDF bills): postponed to later iterations; keep in roadmap.

## Future Enhancements (not in this commit)
- Web Share API fallback improvements with QR generation.
- STC calculation by zone and system size; postcode-to-zone mapping.
- OCR/PDF import for power bills to auto-fill consumption and tariff details.
- Add installer certifications (CEC), warranties, installation timeline estimator.
- Finance/repayment options to reduce price sensitivity.

## Testing Checklist
- Share dialog opens from System budget Save image button.
- Dialog shows image, message, H5 link; Share/Copy function; no Save image button.
- One scheme expanded by default (selected or recommended), others collapsed.
- Contact installer form opens and shares validation with Refine info.
- If postcode exists in state, STC UI uses it; if not, requests once and stores.

## 问题与修复清单（2025-09-01）

1. 【Step 1 无法输入/点击】
   - 现象：地址输入无效，“Start exploring” 不可点击。
   - 根因：初始化期间 `addBotMsg()` 调用的 `refreshIcons()` 未定义，`boot()` 抛错导致包括 `bindStep1()` 在内的所有绑定中断。
   - 修复：新增全局 `refreshIcons()`；在文末用 `DOMContentLoaded` 保障 `boot()` 调用顺序。
   - 代码：`generated-page-v1.6_en.html` 中新增 `refreshIcons()`，并在文末新增 `document.addEventListener('DOMContentLoaded', boot)` 包装。

2. 【Share 与 Save image 行为】
   - 设计策略：
     - Share：打开分享弹窗，支持原生分享或回退复制。
     - Save image：按偏好改为“真正保存图片”。
   - 实现：引入 `html2canvas`，新增 `saveBudgetAsImage()` 将 `#s4BudgetPanel` 导出为 PNG；`#s4SaveImgBtn` 绑定为调用该函数。
   - 代码：`generated-page-v1.6_en.html` 新增 html2canvas CDN；在 `bindStep4()` 中将 `s4SaveImgBtn` 改绑为 `saveBudgetAsImage`。

3. 【分享链接与复制内容的区别】
   - Share（弹窗内 Share 按钮）：分享“报价摘要文本 + URL”。
   - Copy link（弹窗内）：仅复制 URL。
   - Copy（卡片按钮）：复制“报价摘要文本 + URL”。
   - URL 来源：统一为 `location.href`（当前 v1.6 页面地址），`openShareModal()` 每次打开都会覆盖 `#shareUrlText`，避免占位符外泄。

4. 【字体资源 404（非阻断）】
   - 现象：Inter 字体 woff2 404，不影响交互与功能。
   - 处理建议：后续补齐字体文件或移除引用。

## 链接策略说明（Share/Copy）

- 统一以 `location.href` 为准，不指向弹窗本身。
- 示例占位 H5 `https://example.com/h5?...` 仅为文案展示，实际在弹窗打开时会被覆盖为当前页面 URL。
- 如需引导到独立 H5 落地页（含 UTM 追踪），可将 `openShareModal()` 与 `buildShareText()` 的 URL 源改为该落地页地址。

## 额外测试项（更新）

- Step 1：输入 ≥6 字符后按钮可点，点击进入 Step 2。
- Save image：点击后下载 `#s4BudgetPanel` 的 PNG 文件（文件名含方案与时间戳）。
- Share 弹窗：每次打开时 `#shareUrlText` 更新为当前页面 URL；Share/Copy link 正常；Contact installer、Learn STC 正常。

## 后续路线图（与本次相关）

- 字体资源：补齐或移除 Inter 字体，消除 404。
- 导出能力：支持整卡/整屏/含二维码导出可选项。
- 链接落地：接入真实 H5 落地页并统一 UTM 归因。
