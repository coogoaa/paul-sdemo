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
