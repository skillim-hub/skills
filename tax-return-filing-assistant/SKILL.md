---
name: tax-return-filing-assistant
description: Guide Israeli small businesses, freelancers, employers, and consumers through income-tax filing workflows for Forms 1301, 135, 126, 856, and 6111. Use for form selection, field-by-field help, source-document checklists, deadline reminders, validation, and preparation for official Tax Authority submission. Not legal, accounting, or tax representation.
license: MIT
allowed-tools: Bash(python:*)
---

# Tax Return Filing Assistant

## Purpose

Guide a user through Israeli tax return preparation for:

- **Form 1301** — annual individual return for individuals, sole proprietors, freelancers, and other non-corporate taxpayers.
- **Form 135** — short annual return, commonly used by salaried individuals requesting a refund.
- **Form 126** — annual employer salary and withholding report.
- **Form 856** — annual report of payments to suppliers and non-employee service providers.
- **Form 6111** — standardized financial statement report submitted with the annual return when required.

Use a neutral, practical workflow: identify the required form, collect supporting documents, map values to fields, validate common risks, remind about deadlines, and prepare a submission checklist. Do not file the return for the user, promise a refund, or replace a licensed Israeli tax adviser.

## Operating rules

1. **Ask for the tax year first.** Israeli deadlines, thresholds, forms, and instructions can change by year.
2. **Separate preparation from submission.** Prepare data and checklists; direct the user to official Tax Authority systems or an authorized representative for final submission.
3. **Use exact currency and dates.** Write Israeli shekels as `₪12,345` and dates as `DD/MM/YYYY` when giving examples.
4. **Mark uncertainty clearly.** When a threshold, deadline, or portal rule depends on the filing year, state that official current instructions must be checked before filing.
5. **Protect personal data.** Do not request unnecessary identity numbers, bank details, medical records, or full payroll files. Ask for totals or redacted extracts whenever possible.
6. **Use imperative guidance.** Prefer: “Collect Form 106”, “Compare tax withheld”, “Validate supplier IDs”.

## First response template

When a user asks for help filing a return, collect only the minimum facts needed to choose the workflow:

```text
Provide:
1. Tax year, for example 2025.
2. Situation: salaried employee, freelancer/sole proprietor, employer, business paying suppliers, or business required to submit financial statements.
3. Goal: annual filing, refund request, employer report, supplier report, or Form 6111 preparation.
4. Available documents: Form 106, bookkeeping trial balance, receipts, supplier withholding certificates, payroll file, or accounting software export.
5. Whether submission will be self-filed or handled by a tax adviser.
```

If the user already provided these facts, proceed directly.

## Decision tree

```mermaid
flowchart TD
    A[Start: identify tax year and taxpayer role] --> B{Only salaried and seeking refund?}
    B -- Yes --> F135[Use Form 135 workflow]
    B -- No --> C{Individual or freelancer with annual income to report?}
    C -- Yes --> F1301[Use Form 1301 workflow]
    C -- No --> D{Employer with employees?}
    D -- Yes --> F126[Use Form 126 workflow]
    D -- No --> E{Paid suppliers or service providers as a business?}
    E -- Yes --> F856[Use Form 856 workflow]
    E -- No --> G{Business financial statements required?}
    G -- Yes --> F6111[Use Form 6111 workflow]
    G -- No --> H[No covered form identified; explain boundary and ask for context]
    F1301 --> I{Turnover or filing instructions require standardized financial statement?}
    I -- Yes --> F6111
    I -- No --> J[Prepare final checklist]
    F135 --> J
    F126 --> J
    F856 --> J
    F6111 --> J
```

## Form selection guide

| Situation | Primary form | Key trigger | Typical user | Do not use when |
|---|---:|---|---|---|
| Annual individual return | 1301 | Self-employment, business income, rental income, capital gains, foreign income, filing obligation, or full annual return | Freelancer, sole proprietor, investor, landlord | Salaried refund only with no full filing obligation |
| Salaried refund request | 135 | Employee wants a refund and is not otherwise required to file full annual return | Employee who changed jobs, missed credits, donated to recognized institution | Business income, foreign income, complex capital gains, or required full return |
| Employer annual payroll report | 126 | Employer paid wages and withheld tax/National Insurance | Small business with employees | Payments to suppliers only |
| Supplier payments report | 856 | Business paid non-employees and reported/withheld tax at source | Business paying freelancers, landlords, lecturers, service providers | Wages to employees |
| Standardized financial statement | 6111 | Business/financial reporting requirement applies by Tax Authority instructions, often based on turnover/entity/filing type | Sole proprietor or company with accounting records | Consumer refund without business activity |

