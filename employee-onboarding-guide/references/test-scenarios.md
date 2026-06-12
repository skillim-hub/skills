# Test Scenarios

Use these scenarios to verify onboarding output quality.

| # | Scenario | Expected result |
|---|---|---|
| 1 | Standard salaried employee | Form 101, bank details, written terms, pension status, payroll handoff |
| 2 | First employee | Employer readiness, payroll provider check, secure storage, timekeeping |
| 3 | Hourly cafe worker | Hourly rate in ₪, shifts, breaks, overtime approval, timesheet |
| 4 | Employee with another employer | Tax coordination and National Insurance coordination prompt |
| 5 | Active pension | Fund details and first deposit deadline |
| 6 | No active pension | Neutral choice process and default arrangement review |
| 7 | Freelancer converts to employee | Separate invoices from payroll and update access |
| 8 | Remote developer | Equipment, security, availability, incident reporting |
| 9 | Youth employee | Age, permitted hours, safety, supervision |
| 10 | Foreign worker | Permit, visa, authorization, health insurance, language access |
| 11 | Student employee | Ask for documentation only when relevant |
| 12 | Employee starts tomorrow | Prioritize payroll-blocking documents |
| 13 | Missing bank details | Salary-payment warning |
| 14 | Net salary promise | Payroll review and gross salary wording |
| 15 | Commission employee | Commission formula and payment timing |
| 16 | Employee with vehicle | Vehicle handover, fines, insurance, taxable benefit review |
| 17 | Clinic receptionist | Patient privacy and confidentiality |
| 18 | NGO part-time coordinator | Part-time terms and data privacy |
| 19 | Household employee | Special employer reporting path |
| 20 | Refusal to complete Form 101 | Do not fill for employee; escalate to payroll |
| 21 | Family status changed | Updated Form 101 and payroll notice |
| 22 | Non-Hebrew speaker | Provide understood employee-facing instructions |
| 23 | Supplier mistakenly asked for Form 101 | Remove Form 101 and review classification |
| 24 | Equipment issued without form | Record serial numbers and return terms |
| 25 | Payroll close passed | Escalate, correct next run, add prevention reminder |
| 26 | Insecure document channel | Move to restricted storage and remove unnecessary copies |
| 27 | Remote work abroad | Pause for cross-border tax and labor review |
| 28 | Shift cancellation policy missing | Add scheduling and approval rules |
| 29 | Pension fund unknown | Request statement or provider contact |
| 30 | Employment terms mismatch | Create single source of truth and update payroll |

## Automated checks

The test suite verifies date validation, employee and supplier workflow separation, Form 101 actions, coordination warnings, pension warnings, Hebrew localization, CLI create and checklist chaining, JSON output, installable imports, example behavior, and syntax compilation.


## Web-validated additions for v2.2.0

| # | Scenario | Expected result |
|---|---|---|
| 31 | Form 101 timing | Employee request mentions 7-day submission and annual renewal. |
| 32 | Adult written terms | Checklist mentions 30-day delivery timing. |
| 33 | Youth written terms | Checklist mentions 7-day delivery timing. |
| 34 | 2026 National Insurance reference | Reference notes show ₪7,703 and ₪51,910 with a verification warning. |
| 35 | Foreign worker health insurance | Workflow verifies private medical insurance before work starts. |
| 36 | Privacy and remote work | Remote workflow includes privacy minimization and security controls. |
