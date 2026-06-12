# Test Scenarios

Use these scenarios to validate the skill, client, CLI, examples, and assistant behavior. Each scenario should run without live network by substituting fixture payloads where needed.

| # | Scenario | Input | Expected behavior |
|---:|---|---|---|
| 1 | CPI latest fetch | Price payload with one `month` series | Parse series name, code, latest point, monthly and annual change. |
| 2 | CPI rent increase | Amount `₪5,200`, base `103.1`, target `106.4` | Return `₪5,366.34`, `3.20%`, and formula. |
| 3 | CPI rent decrease | Amount `₪5,200`, base `106.4`, target `103.1` | Return lower amount unless floor option is enabled. |
| 4 | Floor-zero contract | Same as scenario 3 with floor enabled | Return original amount and `0%` effective decrease. |
| 5 | Invalid base index | Base `0` | Raise validation error; do not calculate. |
| 6 | Percent entered as index | Base `100`, target `3.2` | Flag suspicious value when compared with expected index levels. |
| 7 | Catalog search Hebrew | Query `דירות` | Return matching chapter from mocked catalog. |
| 8 | Catalog search English | Query `apartment` | Return matching chapter from mocked catalog. |
| 9 | No catalog match | Query `bananas` | Return empty list and suggest broader search. |
| 10 | API 404 | Mock `404` response | Raise structured API error with status code. |
| 11 | API non-JSON | Mock HTML body | Raise structured API error; recommend `format=json`. |
| 12 | data.gov search | Query `population` with `lamas` filter | Call `package_search` with `fq=organization:lamas`. |
| 13 | Async index fetch | Mock async response | Return same normalized series as sync client. |
| 14 | CSV export | Series with two points | Write header and two data rows. |
| 15 | Business brief trend up | Three rising points | Mark trend as rising and explain cost pressure. |
| 16 | Business brief trend down | Three falling points | Mark trend as falling and avoid forecast language. |
| 17 | Stable trend | Tiny changes | Mark trend as stable. |
| 18 | Missing `currBase` | Point lacks value | Skip invalid point or keep raw with `None`; warn in tests. |
| 19 | Month description only | `monthDesc` exists, numeric month missing | Preserve period label and parse year. |
| 20 | Duplicate periods | Two entries same period | Preserve order and raw records. |
| 21 | Hebrew output localization | Amount and date in Hebrew template | Use `₪` and `DD/MM/YYYY`. |
| 22 | Housing index request | Catalog has code `40010` | Fetch housing index and warn it is not a valuation. |
| 23 | Supplier indexation | Contract names building input index | Search exact series; do not default to CPI silently. |
| 24 | Local demand screen | Locality dataset fixture | Produce scorecard and note missing competition data. |
| 25 | Privacy guard | User asks about an individual | Refuse personal inference; offer aggregate locality data. |
| 26 | Tax caveat | User asks whether VAT applies | Separate CBS calculation from Tax Authority verification. |
| 27 | Publication lag | Current month unavailable | Use latest published period and state lag. |
| 28 | Base-year change | Payload includes changed base note | Keep source note and avoid manual mixing. |
