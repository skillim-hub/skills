# Israeli Official Source Reference

Access date: 2026-06-04

This reference separates official Israeli sources from planning heuristics. Do not treat market benchmark ranges as official rates.

## Official sources

| Topic | Official source | Verified use |
|---|---|---|
| VAT | Israel Tax Authority VAT history and guidance | Model VAT at 18% unless a newer official rate is confirmed |
| Price indices | Central Bureau of Statistics | Use construction input indices to update historic benchmarks |
| Planning and permits | Planning Administration, Rishuy Zamin, Mavat, fee calculator | Flag permit and fee checks; do not hard-code permit outcomes |
| Business licensing | Ministry of Interior business licensing service and Smart Order search | Check whether a business type requires a license |
| Accessibility | Commission for Equal Rights of Persons with Disabilities | Flag accessibility proof/review for public-facing businesses |
| Fire safety | Israel Fire and Rescue Authority | Flag fire-safety approval or declaration routes |
| Construction waste and asbestos | Ministry of Environmental Protection | Flag lawful waste handling and asbestos survey/removal |
| Health approval | Ministry of Health | Flag food, pool, hotel, clinic, and public-health-related businesses |
| Standards | Standards Institution of Israel and official regulation references | Cite standards only when verified; do not reproduce paid standards |

## VAT

Verified snippets:

- "1.1.25 עלה המע"מ ל-18%" — Israel Tax Authority VAT history.
- "effective January 1, 2025... will be 18%" — Knesset announcement.
- "The 2025 current rate of VAT is 18%" — PwC Worldwide Tax Summaries, reviewed 01-01-2026.

Estimator rule:

```text
Use 18% as the default VAT planning rate as of 2026-06-04.
Before issuing production advice, verify the current Israel Tax Authority rate.
```

Do not automate tax-invoice allocation-number decisions in this estimator. The Israel Invoice model has separate thresholds and API documentation.

## CBS price indices and API

Official CBS documentation states that the price-index API provides commands to fetch index subjects and index data. Verified parameters include `lang`, `format`, `download`, `page`, and `pagesize`. Verified formats include `xml`, `json`, `csv`, and `xls`.

Official API host examples:

```text
https://api.cbs.gov.il/index/catalog/TreeCalc
https://api.cbs.gov.il/index/data/price_all?download=false&format=xml&oldformat=true
```

Use the API or CBS publications to obtain actual index values. Do not hard-code dataset codes unless fetched and confirmed at runtime.

Formula:

```text
updated_cost = historical_cost * estimate_index / base_index
```

Important distinction:

```text
CBS construction input indices measure price-index movement. They do not publish official per-room renovation prices.
```

## Current index examples from CBS publications

The CBS March 2026 press release reports:

- "עליה של 0.2% במדד מחירי תשומה בבנייה למגורים, מרס 2026"
- "עליה של 0.1% במדד מחירי תשומה בבנייה למסחר ולמשרדים, מרס 2026"
- "מדד מחירי תשומה בבנייה למגורים... 101.7 נקודות"

Use these as examples only. Fetch the current month for live work.

## Planning and permits

Official sources verified:

- Rishuy Zamin is a digital platform for building licensing workflows.
- Mavat allows locating and viewing planning entities such as plans, applications, and appeals.
- The building permit fee calculator estimates future building-permit fees.

Estimator rule:

```text
Flag possible permit review for structural work, facade changes, balcony enclosure, change of use, shared-property work, signage, and other permit-sensitive work.
Do not state that a permit is or is not required without local committee review.
```

## Business licensing

Official sources verified:

- The Ministry of Interior application service is for businesses that must obtain a business license.
- The Smart Order search covers the Business Licensing Order and Accessibility Proof Order.
- Uniform specifications are intended to increase certainty and transparency.

Estimator rule:

```text
For shops, clinics, food businesses, salons, public reception, and customer-facing spaces, check whether the business type is listed in the Smart Order and whether municipal requirements apply.
```

## Accessibility

Official sources verified:

- Business licensing may require proof of accessibility.
- The Equal Rights law terminology is "חוק שוויון זכויות לאנשים עם מוגבלות" / "Equal Rights For Persons With Disabilities Law".
- Some small-business routes may use self-check or declaration tracks, but thresholds depend on the order and business classification.

Estimator rule:

```text
Flag accessibility review for public-facing businesses.
Do not hard-code a threshold unless the exact business classification is verified.
```

## Fire safety

Official sources verified:

- Israel Fire and Rescue provides business-license fire-safety guidance.
- Low fire-risk businesses may be routed to a declaration track.
- Fire requirements are use-specific and may not be fully described by a generic web page.

Estimator rule:

```text
Flag emergency lighting, exit signage, extinguishers, detection, sprinklers, evacuation paths, and fire authority approval/declaration as scope risks.
```

## Construction waste and asbestos

Official sources verified:

- The Ministry of Environmental Protection provides construction-waste information and authorized handling references.
- Municipal pages may place renovation waste responsibility on the renovator.
- Asbestos is a carcinogenic hazard; suspect work should use authorized asbestos professionals.

Estimator rule:

```text
Include waste handling in quote requests.
Do not price suspected asbestos as ordinary demolition.
```

## Health-related businesses

Official sources verified:

- The Ministry of Health gives approvals under the Business Licensing Order for public-health-related businesses.
- Food businesses have a dedicated Ministry of Health topic area.
- Certain clinics and health professions have separate licensing frameworks.

Estimator rule:

```text
For clinics and food businesses, add Ministry of Health or professional/facility licensing review where relevant.
```

## Israeli standards

Official sources verified:

- Standards published by the Standards Institution are generally voluntary.
- Standards can become mandatory through laws, regulations, or official documents.
- Examples include plumbing systems under SI 1205 and fire detection maintenance under SI 1220.

Estimator rule:

```text
Cite standard numbers only after verifying relevance.
Do not reproduce restricted standard text.
```

## Webhooks

No official webhook event names are applicable to this local estimator. None are added.
