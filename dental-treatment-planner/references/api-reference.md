# Israeli Interface and Regulatory Reference

This package is offline-first. No official, comprehensive, public Israeli dental-price API or provider webhook feed is assumed. Treat provider prices, HMO dental benefits, supplementary-insurance rules, and clinic-specific quotes as source data that must be imported, dated, and reviewed.

Use this document as the interface and compliance reference for production integrations. Treat all `/v1/...` examples below as local service contracts, not as Maccabident, Clalit Smile, Ministry of Health, or Tax Authority endpoint paths.


## Web-validated source snapshot

Access date for all rows: 04/06/2026. Keep the complete two-pass source list in `verification-log.md`.

| Topic | Current source-backed handling |
|---|---|
| VAT rate | Use 18% as the default simulation rate when `include_vat=true`. The rate was corrected from 17% after live validation. |
| VAT classification | Do not decide whether a dental invoice is taxable. The planner may simulate VAT only when a user explicitly requests taxable-item modeling. |
| Children under 18 | Model eligibility as a check, not as a guaranteed zero price. Ministry of Health states preventive care is without payment and preservative/restorative care is with low copay through HMOs. |
| Age 72 and above | Model age-based benefits as a check. Ministry of Health states preventive, preservative and some rehabilitative care is available through HMOs, with item-level copays. |
| Maccabident | Prefer item-level import from the official 2026 tariff PDF or the current rights page. Avoid one universal discount. |
| Clalit Smile and Clalit Mushlam | Prefer item-level and plan-level rules from current Clalit pages. Verify age range, waiting period and plan membership. |
| Public APIs and webhooks | No official public tariff API host, endpoint path, or webhook event name was confirmed for provider pricing. Do not automate scraping without permission and source review. |

## Source register

| Source or rule | Purpose | Production handling |
|---|---|---|
| Ministry of Health public information and professional licensing resources | Verify dentist/specialist status, public guidance, and professional obligations | Prefer official pages and manual verification where no stable API exists |
| Dentists Ordinance and related professional rules | Licensing and professional conduct framework | Do not present output as diagnosis or dental prescription |
| Patient Rights Law, 5756-1996 | Informed consent, medical information, patient autonomy | Preserve clinical decision-making and consent boundaries |
| National Health Insurance Law and HMO/supplementary-plan publications | Eligibility, age benefits, co-payments, service route | Verify current plan terms and waiting periods |
| Consumer Protection Law and price-disclosure/cancellation rules | Written quote, transparency, consumer notices | Ask for written quote and excluded items |
| Protection of Privacy Law and Data Security Regulations, 5777-2017 | Health-data handling and security | Minimize, encrypt, log access, and obtain consent |
| VAT Law and Israeli tax-administration publications | Tax classification, invoice handling, business expense questions | Use 18% only for explicit VAT simulation; verify invoice classification with clinic and accountant |
| HMO dental networks such as Maccabident and Clalit Smile | Clinic route, published benefits, appointment availability | Treat published prices as dated inputs, not universal current truth |
| Private clinic quote | Binding commercial source for the specific patient | Require written quote, validity period, exclusions, and provider identity |

## Integration principle

Use dated local tables rather than brittle scraping. Store each tariff row with:

```json
{
  "source_name": "clinic_quote_or_provider_tariff",
  "source_date": "04/06/2026",
  "access_date": "04/06/2026",
  "provider": "private",
  "region": "center",
  "treatment_code": "crown_porcelain",
  "price_min_ils": 2200,
  "price_max_ils": 4500,
  "includes_lab": true,
  "includes_imaging": false,
  "notes": "Example only; replace with current written source."
}
```

## Local API-equivalent contract

A production service can expose the following local endpoints. The included CLI and client implement the same shape without network calls.

### `GET /v1/catalog`

Return available treatment codes.

Request:

```http
GET /v1/catalog?provider=private&region=center HTTP/1.1
Accept: application/json
```

Response:

```json
{
  "generated_on": "04/06/2026",
  "source_policy": "local dated tables; no external provider API assumed",
  "currency": "ILS",
  "items": [
    {
      "code": "cleaning",
      "description": "Dental hygienist cleaning",
      "category": "preventive",
      "price_min_ils": 220,
      "price_max_ils": 420,
      "visits": 1,
      "minutes": 45,
      "requires": []
    }
  ]
}
```

Errors:

| Code | Meaning | Fix |
|---:|---|---|
| 400 | Unsupported provider or region | Validate against provider and region lists |
| 404 | Catalog not loaded | Load dated tariff table |
| 409 | Catalog expired | Refresh tariff data and source date |
| 500 | Internal mapping error | Inspect treatment-code mapping |

### `POST /v1/estimate`

Estimate a plan.

Request:

```http
POST /v1/estimate HTTP/1.1
Content-Type: application/json
Accept: application/json
```

