# Test Scenarios

Use these scenarios to verify drafting behavior and reviewer judgment.

| Number | Scenario | Expected result |
| --- | --- | --- |
| 1 | Standard 12-month apartment, ₪5,200 rent, ₪10,400 security | Drafted without error |
| 2 | Apartment with missing tenant name | Error `MISSING_PARTY_NAME` |
| 3 | Apartment with missing property address | Error `MISSING_PROPERTY_ADDRESS` |
| 4 | Apartment with zero rent | Error `MISSING_RENT` |
| 5 | Apartment with end date before start date | Error `INVALID_DATE_RANGE` |
| 6 | Covered apartment with excessive security | Warning `RESIDENTIAL_DEPOSIT_CAP` |
| 7 | Apartment marked as VAT-applicable | Warning `VAT_ON_APARTMENT` |
| 8 | Three-month apartment lease | Coverage marked limited; no automatic cap assumption |
| 9 | Apartment above ₪20,000 monthly rent | Coverage marked uncertain for legal review |
| 10 | Furnished apartment | Inventory appendix required |
| 11 | Apartment with pets | Pet conditions must not override mandatory rights |
| 12 | Apartment with home office carve-out | Municipal, tax, insurance, and building rules flagged |
| 13 | Roommate replacement | Consent, guarantor, and deposit allocation needed |
| 14 | Protected tenancy hint | Stop and escalate |
| 15 | Standard office with VAT | Draft includes VAT and tax invoice language |
| 16 | Office without permitted use | Warning `OFFICE_WITHOUT_USE` |
| 17 | Office with fit-out works | Attach plans, approvals, insurance, restoration rules |
| 18 | Office with signage | Add signage approval and municipal rule check |
| 19 | Office with public reception | Check accessibility and business licensing |
| 20 | Renewal option | Require notice deadline and written exercise |
| 21 | Early exit by landlord only | Flag one-sided termination |
| 22 | Template missing repair clause | Warning `NO_REPAIR_CLAUSE` |
| 23 | Template missing handover protocol | Warning `NO_HANDOVER_PROTOCOL` |
| 24 | Template missing balanced early termination | Warning `NO_EARLY_TERMINATION_BALANCE` |
| 25 | Invalid date format | Raise validation error |
| 26 | English draft requested | Output English headings and clauses |
| 27 | Async batch draft | All drafts return stable ids |
| 28 | Export Markdown | File begins with a title heading |
| 29 | CLI draft then audit | Extract id from draft response and use it in audit response |
| 30 | Hebrew JSON output | Hebrew remains readable with `ensure_ascii=False` |
