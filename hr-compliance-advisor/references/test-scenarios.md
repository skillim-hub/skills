# Test Scenarios

| # | Scenario | Key facts | Expected primary risk |
|---:|---|---|---|
| 1 | Hourly retail minimum wage | ₪31/hour, adult cashier, unpaid closing time | Critical minimum wage and unpaid time |
| 2 | Monthly salary with excessive hours | ₪8,000/month, 55 hours/week | High overtime and effective wage review |
| 3 | Blanket global overtime | Contract says salary includes all overtime | High invalid clause risk |
| 4 | No attendance records | Variable shifts but no clock records | High wage-proof risk |
| 5 | Pension missing after 10 months | Employee, no pension arrangement | High pension gap |
| 6 | Prior pension ignored | Active fund before start, employer starts after 6 months only | High retroactive pension gap |
| 7 | Section 14 partial deposits | Clause exists, severance deposits below full rate | High severance exposure |
| 8 | Immediate termination | Fired by message without hearing | Critical termination-process risk |
| 9 | Short notice | Monthly employee, 30 months tenure, 7 days notice | High advance-notice gap |
| 10 | Pregnant employee shift reduction | Shifts reduced after disclosure | Critical protected-status risk |
| 11 | Fertility treatment dismissal | Termination near disclosure | Critical protected-status risk |
| 12 | Return from parental leave | Role replaced, pay reduced | Critical parental-rights risk |
| 13 | Contractor integrated into team | Invoice, fixed hours, company email, manager approval | High misclassification risk |
| 14 | Genuine supplier | Project fee, multiple clients, own tools, substitution allowed | Low or medium contractor risk |
| 15 | Cleaning-sector worker | General contract omits sector benefits | Medium/high expansion-order risk |
| 16 | Guarding-sector overtime | Long shifts, rest-day work | High sector and hours risk |
| 17 | Youth worker | Teen employee with adult schedule | High youth-rule verification |
| 18 | Foreign worker caregiving | Live-in care, deductions, passport held | Critical wage/deduction/immigration sensitivity |
| 19 | Tips in restaurant | Tips treated as full salary without records | High wage-record risk |
| 20 | Commission-only sales | No guaranteed minimum in slow month | Critical minimum wage risk |
| 21 | Uniform deduction | Deducted ₪400 for uniform and breakage | High wage-protection risk |
| 22 | Sick leave policy | Policy omits statutory structure | Medium/high sick-pay wording risk |
| 23 | Vacation forfeiture | All unused vacation deleted on 31-12-2025 | Medium/high vacation policy risk |
| 24 | Travel reimbursement missing | Hourly employee uses buses, no travel line | Medium/high travel expansion-order risk |
| 25 | Reserve duty retaliation | Fewer shifts after reserve duty | Critical protected-status/retaliation risk |
| 26 | Public contractor service | Service contractor at public site omits wage components | High sector and contract compliance risk |
| 27 | Remote Israeli employee | Worker in Israel for foreign parent, no Israeli payroll | High cross-border employment risk |
| 28 | Probation no rights | No pension, vacation, sick leave or notice during probation | High mandatory-rights risk |
| 29 | Manager exemption by title | Team lead has fixed schedule and no autonomy | High overtime exemption risk |
| 30 | Final payslip withholding | Final wage held pending equipment return | Critical wage-protection risk |

## Scenario JSON pattern

```json
{
  "name": "Hourly retail minimum wage",
  "facts": {
    "worker_type": "employee",
    "sector": "retail",
    "hourly_rate_ils": 31,
    "weekly_hours": 38,
    "tenure_months": 10,
    "has_pension_arrangement": false,
    "contract_text": "Closing time is unpaid."
  },
  "expected_codes": ["MIN_WAGE_HOURLY", "PENSION_MISSING", "UNPAID_CLOSING_TIME"]
}
```
