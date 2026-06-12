# Test Scenarios

Use these scenarios to validate parsing, classification, scoring, localization, and operational routing.

| # | Scenario | Expected result |
|---:|---|---|
| 1 | Reshumot publication includes final regulation and no future date | `enacted` |
| 2 | Reshumot publication includes commencement on 01/01/2027 | `future-effective` |
| 3 | Knesset OData bill with no final publication | `bill` |
| 4 | Knesset bill contains public consultation words | `draft-regulation` only when draft terms dominate |
| 5 | Regulator FAQ about cancellation rights | `guidance` |
| 6 | Authority notice announces inspection campaign | `enforcement` |
| 7 | Public consultation page includes deadline 30/06/2026 | `draft-regulation` and response deadline extracted |
| 8 | HTML page contains script tags | Visible text excludes script content |
| 9 | RSS feed item includes `pubDate` | Date parsed |
| 10 | Atom entry includes `updated` | Date parsed |
| 11 | JSON OData response contains `value` list | Records parsed |
| 12 | JSON response contains `items` list | Records parsed |
| 13 | Invalid JSON source | Parse error raised |
| 14 | HTTP 500 source | Fetch error raised |
| 15 | Online store profile with cancellation keyword | High relevance for ecommerce item |
| 16 | Food profile receives privacy-only update | Filtered out unless keyword matches |
| 17 | Update includes ₪10,000 | Amount extracted |
| 18 | Hebrew date `02/06/2026` | Parsed as 2 June 2026 |
| 19 | Hebrew digest requested | Dates rendered as `DD/MM/YYYY` |
| 20 | English digest requested | Dates rendered as ISO where appropriate |
| 21 | Duplicate title and URL with different score | Higher score retained |
| 22 | Profile id mismatch in CLI scan | Error returned |
| 23 | Sandbox config generation | Inline sources created |
| 24 | Production config generation | Official source URLs created |
| 25 | Empty source text | Empty update list |
| 26 | Scanned PDF placeholder text | Manual review note required |
| 27 | Guidance conflicts with statute | Legal review flagged |
| 28 | Consultation deadline passed | Mark as late and keep final-rule watch |
| 29 | Source page changed without date | Use retrieval date only as metadata |
| 30 | Employer update includes fine and deadline | Critical or high severity |
| 31 | Consumer notice omits legal basis | Mark as guidance or enforcement context |
| 32 | Tax notice affects invoices | Accountant review flagged |


## Web validation scenarios

| # | Scenario | Expected result |
|---:|---|---|
| 31 | VAT rate conflict between a cached article and current Tax Authority page | Prefer current official Tax Authority or Reshumot source |
| 32 | Knesset OData returns a geo-block page | Mark source unavailable and retry with official Knesset page |
| 33 | Government Legislation Site item has an open comment deadline | Classify as `draft-regulation` with response deadline |
| 34 | Israel Invoice threshold changes mid-year | Use effective date and route to accountant review |
| 35 | A public guide contains a numeric threshold not present in the source text | Remove the threshold or mark as illustrative fixture |
