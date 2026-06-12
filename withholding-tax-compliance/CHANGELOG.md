# Changelog

## 0.3.0 — 2026-06-01

### Phase 1 web-validation findings

- Confirmed the standard Israeli VAT rate as 18% from 2025-01-01 via official/Knesset/Gov.il sources.
- Confirmed Form 856 belongs to the annual 126/856 reporting service for deductions/payments other than salary/wages.
- Confirmed 126/856 reporting is online through the Tax Authority internet service or representative portal.
- Confirmed the separate 126/856 submission-confirmation workflow and its key inputs: deductions file number, tax year, form type, barcode.
- Confirmed the official logical-tests simulator for 126/856 pre-submission checking.
- Confirmed the Tax Authority withholding-tax/bookkeeping confirmation service provides rates to deduct at source.
- Confirmed the confirmation service is free of charge.
- Confirmed 2026 certificate-validity material through 2027-03-31 from the 2026 instruction.
- Confirmed the official 856 file-structure document exists for tax years 2017-2025.
- Confirmed Tax Authority API materials exist for deductions reporting/payment by SHAAM-connected representatives.

### Phase 2 skeptical re-validation findings

- Double-confirmed VAT rate in 2026 through PwC Israel Corporate Other Taxes, reviewed 2026-01-01.
- Double-confirmed VAT effective date through Herzog's VAT update.
- Double-confirmed Form 856 workflow through Oracle/SAP-style ERP documentation and accounting-firm summaries.
- Double-confirmed submission-confirmation terminology through the English Gov.il confirmation page.
- Double-confirmed official simulator terminology through Hebrew and English Gov.il pages.
- Double-confirmed the supplier-specific certificate/rate model through the Tax Authority certificate service and 2026 instruction mirrors.
- Corrected the original “rates by supplier category” phrasing: the package now requires supplier certificate rate snapshots or explicit professional override.
- Corrected API claims: the package now does not implement auto-filing or hard-code annual Form 856 endpoint paths.
- Confirmed no official Form 856/withholding webhook event names were found; no webhook events are exposed by the package.
- Confirmed Hebrew official terminology: ניכוי מס במקור, אישור ניהול ספרים, דוחות 126 ו-856.
- Confirmed English official terminology: withholding tax at source, bookkeeping confirmations, Submission Confirmation System.

### Package corrections

- Rewrote `SKILL.md` and `SKILL_HE.md` to require supplier-specific certificates.
- Added conservative API and auto-filing limitations to metadata and docs.
- Added `references/verification-log.md` with two-pass source columns and status tags.
- Added `references/sources.json` with official/secondary source inventory.
- Added calculation and validation helpers in `scripts/withholding_tax_compliance.py`.
- Added CLI staging generator in `scripts/generate_856.py`.
- Added examples for payments and certificate snapshots.
- Added pytest coverage for VAT, certificate validity, calculation, staging, and summaries.
