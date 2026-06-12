# Changelog

## 0.3.0 — 2026-06-01

### Web validation — Pass 1 findings

- Confirmed 2026 self-employed National Insurance reduced/regular rates: 4.47% and 12.83%.
- Confirmed 2026 health-insurance reduced/regular rates: 3.23% and 5.17%.
- Confirmed combined rates: 7.70% and 18.00%.
- Confirmed reduced-rate monthly threshold: ₪7,703.
- Confirmed maximum monthly income subject to contributions: ₪51,910.
- Confirmed minimum monthly self-employed income basis: ₪3,442.
- Confirmed average wage used by the calculation: ₪13,769.
- Confirmed Section 345 basis deduction: 52% of National Insurance contributions, excluding health insurance.
- Confirmed official NII example: ₪12,000/month -> ₪34,690 quarterly basis -> ₪3,864 quarterly total.
- Confirmed Form 6101 as the official multi-year report for BTL collection file opening/change notices.
- Confirmed standard VAT rate increased to 18% from 2025-01-01.
- Found 2026 Israel Invoices allocation threshold of ₪10,000 before VAT from 2026-01-01.
- Found official Tax Authority API catalog and sandbox `Invoices/v1/Approval` path.

### Skeptical re-validation — Pass 2 findings

- Double-confirmed rates and thresholds against English NII pages and the 2026 NII circular.
- Double-confirmed average wage against Hebrew and English average-wage pages.
- Double-confirmed the calculation formula against Hebrew and English NII calculation pages.
- Double-confirmed official terminology in Hebrew and English.
- Corrected Israel Invoices 2026 threshold: from 2026-06-01 the threshold is ₪5,000 before VAT, not ₪10,000.
- Corrected API guidance: do not hard-code production invoice endpoints from older v1 beta material; use current Tax Authority swagger/developer portal.
- Confirmed no official webhook event names are referenced by the NII/Tax Authority sources used by this estimator.

### Package changes

- Bumped metadata to 0.3.0.
- Rebuilt `SKILL.md` and `SKILL_HE.md` around 2026 official rates.
- Added `references/verification-log.md` in two-pass format.
- Added machine-readable `references/rates-2026.json` and `references/sources.json`.
- Added estimator implementation, CLI, examples, and tests.
- Added VAT helper using 18% for standard VAT from 2025-01-01.
