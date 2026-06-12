# Migration Checklist

## 1. Inventory existing assets

Collect old skill files, contract templates, policy documents, payroll assumptions, rate tables, sector checklists, termination templates, Hebrew wording, test scenarios, and scripts.

## 2. Remove prohibited content

Remove legacy identity markers, image references, creator metadata, and distribution callouts. Use neutral imperative voice. Keep only the required neutral notice in the license file.

## 3. Rename and normalize

Use slug `hr-compliance-advisor`. Store references under `references/`, executable helpers under `scripts/`, and runnable examples under `scripts/examples/`.

## 4. Expand scope

| Legacy area | New coverage |
|---|---|
| Contract red flags | HR policy, payroll, onboarding, termination, parental rights |
| Section 14 traps | Pension, severance, release of funds, final-pay workflow |
| Non-compete review | Contractor status, confidentiality, unfair restrictions |
| Notice clauses | Statutory notice calculations and termination workflow |
| Salary wording | Minimum wage, overtime, wage protection, payslip evidence |

## 5. Localize Hebrew

Use ₪ for amounts and DD/MM/YYYY for dates. Use שכר מינימום, שעות נוספות, פנסיה חובה, פיצויי פיטורים, הודעה מוקדמת, דמי הבראה, החזר נסיעות, תלוש שכר. Avoid unnecessary transliteration and masculine-only wording where a neutral alternative works.

## 6. Refresh rate configuration

Before production, refresh minimum monthly wage, hourly wage, travel cap, convalescence rate, pension components, severance component, and sector rates. Document source, effective date, and retrieval date.

## 7. Validate with tests

Run:

```bash
python -m pytest scripts/test_hr_compliance_advisor_client.py
```

Acceptance target: at least 20 tests and coverage for minimum wage, overtime, pension, notice, contractor status, protected status, and CLI smoke tests.

## 8. Pilot

Run five historical cases, compare output to payroll/legal conclusions, adjust configuration, add missing scenarios, and train users to treat output as triage.

## 9. Production controls

Require current-rate verification, professional review for critical/high action, sensitive-data redaction, versioned outputs, source preservation, assumptions, and re-testing after legal or payroll changes.
