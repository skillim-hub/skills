# Israeli Regulation and Data Reference

This reference lists official Israeli sources and data categories needed for a reliable Mas Shevach estimate. Some sources are public web forms or professional systems rather than conventional APIs. Treat each as an authoritative data or filing interface and verify availability, authentication, and schema before production use.

## Source map

| Source / system | Hebrew name | Purpose | Typical access |
|---|---|---|---|
| Israel Tax Authority real-estate taxation systems | מיסוי מקרקעין, רשות המסים | Filing declarations, checking assessments, payment certificates, exemption forms | Representative portal, personal identification, tax-office workflow |
| Israel Tax Authority forms and guides | טפסים והוראות ביצוע של רשות המסים | Legal interpretations, declaration forms, exemption notes | Public website / professional publications |
| Real Estate Taxation Law | חוק מיסוי מקרקעין (שבח ורכישה), תשכ"ג-1963 | Primary statutory basis for Mas Shevach and purchase tax | Official law database |
| Tax Ordinance | פקודת מס הכנסה | Capital-gain rates, high-income surtax, depreciation connections | Official law database |
| Central Bureau of Statistics CPI | מדד המחירים לצרכן, הלמ"ס | CPI values for indexation | Public datasets / tables |
| Israel Land Registry | לשכת רישום המקרקעין / טאבו | Ownership, rights, registration approvals | Government services / paid extracts |
| Israel Land Authority | רשות מקרקעי ישראל | Leasehold rights, consent, capitalization, rights data | Online services / representative workflow |
| Municipal betterment levy systems | היטל השבחה ברשות המקומית | Betterment levy deduction and closing certificates | Municipality portals |
| VAT authority guidance | מע"מ | Possible VAT implications for business real estate | Tax Authority systems / professional guidance |

## Practical API-equivalent contracts

### Official CPI lookup and indexation data

Use official CPI values from the Central Bureau of Statistics. The official CBS price-index API page documents these paths:

```http
GET https://api.cbs.gov.il/index/catalog/tree?format=json&download=false&period=M
GET https://api.cbs.gov.il/index/data/price?id=120010&format=json&download=false
GET https://api.cbs.gov.il/index/data/price?id=120010&format=json&download=false&startPeriod=01-2000&endPeriod=12-2019
GET https://api.cbs.gov.il/index/data/calculator/120010?value=100&date=2018-01-01&toDate=2019-01-01&format=json&download=false
```

`120010` is the CBS example code for the general Consumer Price Index. Confirm the exact series and base before using values in a tax filing.

If integrating into an internal service, normalize the official CBS response into this local shape:

```json
{
  "source": "Central Bureau of Statistics",
  "series": "consumer_price_index",
  "series_code": "120010",
  "month": "2025-06",
  "index_value": 108.6,
  "base": "current_official_base",
  "published_at": "2025-07-15",
  "is_final": true,
  "official_url": "https://api.cbs.gov.il/index/data/price?id=120010&format=json&download=false"
}
```

Validation rules:

| Field | Rule |
|---|---|
| `month` | Must be `YYYY-MM`; document whether the known-index date or transaction month is used. |
| `index_value` | Positive number. |
| `base` | Must match for purchase and sale values or be converted to a common base. |
| `is_final` | Prefer final values; flag provisional data. |
| `series_code` | Confirm the correct CPI series before filing. |

Common errors:

| Error | Cause | Action |
|---|---|---|
| `CPI_NOT_FOUND` | Requested month unavailable | Use latest official month only if clearly disclosed, otherwise stop. |
| `CPI_BASE_MISMATCH` | Purchase and sale CPI use different bases | Convert to common base before calculation. |
| `CPI_PROVISIONAL` | Final index not published | Mark result as preliminary. |
| `CPI_MONTH_AMBIGUOUS` | User supplied a date but not the index month rule | Ask or apply the documented known-index convention. |
| `CPI_SERIES_UNVERIFIED` | Series code was not confirmed | Stop and verify the CBS index series. |

### VAT and business-real-estate reference

The current standard Israeli VAT rate is 18%, effective from 01/01/2025. The skill does not calculate VAT; it flags VAT review for business, commercial, mixed-use, and entity-seller transactions.

### Tax rate reference

The CLI default `tax_rate=0.25` is an estimate assumption for common individual real-gain scenarios. It is not a full legal rate engine. Verify:
- historic real-gain period rules,
- company or partnership taxation,
- high-income surtax,
- the additional 2% tax on certain capital income introduced from 2025 where applicable,
- foreign-resident withholding and exemption restrictions.

### Tax calculation request

For internal services or worksheets, use this request model:

```json
{
  "purchase_date": "2008-06-01",
  "sale_date": "2025-06-01",
  "purchase_price": 1000000,
  "sale_price": 2400000,
  "purchase_costs": 50000,
  "sale_costs": 60000,
  "improvements": 150000,
  "depreciation_claimed": 0,
  "ownership_share": 1.0,
  "property_type": "residential_apartment",
  "is_qualifying_residential_apartment": true,
  "cpi_purchase": 82.4,
  "cpi_sale": 108.6,
  "linear_relief_start_date": "2014-01-01",
  "tax_rate": 0.25,
  "exemption_code": null
}
```

Example response:

