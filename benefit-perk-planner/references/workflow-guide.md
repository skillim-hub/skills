# Workflow Guide

Use these workflows to move from a benefit idea to a documented, budgeted, and auditable plan.

## Workflow 1: Launch meal benefits

Inputs: employee list, work model, budget, daily cap, monthly cap, provider shortlist, payroll provider, accounting contact, locations, and remote-work pattern.

Steps: define eligibility, set daily and monthly caps, compare Cibus/Tenbis/Sodexo-style providers and reimbursement, test coverage by city, confirm payroll and tax treatment, confirm VAT/invoice/export workflow, check fees/support/cancellation/data terms, upload employee file or use API provisioning, run a small pilot, reconcile the first invoice and payroll treatment, and publish a review date.

Output:

```markdown
Meal benefit policy
Effective date:
Daily cap:
Monthly cap:
Eligibility:
Remote-work rule:
Part-time rule:
Leave and termination rule:
Fallback route:
Payroll treatment:
Accounting documents:
Review date:
```

## Workflow 2: Add Keren Hishtalmut

Inputs: eligible employees, salary base, contribution split, budget cap, start date, payroll provider, pension/fund contact, accountant contact.

Steps: define objective, choose transparent eligibility criteria, verify current contribution ceilings and tax treatment, model employer cost by employee, check offer letters and agreements, prepare employee communication, collect fund details, configure payroll, submit contributions through the relevant interface, reconcile confirmation, store documentation, and review annually.

## Workflow 3: Freelancer benefit plan

Inputs: monthly revenue, fixed expenses, cash buffer, tax status, pension status, insurance status, tools, subscriptions, family obligations, and risk tolerance.

Steps: calculate 6–12 month average income, separate business expenses and owner drawings, confirm pension obligations, build 3–6 month emergency reserve, evaluate Keren Hishtalmut contribution, review professional liability/disability/cyber/health/business interruption risks, create equipment reserve, cancel unused subscriptions, keep receipts by category, and schedule quarterly review.

## Workflow 4: Compare salary increase and benefit

Inputs: gross salary increase, benefit value, expected utilization, tax/payroll treatment, restrictions, expiry, and portability.

Steps: estimate actual utilization, convert benefit to usable monthly value, compare to net salary after payroll withholding, penalize provider restrictions and expiry, consider portability if leaving employer, and choose the higher risk-adjusted value.

## Workflow 5: Migrate informal perks to policy

Steps: inventory recurring payments, identify recipients/costs/documents/promises, classify payroll/tax/VAT/privacy/classification risks, freeze new exceptions, draft policy with caps and eligibility, decide grandfathering, configure provider/payroll/accounting, communicate effective date, reconcile first two cycles, and archive the old process.

## Workflow 6: Quarterly review

Measure budget utilization, employee utilization, complaints, exceptions, payroll corrections, provider support issues, invoice reconciliation, equity indicators, and unused subscriptions. Keep high-use low-friction benefits, replace low-use high-admin benefits, update pro-rata rules, refresh provider comparison before renewal, and publish changes with reasonable notice.


## Web-validated implementation checks

Before launching any workflow in 2026, verify:

- VAT treatment using the current 18% standard rate.
- Israel Invoice allocation-number threshold: ₪10,000 from 01/01/2026 and ₪5,000 from 01/06/2026.
- Employee pension setup against the general 18.5% minimum and any sector-specific rules.
- Self-employed pension and National Insurance status against current National Insurance and Ministry of Finance guidance.
- Keren Hishtalmut ceilings against the current Tax Authority deductions booklet.
- API endpoint hosts, endpoint paths, webhook event names, and error codes from official developer-portal or vendor documentation only.
