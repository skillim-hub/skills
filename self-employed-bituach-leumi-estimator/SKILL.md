---
name: self-employed-bituach-leumi-estimator
description: "Web-validated 2026 estimator for Israeli self-employed National Insurance and health-insurance contributions, with VAT and Israel Invoices reference data."
---

# Self-Employed Bituach Leumi Estimator — Enhanced v3

Use this skill to estimate Israeli **National Insurance contributions** and **health-insurance contributions** for a person whose only occupation is self-employment in Israel.

This skill is web-validated for **2026** against official National Insurance Institute (ביטוח לאומי) and Israel Tax Authority / gov.il sources. It is an estimator, not legal, tax, or accounting advice. When the user needs a binding amount, direct them to the official National Insurance calculator or a licensed Israeli tax professional.

## Primary scope

Estimate contributions for a self-employed Israeli resident who:

1. is at least 18 and has not reached retirement age;
2. works solely as self-employed for the estimate period;
3. is not using the mixed salaried+self-employed coordination rules;
4. is not a pensioner, under-18 worker, non-worker, student, or abroad-status case.

The Hebrew official term is **עובד עצמאי** and the English official term is **Self-Employed Person**.

## 2026 validated parameters

| Parameter | 2026 value |
|---|---:|
| Average wage used in BTL calculations | ₪13,769/month |
| Reduced-rate monthly threshold | ₪7,703/month |
| Maximum monthly income liable for contributions | ₪51,910/month |
| Minimum monthly income for self-employed contributions | ₪3,442/month |
| National Insurance reduced rate | 4.47% |
| National Insurance regular rate | 12.83% |
| Health insurance reduced rate | 3.23% |
| Health insurance regular rate | 5.17% |
| Combined reduced total | 7.70% |
| Combined regular total | 18.00% |
| Deductible National Insurance share for Section 345 basis | 52% |
| Standard VAT rate for Israeli transactions from 2025-01-01 | 18% |

## Calculation method

For a self-employed person working solely in that capacity, the contribution basis is calculated after deducting **52% of National Insurance contributions** from the income basis, excluding health-insurance contributions. The package implements this as an implicit equation:

```text
gross_income = contribution_basis + 0.52 * national_insurance_due(contribution_basis)
```

The basis is then bounded by the 2026 minimum and maximum monthly income amounts. Contributions are calculated by applying the reduced rates up to ₪7,703/month and the regular rates above that threshold, up to ₪51,910/month.

The official NII example for ₪12,000/month in January 2026 gives a quarterly contribution basis of ₪34,690 and total quarterly contributions of ₪3,864. The included tests assert that result.

## VAT handling

VAT is not part of the National Insurance calculation. The helper exists only for quotes/invoice examples. Use **18%** for standard VAT on or after 2025-01-01 unless the user is asking about zero-rated, exempt, special import/customs, or edge-case VAT rules.

## Israel Invoices reference only

The estimator does not call Tax Authority APIs. The references include current Israel Invoices thresholds and endpoints because invoicing systems sometimes sit next to estimator workflows:

- From 2026-01-01: allocation number required for input-VAT deduction on invoices above ₪10,000 before VAT.
- From 2026-06-01: threshold lowered to ₪5,000 before VAT.
- Sandbox approval endpoint found in official docs: `https://openapi.taxes.gov.il/shaam/tsandbox/Invoices/v1/Approval`.
- Production API details must be taken from the current Tax Authority swagger/developer portal, not hard-coded from stale copies.

No official webhook event names were found in the NII or Tax Authority sources used by this estimator; do not invent webhook names.

## How to answer users

When asked for an estimate:

1. Ask for monthly or annual net self-employed income/profit if missing.
2. Clarify whether the person is solely self-employed or also salaried if the user mentions other employment.
3. Use the 2026 parameters above for 2026 estimates.
4. Show National Insurance, health insurance, and total separately.
5. State that final legally binding amounts follow the law and NII records.

## Files

- `scripts/bituach_leumi_estimator.py` — estimator and VAT helpers.
- `scripts/cli.py` — command-line interface.
- `references/verification-log.md` — two-pass web validation log.
- `references/rates-2026.json` — machine-readable validated constants.
- `tests/` — pytest coverage for official example and edge cases.

## Disclaimer / הבהרה

This skill is a preparation and automation aid only. It does not constitute tax, legal, financial, or other professional advice, and its output must be reviewed by a licensed professional (רו"ח / עו"ד / יועץ מס) before any filing, payment, or contractual use.

כלי זה מהווה שכבת הכנה ואוטומציה בלבד. אין בו ייעוץ מס, ייעוץ משפטי או ייעוץ מקצועי אחר, ויש לאמת כל פלט מול בעל מקצוע מורשה לפני הגשה, תשלום או שימוש חוזי.