```json
{
  "adjusted_basis": 1200000.0,
  "net_sale_proceeds": 2340000.0,
  "gross_gain": 1140000.0,
  "indexed_basis": 1581553.3981,
  "inflationary_gain": 381553.3981,
  "real_gain": 758446.6019,
  "linear_taxable_share": 0.6714,
  "taxable_real_gain": 509185.0,
  "estimated_tax": 127296.25,
  "warnings": [
    "Verify CPI values against the official Central Bureau of Statistics table.",
    "Verify residential exemption eligibility before filing."
  ],
  "assumptions": [
    "Tax rate assumed at 25.00%.",
    "Linear relief date assumed as 2014-01-01."
  ]
}
```

### Filing or declaration reference

A production system should not auto-file from this skill. Produce a structured worksheet for the professional filing process.

Normalized declaration payload for professional review:

```json
{
  "seller": {
    "type": "individual",
    "residency": "israel_resident",
    "ownership_share": 1.0
  },
  "asset": {
    "type": "residential_apartment",
    "block": "0000",
    "parcel": "000",
    "subparcel": "00",
    "address": "example only"
  },
  "transaction": {
    "purchase_date": "2008-06-01",
    "sale_date": "2025-06-01",
    "purchase_value": 1000000,
    "sale_value": 2400000
  },
  "calculation": {
    "adjusted_basis": 1200000,
    "real_gain": 758446.60,
    "taxable_real_gain": 509185.00,
    "estimated_tax": 127296.25
  },
  "exemption_claim": {
    "claimed": false,
    "type": null,
    "notes": "Linear relief estimate only."
  },
  "attachments": [
    "purchase_contract",
    "sale_contract",
    "purchase_tax_assessment",
    "improvement_invoices",
    "broker_invoice",
    "legal_fee_invoice"
  ]
}
```

## Regulation checks to cite in a professional memo

Use exact current provisions when preparing a filing. At minimum, verify:

1. Definition of `sale`, `right in real estate`, `value of sale`, and `value of purchase` under the Real Estate Taxation Law.
2. Deductible expenses under the real-estate taxation regime.
3. Residential-apartment exemption provisions, including single qualifying apartment and inherited apartment conditions.
4. Linear relief provisions for qualifying residential apartments, including effective dates and transitional restrictions.
5. Inflationary amount and real gain definitions.
6. Depreciation treatment and connection to the Income Tax Ordinance.
7. High-income surtax and marginal tax interactions.
8. Foreign resident restrictions and documentation.
9. Reporting deadlines, payment deadlines, interest, linkage, fines, and objections.
10. Special regimes: urban renewal, Tama 38, evacuation/construction, combination transactions, gifts, trusts, companies, and partnerships.

## Error table for calculation services

| Code | Severity | Meaning | Recommended message |
|---|---|---|---|
| `INVALID_DATE` | Error | Date cannot be parsed | Use `YYYY-MM-DD` in CLI or `DD/MM/YYYY` in Hebrew worksheets. |
| `SALE_BEFORE_PURCHASE` | Error | Sale date is not after purchase date | Correct transaction dates. |
| `NEGATIVE_AMOUNT` | Error | Money field is negative | Enter non-negative amount; use costs in the correct field. |
| `INVALID_SHARE` | Error | Ownership share is not greater than 0 and at most 1 | Enter a decimal fraction such as `0.5`. |
| `UNKNOWN_PROPERTY_TYPE` | Error | Property type is unsupported | Use a supported enum or classify as `other`. |
| `CPI_PAIR_REQUIRED` | Error | Only one CPI value supplied | Provide both purchase and sale CPI values or omit both. |
| `CPI_NOT_POSITIVE` | Error | CPI value is zero or negative | Use official positive index values. |
| `EXEMPTION_NOT_SUPPORTED` | Warning | Exemption label is informational only | Do not reduce tax without verifying conditions. |
| `BUSINESS_USE_REVIEW` | Warning | Asset may have depreciation/VAT/business-income issues | Obtain professional review. |
| `FOREIGN_RESIDENT_REVIEW` | Warning | Seller is a foreign resident | Verify exemption and withholding rules. |

## Data quality rules

- Store all money amounts in NIS as decimals or integer agorot in production.
- Store dates as ISO strings internally.
- Preserve user-supplied source notes for CPI and costs.
- Never silently apply an exemption.
- Show every assumption that reduces tax.
- Keep the calculation deterministic and auditable.


### Official forms and services checked in 2026

| Item | Confirmed official wording/use |
|---|---|
| Form 7000 | Declaration on sale and purchase of real-estate property; 30-day filing deadline appears on the official service page. |
| Form 7000b | Declaration for sale of real-estate right where gain is assessed under income tax and section 50 exemption is requested. |
| Form 7002 | Declaration for sale of real-estate right, referenced by Tax Authority forms and receipt PDFs. |
| Form 7003 | Request to spread Mas Shevach calculation for up to four years. |
| Form 7914 | Appendix for sale of qualifying residential apartment taxable under beneficial linearity. |
| Form 2988 | Additional seller request for Mas Shevach exemption on a qualifying residential apartment. |
| Self-assessment calculator | Official service for Mas Shevach self-assessment with or without saving. |

### Webhook and API-host status

No official webhook event names were found for this non-API skill. The package provides a local CLI case workflow only. The only official API host verified for this package is `api.cbs.gov.il` for CBS price-index data.