## Deadline reminder model

Use the filing year following the tax year unless the official instructions state otherwise. Treat these as default planning dates, not final legal advice.

| Form | Planning deadline rule | Reminder schedule | Notes |
|---|---|---|---|
| 1301 | For tax year 2025, use 29/05/2026 for non-online filing and 30/06/2026 for online filing; for other years use year-specific official instructions | 60, 30, 14, and 7 days before; day-of warning | Do not use a generic representative extension unless an official extension schedule is verified |
| 135 | Refund claims are generally time-limited; calculate the last practical submission date as 31-12 six years after the tax year unless official guidance states otherwise | 90, 60, 30, and 7 days before limitation date | Use for salaried refund claims |
| 126 | Generic baseline is 30/04 after the tax year; for tax year 2025 use the extended date 31/05/2026 and verify online approval conditions | 60, 30, 14, and 7 days before | Confirm payroll broadcast deadline and approval-system status for the year |
| 856 | Generic baseline is 30/04 after the tax year; for tax year 2025 use the extended date 31/05/2026 and verify online approval conditions | 60, 30, 14, and 7 days before | Confirm online report format, withholding certificates, and approval-system status |
| 6111 | Submitted with the associated annual return | Same as 1301 or company return deadline | Confirm whether Form 6111 is required and which accounting codes apply |

### Reminder example

For tax year 2025, set the online Form 1301 planning deadline to **30/06/2026**. Generate reminders on **01/05/2026**, **31/05/2026**, **16/06/2026**, **23/06/2026**, and **30/06/2026**. For a taxpayer allowed to file non-online, set **29/05/2026** unless later official instructions apply. For Forms 126 and 856 in tax year 2025, set **31/05/2026** and verify whether later online approval grace-period rules apply.

## Field-by-field help

### Form 1301 — annual individual return

| Field group | Collect | How to use | Common edge cases |
|---|---|---|---|
| Personal details | ID, marital status, spouse details, children, address, bank account for refund | Match taxpayer identity and credits | Marriage/divorce during year, separated spouses, shared custody |
| Salary income | Form 106 from each employer | Sum taxable salary, benefits, tax withheld, pension contributions | Two employers, unemployment benefits, unpaid leave, reserve duty, stock benefits |
| Business income | Profit and loss report, receipt book/export, expense ledger | Report gross income, deductible expenses, net profit | Mixed personal/business expenses, home office allocation, vehicle expenses, cash basis vs accrual |
| Rental income | Rental contracts, deposits, annual rent totals, expenses | Choose exempt/10%/marginal track if available | Partial-year rental, multiple apartments, related-party rent, foreign rental |
| Capital gains | Bank Form 867, broker reports, securities sales reports | Attach/report gains, losses, foreign tax, withholding | Foreign broker without Israeli withholding, loss carryforward, cryptocurrency outside scope |
| Foreign income/assets | Foreign salary, dividends, bank/broker statements, foreign tax paid | Classify income and foreign tax credit support | Tax residency, treaty position, foreign account disclosure |
| Deductions and credits | Pension, life insurance, recognized donations, academic/resident/child credits | Reduce tax or calculate credits | Receipts not in taxpayer name, Section 46 approval missing, wrong child age |
| Prepayments and withholding | Income tax advances, withholding certificates, tax paid on rent/capital gains | Credit against final liability | Payment posted to wrong tax year, spouse allocation mismatch |

### Form 135 — short salaried refund return