```json
{
  "context": {
    "provider": "maccabident",
    "region": "center",
    "start_date": "15/07/2026",
    "max_visits_per_month": 3,
    "include_vat": false,
    "vat_rate": 0.18,
    "insurance": {
      "name": "supplementary_example",
      "discount_pct": 25,
      "annual_limit_ils": 3000,
      "used_annual_ils": 400,
      "waiting_period_met": true,
      "covered_categories": ["diagnostic", "preventive", "restorative"]
    }
  },
  "treatments": [
    {"code": "exam"},
    {"code": "cleaning"},
    {"code": "filling_small", "tooth": "16"}
  ]
}
```

Response:

```json
{
  "provider": "maccabident",
  "region": "center",
  "subtotal_ils": 833.18,
  "covered_ils": 208.30,
  "patient_before_vat_ils": 624.88,
  "vat_ils": 0.0,
  "total_patient_ils": 624.88,
  "visits": 3,
  "chair_minutes": 120,
  "warnings": [],
  "assumptions": ["Amounts are planning estimates, not binding medical quotes."],
  "lines": [
    {
      "code": "exam",
      "description": "Comprehensive dental examination",
      "category": "diagnostic",
      "quantity": 1,
      "gross_ils": 204.75,
      "covered_ils": 51.19,
      "patient_ils": 153.56
    }
  ],
  "schedule": [
    {"visit_number": 1, "date": "15/07/2026", "code": "exam", "minutes": 30}
  ]
}
```

Errors:

| Code | Error | Meaning | Fix |
|---:|---|---|---|
| 400 | `invalid_json` | Body is not valid JSON | Send valid UTF-8 JSON |
| 400 | `missing_treatments` | Treatment list is empty | Add at least one treatment |
| 400 | `unknown_treatment_code` | Code is not in catalog | Map clinic wording to supported code |
| 400 | `unsupported_provider` | Provider profile is missing | Add provider profile or choose supported route |
| 400 | `unsupported_region` | Region factor is missing | Add region or choose supported region |
| 422 | `clinical_dependency_warning` | Missing exam, X-ray, imaging, or prerequisite | Add prerequisite or mark completed externally |
| 422 | `strict_validation_failed` | Strict mode blocks warnings | Resolve warnings or disable strict mode |
| 409 | `benefit_exhausted` | Annual cap is fully used | Show self-pay amount or update benefit data |
| 500 | `pricing_rule_error` | Internal price rule failed | Inspect catalog data types and ranges |

### `POST /v1/compare`

Compare provider profiles with the same treatment list.

Request:

```json
{
  "providers": ["private", "maccabident", "clalit_smile"],
  "plan": {
    "context": {
      "region": "tel_aviv",
      "start_date": "01/08/2026"
    },
    "treatments": [
      {"code": "exam"},
      {"code": "panoramic_xray"},
      {"code": "implant", "tooth": "36"},
      {"code": "implant_crown", "tooth": "36"}
    ]
  }
}
```

Response:

```json
{
  "currency": "ILS",
  "ranked": [
    {
      "provider": "maccabident",
      "total_patient_ils": 7883.90,
      "visits": 8,
      "warnings": []
    },
    {
      "provider": "clalit_smile",
      "total_patient_ils": 8085.02,
      "visits": 8,
      "warnings": []
    }
  ]
}
```

### `GET /v1/provider-coverage`

Return known plan rules. This endpoint must be dated and source-backed in production.

Request:

```http
GET /v1/provider-coverage?provider=maccabident&plan=supplementary_example HTTP/1.1
```

Response:

```json
{
  "provider": "maccabident",
  "plan": "supplementary_example",
  "source_date": "04/06/2026",
  "rules": [
    {
      "category": "preventive",
      "discount_pct": 25,
      "annual_limit_ils": 3000,
      "waiting_period_months": 0
    },
    {
      "category": "prosthodontics",
      "discount_pct": 15,
      "annual_limit_ils": 3000,
      "waiting_period_months": 6
    }
  ],
  "disclaimer": "Example only. Replace with current provider source."
}
```

Errors:

| Code | Meaning | Fix |
|---:|---|---|
| 404 | Plan not found | Load current plan table |
| 409 | Source date too old | Refresh plan data |
| 451 | Use restricted | Stop automated retrieval if source terms prohibit it |

## Webhooks

No provider webhook event names are defined by this package. Do not invent events such as `price.updated` or `eligibility.changed` unless an implementing service owns those events and documents them internally.

## Data-quality controls

- Every price row must have `source_name` and `source_date`.
- Every provider benefit must have `plan_name`, `category`, `waiting_period`, and `annual_limit`.
- Every estimate must display “planning estimate” and “not a binding quote.”
- Every clinical warning must remain visible in API and UI output.
- Every stored treatment plan containing health information must be protected under a privacy and security process.
- Every export to accountants must exclude unnecessary clinical details unless the patient explicitly requests inclusion.

## Security and privacy

Treat dental plans as health information:

- Use data minimization.
- Avoid storing ID numbers unless legally required.
- Encrypt at rest and in transit.
- Restrict access by role.
- Log access to patient records.
- Delete draft estimates on request.
- Separate clinical notes from bookkeeping exports.
- Avoid sending sensitive plans through unsecured email.

## Tax and invoice boundary

The planner can help organize payments and receipts. It must not decide deductibility, employee benefit taxation, VAT treatment, or business-expense classification. Route those questions to a licensed accountant or tax adviser.
