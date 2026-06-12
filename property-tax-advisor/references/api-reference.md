# Israeli property-tax regulatory and service reference

This reference is an operational map, not a live legal database. Verify every rate, bracket, form, deadline, and URL against the official source on the action date.

## Source hierarchy

1. Primary legislation and regulations.
2. Annual municipal Arnona order for the exact local authority and year.
3. Formal notice, assessment, or decision sent to the taxpayer.
4. Published Tax Authority guidance and online services.
5. Municipal service pages, GIS layers, and forms.
6. Professional advice from a licensed Israeli lawyer, tax advisor, CPA, or appraiser.


## Live-source validation notes

The package was revalidated on 01/06/2026 against official and secondary sources. Use `references/verification-log.md` for exact snippets, URLs, and two-pass status.

| Item | Validated handling | Implementation impact |
|---|---|---|
| VAT | Current official VAT references show 18% from 01/01/2025. VAT is not a property tax, but may affect professional fees, construction services, and some real-estate workflows. | Keep VAT out of property-tax calculations unless the user asks about service invoices or transaction costs. |
| Purchase tax | Residential single-home brackets in the helper match the current Tax Authority calculator values published for 16/01/2025 through 15/01/2028. | Keep bundled brackets as examples and require official verification before filing. |
| Additional-home purchase tax | Current sources support the 8% and 10% example brackets used by the helper for the checked period. | Keep example brackets and warning text. |
| Arnona | 2026 local orders and national minimum/maximum tables confirm local-authority-specific annual rates and classifications. | Keep sample municipal rates clearly marked as non-official examples. |
| Mas Rechush | Direct-damage compensation remains the core current workflow. The 2026 vacant-land 1.5% framework was treated as a proposal unless enacted or assessed. | Add caution language; do not compute a current vacant-land Mas Rechush liability by default. |
| Betterment levy | Sources confirm the local-planning-committee framework and the common 50% uplift estimate, subject to exemptions and appraisal. | Keep the rough 50% estimate and warning. |
| data.gov.il CKAN | The documented public host and action paths remain discovery APIs, not tax-assessment endpoints. | Keep CKAN examples as dataset discovery only. |
| Webhooks | No official public webhook event names are used or referenced by this package. | Do not invent webhook events. Treat portals as form workflows unless official API docs say otherwise. |

## Regulations and legal instruments

| Subject | Hebrew title | English description | Practical use |
|---|---|---|---|
| Arnona authority | פקודת העיריות, צו המועצות המקומיות, פקודת המועצות המקומיות | Local-authority tax collection and municipal powers | Confirm collection authority and local billing powers |
| Annual Arnona | חוק ההסדרים במשק המדינה ותקנות הסדרים במשק המדינה (ארנונה כללית ברשויות המקומיות) | National framework for municipal Arnona rates, updates, minimums, and maximums | Check rate limits and annual update mechanism |
| Municipal order | צו ארנונה שנתי של הרשות המקומית | Local annual tariff order | Determine actual classification, zone, measurement method, and discounts |
| Arnona disputes | חוק הרשויות המקומיות (ערר על קביעת ארנונה כללית), התשל"ו-1976 | Objection and appeal framework | Determine objection grounds, route, and deadline |
| Discounts | תקנות ההסדרים במשק המדינה (הנחה מארנונה) | National discount categories and caps | Check eligibility, area caps, documents, and committee discretion |
| Purchase tax and land appreciation tax | חוק מיסוי מקרקעין (שבח ורכישה), התשכ"ג-1963 | National real-estate transaction tax law | Calculate or triage purchase tax, land appreciation tax, reliefs, and declarations |
| Mas Rechush compensation | חוק מס רכוש וקרן פיצויים, התשכ"א-1961 והתקנות מכוחו | Property Tax and Compensation Fund framework | Route direct-damage claims from war or hostile acts |
| Betterment levy | חוק התכנון והבנייה, התשכ"ה-1965, התוספת השלישית | Local planning betterment levy | Assess levy trigger, 50% mechanism, exemptions, appraiser disputes |
| Business signage | חוקי עזר עירוניים לשילוט | Local signage bylaws | Verify sign tax or signage permit charges |
| Business licensing | חוק רישוי עסקים, התשכ"ח-1968 וחוקי עזר | Business-license framework | Explain when municipal charges relate to licensing rather than Arnona |

## Official online services and datasets

No single national public API returns current Arnona liability for every Israeli property. Production workflows normally combine municipal documents, Tax Authority services, and user-provided notices.

| Service or dataset | Provider | Typical access | Data returned | Production caveat |
|---|---|---|---|---|
| Real Estate Taxation online declarations | Israel Tax Authority | gov.il online service | Purchase/sale declarations, payment workflows | Requires identity, permissions, and current official forms |
| Purchase-tax calculator or bracket publications | Israel Tax Authority | gov.il guidance/service pages | Current residential and non-residential purchase-tax brackets | Brackets update; verify year and buyer status |
| Property Tax and Compensation Fund claim service | Israel Tax Authority | gov.il online service | Damage-claim filing, claim number, status | Eligibility depends on event, evidence, geography, and regulations |
| Municipal Arnona account portals | Local authorities | Municipal website / personal area | Bills, balances, holder data, payments, forms | Formats differ by authority; authentication may be required |
| Annual Arnona orders | Local authorities | PDF/HTML on municipal website | Classification, zones, rates, measurement rules | PDFs change yearly; preserve source copy |
| data.gov.il CKAN API | Government data portal | Public JSON API | Datasets and metadata, sometimes local-authority codes and geospatial resources | Dataset availability varies; not a tax assessment API |
| Municipal GIS | Local authorities | Public map service or GIS portal | Zoning, street, parcel, neighborhood, plan layers | GIS layer is evidence aid, not always binding |
| Planning Administration / local committee systems | Planning authorities | Public planning portals | Plans, permits, parcels, committee data | Legal status and valuation require professional review |