| Field group | Collect | How to use | Common edge cases |
|---|---|---|---|
| Employee identity | ID, address, bank details | Identify refund claimant | Closed bank account, changed address |
| Employment income | Form 106 from each employer | Combine annual salary and tax withheld | Employer missing Form 106, two jobs overlapping |
| Refund reason | Donations, unemployment periods, maternity/parental leave, degree credits, child credits, pension/life insurance | Explain why withholding exceeded final tax | Credit already used by employer, duplicate claim with spouse |
| Supporting documents | Receipts, approvals, National Insurance confirmations, tax coordination records | Attach evidence | Missing original approval, unrecognized donation recipient |
| Limitation period | Tax year and filing date | Check whether refund claim is still timely | Old years near limitation deadline |

### Form 126 — annual employer salary report

| Field group | Collect | How to use | Common edge cases |
|---|---|---|---|
| Employer identification | Withholding file number, employer name, address | Match payroll file to employer | Multiple payroll files, branch split |
| Employee identity | ID, name, employment months | Build per-employee records | Foreign workers, corrected ID, employee with two roles |
| Salary and benefits | Gross salary, taxable benefits, exempt components | Reconcile to payroll ledger and Forms 106 | Company car value, meals, gifts, retroactive pay |
| Tax and social deductions | Income tax withheld, National Insurance, health tax, pension, study fund | Reconcile withholding and payments | Negative corrections, terminated employee, maternity leave |
| Form 106 reconciliation | Employee annual certificates | Ensure totals match annual report | Form 106 issued before final correction |

### Form 856 — payments to suppliers

| Field group | Collect | How to use | Common edge cases |
|---|---|---|---|
| Supplier identity | ID/company number, name, address | Create supplier recipient record | Supplier changed legal entity, foreign supplier |
| Payment classification | Service, rent, royalties, lecturer fee, subcontractor, other | Use correct payment type | Mixed invoice with goods and services |
| Gross payments | Annual amount before withholding | Reconcile to ledger and payment cards | Credit notes, refunds, VAT-inclusive vs VAT-exclusive reports |
| Withholding rate | Tax Authority certificate or default rate | Calculate/validate tax withheld | Expired certificate, exemption valid only part of year |
| Tax withheld | Actual amount deducted and remitted | Reconcile to withholding payments | Withheld but not remitted, rounding differences |
| Attachments | Supplier certificates, ledger cards, payment files | Support audit trail | Missing certificate for large payment |

### Form 6111 — standardized financial statement

| Field group | Collect | How to use | Common edge cases |
|---|---|---|---|
| Period and entity | Tax year, entity ID, accounting basis | Identify report scope | Short tax year, business opened/closed mid-year |
| Profit and loss | Revenue, purchases, salaries, rent, depreciation, finance costs | Map to Tax Authority item codes | Personal expenses, non-deductible fines, owner drawings |
| Balance sheet | Cash, receivables, inventory, fixed assets, payables, loans, equity | Map ending balances | Negative cash, unreconciled receivables, personal bank account |
| Tax adjustments | Non-deductible expenses, depreciation differences, loss carryforward | Bridge accounting profit to taxable income | Missing depreciation schedule, prior-year loss not approved |
| Reconciliation | Trial balance, ledgers, Form 1301/1214 totals | Ensure totals agree across forms | Turnover mismatch with VAT reports, payroll mismatch with 126 |

## Concrete examples

### Example 1 — salaried employee requesting a refund

Facts: Employee worked for two employers in 2025, no tax coordination, donated ₪1,200 to a recognized institution, and paid too much tax. Use Form 135 if no full filing obligation exists. Collect two Forms 106, donation receipt with Section 46 recognition, bank confirmation, and any unemployment/National Insurance confirmations. Compare total tax withheld to calculated annual tax after credits.

### Example 2 — freelancer with small business income

Facts: Osek patur earned ₪85,000 in consulting fees, had ₪12,000 deductible expenses, no employees, and no supplier withholding obligation. Use Form 1301. Add a profit and loss appendix. Check whether Form 6111 is required for the filing year; do not assume exemption solely from “osek patur” status.

### Example 3 — small employer

Facts: A studio paid three employees and issued monthly payslips. Use Form 126. Reconcile payroll ledger, monthly withholding payments, National Insurance reports, and Forms 106. Verify employee IDs and annual totals before transmission.

### Example 4 — business paying freelancers

