# Troubleshooting Guide

Use this guide when a benefit plan fails, overruns, or cannot pass payroll, accounting, legal, privacy, or employee review.

## Fast triage

| Question | Action |
|---|---|
| Is the item mandatory or discretionary? | Fix mandatory items first |
| Is cost capped? | Add daily, monthly, annual, or event caps |
| Is eligibility written? | Draft policy before launch |
| Can payroll code it? | Create or map component |
| Can accounting document it? | Require invoice, receipt, and approval trail |
| Does it involve health or personal data? | Minimize data and publish notice |
| Are contractors included? | Review classification |
| Is provider coverage adequate? | Test locations and create fallback |

## Issue: meal cost exceeds budget

Symptoms: invoice exceeds forecast, employees use full balance early, or finance requests post-fact corrections. Causes: missing monthly cap, missing leave/termination rules, provider fees excluded from model, or informal remote-day use. Fix by adding daily and monthly caps, tying eligibility to workdays, adding provider fees, exporting utilization by employee, and communicating changes before the next cycle.

## Issue: employees outside central areas get little value

Symptoms: low usage in remote or peripheral locations, fairness complaints, or manual cash exceptions. Fix by adding supermarket eligibility where possible, receipt-based fallback, flexible food/wellness wallet, and provider reassessment before renewal.

## Issue: payroll rejects wellness reimbursements

Symptoms: payroll asks whether the benefit is taxable, receipts arrive without approval, or reimbursement appears as miscellaneous salary. Fix by defining eligible categories, using an approval form, confirming treatment with accountant and payroll, configuring a payroll component, and prohibiting collection of medical details.

## Issue: Keren Hishtalmut creates fairness complaints

Symptoms: some employees receive it without criteria, recruiters promise it inconsistently, or new hires negotiate exceptions. Fix by defining eligibility by tenure, role family, level, or broad rollout; publishing criteria; adding expansion review date; and aligning offer letters with payroll capability.

## Issue: freelancer overspends on perks

Symptoms: high subscription cost, weak tax reserve, or no emergency buffer. Fix by freezing discretionary spending, building a 3–6 month reserve, confirming pension and National Insurance status, keeping only revenue-critical tools, and reviewing after two profitable quarters.

## Issue: contractor receives employee-like benefits

Symptoms: contractor receives meal card, wellness wallet, approval flow, and manager-style supervision. Fix by pausing expansion of employee-style perks, keeping contractor commercial terms separate, avoiding HR benefit systems unless legal review approves, and documenting independent contractor indicators.

## Issue: privacy concern in wellness program

Symptoms: program asks for diagnosis, provider receives sensitive data, or employees object to tracking. Fix by requesting receipt and category only, avoiding diagnosis/treatment/biometric data, reviewing data-processing terms, publishing notice, and setting retention period.

## Issue: accounting cannot reconcile invoice

Symptoms: invoice total differs from HR expectation, terminated employee appears, or VAT treatment is unclear. Fix by reconciling HR master list, requiring utilization CSV, matching invoice/report/payroll file, removing inactive employees, and asking accountant to classify VAT and expense treatment.

## Escalation matrix

| Severity | Example | Owner | Timing |
|---|---|---|---|
| Critical | missed mandatory pension | payroll plus accountant/legal | immediate |
| High | uncertain tax treatment | accountant plus payroll | before next payroll |
| High | contractor classification risk | legal | before continuation |
| Medium | weak provider coverage | operations | within 30 days |
| Medium | budget overrun | finance | next cycle |
| Low | employee confusion | operations or HR | within one week |

## Recovery template

```markdown
Benefit:
Issue:
Affected people:
Root cause:
Immediate fix:
Payroll/accounting action:
Legal/privacy action:
Communication:
Policy version:
Next review date:
```


## Web-validated troubleshooting additions

| Symptom | Web-validated risk | Fix |
|---|---|---|
| VAT amount does not match invoice | Standard VAT rate is 18% from 01/01/2025, but invoice date and transaction type matter | Recalculate using current Tax Authority guidance |
| Input VAT cannot be deducted | Israel Invoice allocation number may be missing above the 2026 threshold | Check ₪10,000 threshold from 01/01/2026 and ₪5,000 from 01/06/2026 |
| Pension file rejected | Contribution split or salary basis may not match the applicable arrangement | Recheck 6% employee, 6.5% employer, 6% severance baseline and sector exceptions |
| Freelancer pension estimate is wrong | Average wage or income bracket changed | Recalculate 4.45% and 12.55% brackets with current average wage |
| Vendor integration fails | Endpoint or webhook name was assumed from an example | Replace with signed vendor or official developer-portal documentation |