## data.gov.il CKAN examples

Use the government data portal API to find public datasets. Query names change, so treat results as discovery aids.

### Search request

```http
GET https://data.gov.il/api/3/action/package_search?q=%D7%A8%D7%A9%D7%95%D7%99%D7%95%D7%AA%20%D7%9E%D7%A7%D7%95%D7%9E%D7%99%D7%95%D7%AA
Accept: application/json
```

### Search response shape

```json
{
  "help": "https://data.gov.il/api/3/action/help_show?name=package_search",
  "success": true,
  "result": {
    "count": 12,
    "results": [
      {
        "id": "dataset-id",
        "name": "local-authorities",
        "title": "Local authorities",
        "resources": [
          {
            "id": "resource-id",
            "format": "CSV",
            "url": "https://..."
          }
        ]
      }
    ]
  }
}
```

### Datastore request pattern

```http
GET https://data.gov.il/api/3/action/datastore_search?resource_id=<resource-id>&limit=5
Accept: application/json
```

### Common CKAN errors

| HTTP status | Meaning | Fix |
|---|---|---|
| 200 with `success: false` | CKAN action failed | Inspect `error` object; check action name and resource id |
| 404 | Dataset/resource not found | Repeat package search; resource may have changed |
| 409 | Invalid datastore query | Simplify filters and field names |
| 429 | Rate limit or throttling | Retry later and cache metadata |
| 500 | Portal or backend error | Retry; keep a fallback manual workflow |


## Public webhook and event-name policy

Do not invent webhook events for Israeli tax or municipal portals. This package does not rely on any official public webhook API for Arnona, Mas Rechush, purchase tax, land appreciation tax, betterment levy, or municipal service portals. If an authority later publishes an API with webhook events, update this reference only after capturing the official event names, host, request signature, retry policy, and error model.

## Structured local helper API

The included Python helper is not an official government API. It provides deterministic triage and example calculations.

### Arnona request

```json
{
  "municipality": "tel-aviv",
  "area_sqm": 80,
  "zone": "A",
  "usage": "residential",
  "months": 2,
  "discount": "senior",
  "discount_months": 2
}
```

### Arnona response

```json
{
  "authority": "municipality",
  "municipality": "tel-aviv",
  "usage": "residential",
  "zone": "A",
  "area_sqm": 80.0,
  "annual_rate_per_sqm": 105.0,
  "annual_charge": 8400.0,
  "period_charge": 1400.0,
  "discount_amount": 420.0,
  "payable": 980.0,
  "warnings": [
    "Sample rate used; verify against the current municipal Arnona order."
  ]
}
```

### Purchase-tax request

```json
{
  "price": 2400000,
  "buyer_profile": "additional_home",
  "contract_date": "15/03/2026"
}
```

### Purchase-tax response

```json
{
  "tax_type": "purchase_tax",
  "price": 2400000.0,
  "buyer_profile": "additional_home",
  "estimated_tax": 192000.0,
  "effective_rate": 0.08,
  "warnings": [
    "Sample brackets are not official. Verify current Israel Tax Authority brackets."
  ]
}
```

### Betterment-levy request

```json
{
  "planning_uplift": 300000,
  "ownership_share": 1.0,
  "exemption": false
}
```

### Betterment-levy response

```json
{
  "tax_type": "betterment_levy",
  "planning_uplift": 300000.0,
  "ownership_share": 1.0,
  "estimated_levy": 150000.0,
  "warnings": [
    "A licensed appraiser should review any material levy assessment."
  ]
}
```

## CLI error reference

| Code | Message | Cause | Fix |
|---|---|---|---|
| `UNKNOWN_MUNICIPALITY` | Municipality is not in sample table | Unsupported or misspelled municipality | Use `rates --municipalities` or enter a custom rate |
| `UNKNOWN_USAGE` | Usage is not available for municipality/zone | Unsupported classification | Use an available sample usage or official custom calculation |
| `UNKNOWN_ZONE` | Zone is not available | Invalid zone | Check annual Arnona order or run `rates` |
| `INVALID_AREA` | Area must be positive | Zero or negative sqm | Enter a positive numeric sqm |
| `INVALID_MONTHS` | Months must be from 1 to 12 | Invalid billing period | Enter 1-12 |
| `UNKNOWN_DISCOUNT` | Discount key not recognized | Typo or unsupported category | Run `rates --discounts` |
| `INVALID_PRICE` | Price must be positive | Zero or negative price | Enter transaction price |
| `INVALID_UPLIFT` | Planning uplift cannot be negative | Invalid betterment input | Enter zero or positive uplift |
| `DATE_FORMAT` | Date must be DD/MM/YYYY | Wrong localization | Enter a date such as 15/03/2026 |

## Official-source capture template

```text
Source title:
Authority:
URL or document identifier:
Publication year:
Access date:
Relevant section/page:
Extracted rate or rule:
Assumptions:
User document matched:
Confidence:
```

## Rate verification pattern

1. Locate the municipal order for the bill year.
2. Save the PDF or official HTML source.
3. Search for the exact classification.
4. Check zone table and street list.
5. Read the measurement clause.
6. Compare the annual rate per sqm to the bill.
7. Confirm discounts and exemptions in a separate section.
8. Preserve a screenshot or downloaded copy with access date.