Facts: A marketing agency paid ten freelance designers. Use Form 856 if reportable supplier payments and withholding rules apply. Collect supplier withholding certificates, gross payments, VAT treatment, and tax withheld. Flag expired certificates.

### Example 5 — Form 6111 mismatch

Facts: Bookkeeping revenue is ₪1,250,000, VAT returns show ₪1,270,000, and Form 6111 export shows ₪1,245,000. Stop before filing. Reconcile credit notes, timing differences, exempt revenue, and manual journal entries.

## Edge cases

- **Married couple with separate businesses:** Check whether spouse income must be reported in the same return and how income/credits are allocated.
- **New immigrant or returning resident:** Identify exemptions, reporting relief, and end dates; do not assume all foreign income is exempt.
- **Foreign broker:** Request annual statements, realized gain report, dividends, withholding, and currency conversion method.
- **Rental income:** Compare exemption, reduced-rate, and marginal tracks; consider the effect on deductions and surtax.
- **Multiple employers:** Tax coordination may be missing; Form 135 may be enough for refund-only cases.
- **Mid-year business opening:** Annualize nothing unless the form instructions require it; use actual tax-year income and expenses.
- **Cash withdrawals by owner:** Do not record owner drawings as business expenses.
- **Supplier withholding exemption expired mid-year:** Split payments by certificate validity period.
- **Corrected payroll after Form 106:** Update Form 126 and reissue corrected employee documents if required.
- **6111 code mapping uncertainty:** Use accountant-approved mapping from accounting software; do not guess tax codes.

## Validation checklist

Before presenting a final draft to the user, check:

1. Tax year is explicit.
2. Form selection matches facts.
3. Supporting documents are listed.
4. Deadlines are labeled as planning deadlines unless officially verified.
5. All money amounts use ₪ and totals reconcile.
6. Field help explains source documents and common errors.
7. Missing data is listed as an action item.
8. Sensitive data is minimized or redacted.
9. Submission channel is official or adviser-handled.
10. Legal/tax advice boundary is clear.

## Anti-patterns

- Do not promise “guaranteed refund”.
- Do not use outdated thresholds without the tax year.
- Do not ask for full unredacted ID scans unless essential.
- Do not mix VAT periodic reporting into income-tax workflows.
- Do not treat Form 135 as a substitute for Form 1301 when business, foreign, or complex capital-gain income exists.
- Do not report supplier invoices on Form 126 or employee wages on Form 856.
- Do not ignore Form 6111 because the business is small; verify the filing-year instruction.
- Do not submit based on trial balance totals that do not reconcile to VAT, payroll, and bank records.
- Do not screen-scrape Tax Authority portals; use official exports, certified software, or manual portal entry.

## Troubleshooting quick map

| Symptom | Likely cause | Action |
|---|---|---|
| Portal rejects ID number | Invalid checksum, wrong entity type, leading zero omitted | Re-enter exactly as registered; validate check digit |
| Refund lower than expected | Credit already used, income omitted, withholding lower than assumed | Recalculate from Form 106 and official credit rules |
| 126 total does not match payroll | Retroactive payslip, terminated employee correction, benefits not included | Reconcile month-by-month payroll register |
| 856 withholding mismatch | Expired certificate, VAT-inclusive amount used incorrectly, payment split | Reconcile supplier cards and certificates by date |
| 6111 imbalance | Trial balance not closed, opening balances wrong, account mapping error | Re-export after closing entries and code review |
| Missing Form 106 | Employer delay or closed employer | Request replacement and use payroll slips only as interim support |
| Late filing risk | Deadline misunderstood or adviser extension not confirmed | Confirm official deadline and file extension request where available |

## Production checklist for a deployed assistant

- Store no personal tax data unless the user explicitly saves a file.
- Redact ID numbers in logs and examples.
- Keep a versioned table of deadline assumptions.
- Keep a versioned table of form field definitions.
- Force tax-year selection before calculations.
- Run the pytest suite before publishing changes.
- Include Hebrew and English help text for each covered form.
- Provide source-document checklists per form.
- Include “verify official instructions” on every generated report.
- Do not include branding, visual marks, credit lines, or distribution callouts.
- Keep dependencies minimal and auditable.
- Handle offline operation; never require unofficial APIs.
