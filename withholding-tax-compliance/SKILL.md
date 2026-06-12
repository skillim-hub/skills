---
name: withholding-tax-compliance
description: "Conservative Israeli supplier withholding-tax compliance skill for certificate-based calculations and Form 856 staging workflows."
---

# Withholding Tax Compliance — Israel Form 856 Enhanced Skill

Use this skill when preparing Israeli supplier withholding-tax workflows for payments subject to ניכוי במקור and annual Form 856 reporting.

## Validated scope as of 2026-06-01

- **VAT**: The standard Israeli VAT rate is treated as **18%** for dates from **2025-01-01** onward.
- **Form 856**: Use for annual reporting of deductions and payments that are not salary/wage payments.
- **Withholding rate source**: Use the supplier-specific Israel Tax Authority certificate/service output or an accountant-approved explicit rate. Do not infer a rate only from supplier category.
- **Submission posture**: This skill stages and validates data. It does not auto-file Form 856.
- **API posture**: Tax Authority API materials exist for representative/SHAAM-connected reporting and payment flows, but this skill does not hard-code or call annual Form 856 API endpoints.
- **Official simulator**: Run the official logical-tests simulator for 126/856 before transmission.
- **Confirmation step**: After transmission, complete the separate 126/856 submission-confirmation workflow and retain the confirmation.

## Inputs required

For each supplier payment:

- payment ID
- supplier tax ID / VAT file number / entity identifier, normalized to 9 digits where applicable
- payment date
- amount before VAT
- VAT amount, if applicable
- supplier certificate rate percentage
- supplier certificate validity period and reference/source

## Calculation rule

By default, the package calculates withholding on `amount_before_vat_ils` and excludes VAT from the base. VAT can be included only by explicitly setting `include_vat_in_base=True` after accountant/legal workflow approval for the specific case.

## Safe workflow

1. Capture supplier certificate information from the Tax Authority service or authorized channel before payment.
2. Validate that the certificate is valid on the payment date.
3. Calculate withholding from the explicit certificate rate.
4. Reconcile totals to bookkeeping and periodic deduction reports.
5. Generate a staging CSV using `scripts/generate_856.py`.
6. Convert to the official current 856 file structure in your authorized accounting/payroll system.
7. Run the Tax Authority logical-tests simulator.
8. Upload through the official 126/856 service or representative/SHAAM channel.
9. Confirm the submission in the 126/856 confirmation system.
10. Store the online confirmation, certificate snapshots, staging file, official file, and simulator output.

## Official service URLs

- Annual 126/856 report upload: https://www.gov.il/he/service/report126
- Submission confirmation system: https://www.gov.il/he/service/serving-approval-system
- Logical-tests simulator: https://www.gov.il/he/service/logical-tests-for-reports-126-856
- Withholding-tax and bookkeeping confirmations: https://www.gov.il/he/service/itc-gmishurim
- Annual certificate Form 806: https://www.gov.il/he/service/itc806
- Deductions online payment/reporting service: https://www.gov.il/he/service/payment-of-taxes-deductions
- Tax Authority API information: https://govextra.gov.il/taxes/innovation/home/api/
- Software-house information: https://www.gov.il/he/departments/targetaudience/taxes-adience-software

## Do not do

- Do not present static supplier-category rates as authoritative.
- Do not call a non-official endpoint for 856 filing.
- Do not skip the official simulator.
- Do not treat a staged CSV as an official 856 fixed-width file.
- Do not rely on stale certificate data after its validity period.

## Files in this package

- `scripts/withholding_tax_compliance.py` — calculation and validation helpers
- `scripts/generate_856.py` — CLI staging-file generator
- `examples/` — example payment and certificate inputs
- `tests/` — pytest coverage for the public helpers
- `references/verification-log.md` — two-pass web validation log
- `references/sources.json` — structured source inventory

## Disclaimer / הבהרה

This skill is a preparation and automation aid only. It does not constitute tax, legal, financial, or other professional advice, and its output must be reviewed by a licensed professional (רו"ח / עו"ד / יועץ מס) before any filing, payment, or contractual use.

כלי זה מהווה שכבת הכנה ואוטומציה בלבד. אין בו ייעוץ מס, ייעוץ משפטי או ייעוץ מקצועי אחר, ויש לאמת כל פלט מול בעל מקצוע מורשה לפני הגשה, תשלום או שימוש חוזי.
