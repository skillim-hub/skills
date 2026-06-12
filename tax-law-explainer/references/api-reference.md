# Israeli Tax-Law Reference

This skill does not depend on a single public tax API. Treat this file as a structured reference for official sources, statutes, portals, form families, and local helper request/response formats. Verify current content through official publications before filing.

## Official source map

| Area | Source type | What to verify | Typical question |
|---|---|---|---|
| Income Tax Ordinance [New Version] | Statute | Income source, deduction rules, withholding, annual return duties, statements of capital | “Is this income taxable?” |
| VAT Law, 1975 | Statute | Dealer status, tax invoice, input VAT, reporting, zero rate, exemptions | “Should VAT be charged?” |
| Real Estate Taxation Law (Betterment and Purchase), 1963 | Statute | Betterment tax, purchase tax, apartment exemptions, reporting deadlines | “Is the apartment sale exempt?” |
| Income Tax Regulations | Regulations | Deduction limits, depreciation, bookkeeping, forms, withholding tables | “Can this expense be deducted?” |
| VAT Regulations | Regulations | Invoice details, input VAT documentation, periodic reporting | “Is this invoice valid?” |
| Land Taxation portal | Official portal | Property reporting, assessment status, payment, forms | “What must be filed after signing?” |
| Israel Tax Authority guidance | Official guidance | Thresholds, brackets, procedural updates, circulars | “What is the current threshold?” |
| Represented taxpayer systems | Official portal | Filing through authorized representatives | “Can a representative file this?” |
| Personal government portal | Official portal | Personal filings, payment, certificates | “Where can a consumer check a certificate?” |

## Citation discipline

When citing a law or official procedure, cite the law name, Hebrew term where useful, section or regulation number if known, topic of the section, verification note for changing amounts or dates, and caveat for facts that depend on residence, family unit, asset type, history, or documents.

## Structured helper API

The included Python client and CLI expose a local decision-support API. It does not call government systems.

### `TaxLawExplainerClient.explain`

Request:

```json
{
  "topic": "vat-registration",
  "user_type": "freelancer",
  "facts": {
    "activity_type": "consulting",
    "profession": "graphic designer",
    "annual_turnover": 120000,
    "start_date": "02/06/2026"
  },
  "language": "en"
}
```

Response:

```json
{
  "topic": "vat-registration",
  "language": "en",
  "summary": "Check VAT status before issuing documents or collecting VAT.",
  "decision_points": [
    "Classify the activity as business, profession, salary, hobby, or capital receipt.",
    "Check whether the profession is excluded from exempt dealer status.",
    "Compare expected turnover with the current official exempt-dealer threshold."
  ],
  "documents": ["Identity details", "Bank account confirmation", "Service contracts"],
  "warnings": ["Verify current thresholds, brackets, forms, and deadlines against official Israel Tax Authority publications."],
  "professional_help": false,
  "missing_facts": [],
  "legal_areas": ["VAT Law"]
}
```

### `TaxLawExplainerClient.validate_facts`

Request:

```json
{
  "topic": "real-estate-sale",
  "facts": {
    "asset_type": "residential_apartment",
    "purchase_date": "15/06/2018",
    "sale_date": "20/07/2026"
  }
}
```

Response:

```json
{
  "valid": false,
  "missing": ["purchase_price", "sale_price", "family_unit_holdings", "construction_rights"],
  "warnings": ["Verify current thresholds, brackets, and deadlines before producing final numbers."]
}
```

### `TaxLawExplainerClient.checklist`

Request:

```json
{ "workflow": "freelancer-onboarding", "language": "en" }
```

Response:

```json
{
  "workflow": "freelancer-onboarding",
  "language": "en",
  "steps": [
    "Classify activity and expected turnover.",
    "Check VAT status and profession restrictions.",
    "Open required files."
  ]
}
```

## CLI reference

```bash
python scripts/tax-law-explainer-cli.py list-topics
python scripts/tax-law-explainer-cli.py explain --topic vat-registration --business-type freelancer --annual-turnover 120000
python scripts/tax-law-explainer-cli.py checklist --workflow real-estate-sale
python scripts/tax-law-explainer-cli.py validate --topic real-estate-sale --facts-json '{"asset_type":"residential_apartment"}'
python scripts/tax-law-explainer-cli.py export-scenario --scenario freelancer_home_office --output scenario.json
```

## Error table

