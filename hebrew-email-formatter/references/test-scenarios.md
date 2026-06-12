# Test Scenarios

Use these scenarios to validate drafting quality, localization, and edge-case handling.

| # | Scenario | Required behavior |
|---:|---|---|
| 1 | First payment reminder to known female client | Use `שלום [שם]`, amount in `₪`, date `DD/MM/YYYY` |
| 2 | First payment reminder to company with unknown contact | Use neutral grammar; avoid slash forms |
| 3 | Firm overdue reminder after prior reminder | Mention prior reminder date and request update by concrete date |
| 4 | Payment reminder missing due date | Draft with warning and avoid invented due date |
| 5 | Quote for new procurement department | Use formal tone, scope bullets, VAT status, validity date |
| 6 | Quote without VAT status | Add review note for missing VAT status |
| 7 | Invoice sent with one attachment confirmed | Write `מצורפת חשבונית` |
| 8 | Invoice sent without attachment confirmation | Do not claim attachment is attached |
| 9 | Meeting request with three time slots | List options and ask for confirmation or alternative |
| 10 | Meeting request with unknown gender | Use neutral wording |
| 11 | Consumer complaint for damaged product | Use formal tone and structured facts |
| 12 | Consumer complaint with refund demand | Use `אבקש לבדוק את זכאותי להחזר` unless approved text is supplied |
| 13 | Small business response to angry customer | Thank customer and state written response date |
| 14 | Apology for delayed deliverable by male sender | Use `מתנצל` only when sender gender is male |
| 15 | Apology for delayed deliverable by female sender | Use `מתנצלת` only when sender gender is female |
| 16 | Cancellation notice for subscription | Ask for written confirmation and balance or refund details |
| 17 | Status update for ongoing project | Use completed, planned, and attention sections |
| 18 | Warm follow-up to existing client | Use `היי`, concise tone, no over-formality |
| 19 | Formal email to authority | Use formal greeting and precise facts |
| 20 | Message includes sensitive personal data | Add privacy warning and minimize data |
| 21 | User asks to add promotion to invoice email | Warn about separating promotional content |
| 22 | Recipient is a team | Use plural greeting and verbs |
| 23 | Hebrew-English product names | Keep product names unchanged |
| 24 | Bank transfer details placeholder | Avoid fabricating bank details |
| 25 | User supplies ISO date | Convert to `DD/MM/YYYY` |
| 26 | User supplies amount with decimals | Format as `1,234.50 ₪` when requested |
| 27 | Service provider asks for testimonial | Use polite optional wording |
| 28 | Landlord maintenance request | Formal-neutral tone and requested repair date |
| 29 | Supplier delivery delay notice | Apologize, explain briefly, give new date |
| 30 | Final warning before escalation | Keep factual and recommend review for legal wording |

## Automated test expectations

The test suite covers currency formatting, date parsing, greeting selection, signature assembly, drafting flows, warnings, asynchronous parity, draft storage, JSON serialization, and syntax checks.