| Code | Trigger | Meaning | Recovery |
|---|---|---|---|
| `UNKNOWN_TOPIC` | Topic not in catalog | No structured template exists | Use `list-topics` |
| `UNKNOWN_WORKFLOW` | Workflow not in catalog | No checklist exists | Use `list-workflows` |
| `INVALID_LANGUAGE` | Language not `en` or `he` | Unsupported localization | Use English or Hebrew |
| `MISSING_FACTS` | Required facts absent | Conclusion would be unreliable | Supply facts or accept conditional answer |
| `UNVERIFIED_THRESHOLD` | Threshold-sensitive answer | Current official amount needed | Verify with Israel Tax Authority |
| `PROFESSIONAL_REVIEW_REQUIRED` | High-risk area | Adviser, attorney, appraiser, or official ruling needed | Escalate before filing or signing |
| `UNSUPPORTED_FILING` | Direct government filing requested | Helper cannot file | Use official portal or authorized representative |
| `COMPLIANCE_RISK` | Backdating, hiding, or fabrication requested | Unsafe request | Provide lawful correction route only |

## Topic catalog

| Topic | Main law area | Required facts | Current-data dependency |
|---|---|---|---|
| `vat-registration` | VAT Law | activity type, profession, expected turnover, start date | Exempt dealer threshold and excluded professions |
| `vat-invoice-correction` | VAT Law | VAT status, original invoice, report period, correction reason | Current correction procedure |
| `foreign-client-vat` | VAT Law | client residence, beneficiary, use location, contract | Zero-rate guidance |
| `expense-deductibility` | Income Tax Ordinance | expense type, business link, private use, invoice, payment | Deduction limits |
| `withholding-tax` | Income Tax Ordinance | payer, payee, certificate, payment type | Withholding rates and approvals |
| `annual-return` | Income Tax Ordinance | income sources, file status, spouse income, foreign assets | Filing exemptions and forms |
| `rental-income` | Income Tax Ordinance | residential/commercial, monthly rent, expenses, financing | Rental tracks and thresholds |
| `real-estate-sale` | Real Estate Taxation Law | asset, purchase date, sale date, prices, family holdings | Exemption caps and deadlines |
| `purchase-tax` | Real Estate Taxation Law | asset type, purchaser status, other apartments, price | Brackets and reliefs |
| `inheritance-apartment` | Real Estate Taxation Law | deceased status, heir status, prior holdings | Inheritance exemption conditions |


## Web-validated current reference values

Access date: 02/06/2026. These values are reference snapshots, not a substitute for the official portal at filing time.

| Item | Validated value or status | Source note |
|---|---|---|
| Standard Israeli VAT rate | 18%, effective from 01/01/2025 and still reflected in 2026 Tax Authority materials | Israel Tax Authority VAT history; Knesset VAT order notice |
| Exempt dealer turnover ceiling | ₪122,833 for 2026 | Open exempt dealer service and VAT amounts/rates page |
| Micro-business owner ceiling | Around ₪122,833 for 2026, aligned to the exempt-dealer ceiling | Small Business Owner topic and FAQ |
| Individual annual return | Form 1301 for 2025 tax year; non-online filing by 29/05/2026 and online filing by 30/06/2026 where applicable | 2025 annual report service |
| Withholding and bookkeeping confirmations | Official service provides withholding-at-source rates and bookkeeping confirmation information | `itc-gmishurim` service |
| Residential rental income exemption ceiling | ₪5,654 monthly ceiling referenced in current Tax Authority materials | Rental-income guide and 2026 monthly deduction booklet |
| Residential rental 10% track | Section 122 track allows 10% tax on qualifying Israeli residential rental income | Tax Authority rental-income guide |
| Purchase tax, single residential apartment | Snapshot: 0% to ₪1,978,745; 3.5% to ₪2,347,040; 5% to ₪6,055,070; 8% to ₪20,183,565; 10% above | Gov.il purchase-tax simulator; verify before use |
| Real-estate transaction declaration | 30-day declaration requirement for sale or purchase forms | Form 7000 and related services |
| Israel Invoice allocation number | Official service exists for allocation numbers for tax invoices | Israel Invoice topic |
| Tax Authority APIs | API documentation requires software-house/developer registration; full endpoint paths are not public in this package | Tax Authority API portal and SHAAM connection instructions |
| Webhook event names | Not applicable; the skill does not define or consume official webhooks | Package source review and public API portal review |

### Official API limitation

Do not present the local Python helper as an Israel Tax Authority API client. The helper is deterministic decision support. Official Tax Authority API access requires registration by a software house and its developers, and the full API documentation is available only after registration in the developer portal.
