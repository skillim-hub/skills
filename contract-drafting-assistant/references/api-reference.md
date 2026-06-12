# Israeli regulation and public-data reference

This skill is not an external drafting API integration. Treat this file as a source map for statutory references, public-data lookups, validation examples, and drafting controls. Verify current values before production use because taxes, thresholds, official forms, endpoints, and regulator guidance can change.

## Live validation baseline

Validated on 02/06/2026 against the official or authoritative sources listed in `references/verification-log.md`.

| Item | Current package position | Validation result |
|---|---|---|
| Standard Israeli VAT rate | Helper default remains `0.18` | Confirmed as 18% from 01/01/2025 and still reflected in 2026 official Tax Authority material |
| VAT clause text | Use "VAT at the lawful rate" and state included/excluded | Confirmed; keep contract text flexible instead of hardcoding permanent tax rates |
| Tax invoice and accounting documents | Use "lawful accounting documentation" unless tax-invoice status is confirmed | Confirmed; avoid demanding a tax invoice from a supplier that may not lawfully issue one |
| Withholding tax | Refer to a valid withholding certificate, not a guessed rate | Confirmed; official services publish certificate and bookkeeping information |
| Contract interpretation | Add a 2026 section 25 check for business contracts | Corrected in v3 after live validation |
| Public data API host | `https://data.gov.il/api/3/action/datastore_search` | Confirmed as CKAN Action API pattern |
| Bank of Israel exchange rates | `https://www.boi.org.il/PublicApi/GetExchangeRates?asJson=true` | Confirmed to return JSON on 02/06/2026; official exchange-rate page warns representative rates are not mandatory by law |
| Webhooks | None | Not applicable; the helper is local and has no webhook event names |

## Core statutes and drafting implications

| Area | Source | Use in drafting | Practical check |
|---|---|---|---|
| Contract formation, good faith, and interpretation | Contracts (General Part) Law, 1973, including 2026 section 25 amendment | Offer, acceptance, certainty, capacity, good faith, and interpretation | Make business terms explicit; add interpretation and schedule-priority wording where needed |
| Remedies | Contracts (Remedies for Breach of Contract) Law, 1970 | Cancellation, enforcement, damages, agreed compensation | Keep cure periods and agreed damages proportionate |
| Standard terms | Standard Contracts Law, 1982 | Reusable terms, clickwrap, standard service forms | Avoid terms that are unduly one-sided or hidden |
| Consumer transactions | Consumer Protection Law, 1981 | B2C disclosures, cancellation, misleading practices, distance sales | Add cancellation and disclosure review for consumers |
| VAT | Value Added Tax Law, 1975 and Tax Authority guidance | Price statements, invoices, VAT additions | State whether amounts include or exclude VAT and use the lawful rate |
| Income tax withholding | Income Tax Ordinance and Tax Authority certificate practice | Supplier payment language | Refer to valid withholding certificate; avoid calculating withholding in the contract |
| Bookkeeping/invoices | Income tax bookkeeping instructions and VAT invoice rules | Invoice and receipt obligations | Use "tax invoice" only where supplier may lawfully issue one |
| Privacy | Protection of Privacy Law, 1981 | Personal-data processing | Add purpose limitation, confidentiality, deletion/return |
| Data security | Protection of Privacy Regulations (Data Security), 2017 | Databases and personal-data systems | Add access controls, incident handling, subcontractor limits |
| Electronic signatures | Electronic Signature Law, 2001 | Digital execution | Permit electronic signature where context allows and no physical signature rule applies |
| Copyright | Copyright Law, 2007 | Creative works, code, text, design, photos | Choose assignment or license; preserve third-party exclusions |
| Arbitration | Arbitration Law, 1968 | Arbitration clauses | Define seat, language, appointment, interim relief |
| Sale of goods | Sale Law, 1968 | Delivery, conformity, title, risk | Define specifications, inspection, acceptance, remedies |
| Agency | Agency Law, 1965 | Authorized representatives and brokers | Define authority and commission |
| Guarantees | Guarantee Law, 1967 | Personal guarantees | Use clear guarantor language and review formalities |
| Pledges/security | Pledge Law, 1967 | Security interests | Refer to separate security instrument where needed |
| Interest and linkage | Adjudication of Interest and Linkage Law, 1961 | Late-payment calculations and court awards | Use reasonable contractual interest and verify statutory rates |
| Defective products | Defective Products Liability Law, 1980 | Product liability risk | Do not waive mandatory consumer/product protections |
| Labor classification | National Labor Court employee/contractor tests | Freelancer agreements | Flag employee-like facts for review |

## Official lookup patterns

The following examples show common public-data patterns. Endpoints, dataset identifiers, and field names can change; verify against the current official portal before relying on them.

### 1. Public dataset search pattern

Many Israeli government datasets are exposed through a CKAN-compatible `datastore_search` endpoint on the government data portal.

**Purpose:** Find a registry row, lookup list, or published table by dataset resource identifier.

**Example request**

```bash
curl -G "https://data.gov.il/api/3/action/datastore_search"   --data-urlencode "resource_id=<RESOURCE_ID>"   --data-urlencode "q=515000000"   --data-urlencode "limit=5"
```

**Example successful response shape**

```json
{
  "success": true,
  "result": {
    "include_total": true,
    "limit": 5,
    "records": [
      {
        "_id": 1,
        "Company_Number": "515000000",
        "Company_Name": "Example Ltd",
        "Status": "Active"
      }
    ],
    "total": 1
  }
}
```

**Example error response shape**

```json
{
  "success": false,
  "error": {
    "message": "Not found: Resource was not found",
    "__type": "Not Found Error"
  }
}
```

**Drafting use:** Confirm business identifiers before inserting them. Do not treat a portal row as proof of signing authority.

### 2. Companies and partnerships lookup

**Possible source:** Companies Registrar public datasets on data.gov.il and the Corporations Authority online search.

**Typical fields**

| Field | Drafting use |
|---|---|
| Company number / ח.פ. | Party identification |
| Company name / שם חברה | Exact legal name |
| Status | Flag inactive/dissolved company |
| Address | Optional reference only; confirm with user |
| Type | Company, partnership, nonprofit |

**Example request pattern**

```bash
curl -G "https://data.gov.il/api/3/action/datastore_search"   --data-urlencode "resource_id=<COMPANIES_RESOURCE_ID>"   --data-urlencode "q=<COMPANY_NUMBER>"   --data-urlencode "limit=1"
```

**Example normalized response for the helper**

```json
{
  "legal_name": "דוגמה בע״מ",
  "registration_number": "515000000",
  "status": "active",
  "source": "government_data_portal",
  "checked_at": "02/06/2026"
}
```

**Error table**

| Code / symptom | Meaning | Drafting response |
|---|---|---|
| `success=false` | Portal or resource error | Use placeholder and request verification |
| `total=0` | No matching record | Ask for exact number or legal name |
| Multiple records | Query too broad | Search by exact ח.פ. |
| Inactive status | Legal-capacity/signing risk | Add risk note and request legal review |
| Name mismatch | User-supplied name differs | Use official name only after confirmation |

### 3. Licensed business / municipal permits

**Possible source:** Municipal licensing portals, official permit documents, or user-uploaded permits.

**Request pattern:** No single national API should be assumed for every municipality.

```bash
# Manual verification placeholder
open "<municipality business licensing search page>"
search "business name / address / license number"
record "license number, holder, address, validity date"
```

**Drafting use:** For food, beauty, childcare, events, renovations, transport, and regulated local services, add a representation that the provider holds required licenses and permits.

### 4. VAT and tax invoice validation

**Possible source:** Tax Authority guidance, accountant confirmation, supplier documentation.

**No contract should calculate legal tax status from facts alone.** The draft should state the commercial VAT convention and require lawful tax documentation. The current helper default is 18%, validated on 02/06/2026, but the contract clause should normally say "lawful rate".

**Example clause data**

```json
{
  "price_nis": 12000,
  "vat_rate_assumption": 0.18,
  "vat_treatment": "plus_vat",
  "invoice_document": "חשבונית מס כדין",
  "withholding_tax": "subject to valid withholding certificate"
}
```

**Drafting examples**

- B2B plus VAT: "לכל סכום יתווסף מע״מ כדין כנגד חשבונית מס כדין."
- VAT included: "הסכום כולל מע״מ כדין וישולם כנגד חשבונית מס/קבלה כדין, לפי סוג העוסק."
- Exempt dealer or non-tax-invoice issuer: "התשלום יבוצע כנגד מסמך חשבונאי כדין המתאים לסוג העוסק."

**Error table**

| Symptom | Meaning | Drafting response |
|---|---|---|
| VAT omitted | Price ambiguity | Add placeholder and risk note |
| "invoice" requested from exempt dealer | Wrong document type | Use "מסמך חשבונאי כדין" |
| Gross-up requested in cross-border deal | Tax allocation risk | Add accountant/legal review note |
| Withholding rate inserted without certificate | Tax accuracy risk | Refer to certificate rather than rate |

### 5. Bank of Israel exchange-rate API pattern

**Purpose:** Foreign currency price conversion or linkage clause.

**Example request pattern**

```bash
curl "https://www.boi.org.il/PublicApi/GetExchangeRates?asJson=true"
```

**Example response shape observed on 02/06/2026**

```json
{
  "exchangeRates": [
    {
      "key": "USD",
      "currentExchangeRate": 2.825,
      "currentChange": 0.4265908283,
      "unit": 1,
      "lastUpdate": "2026-06-02T12:21:03.484464Z"
    }
  ]
}
```

**Drafting use:** If pricing is linked to USD/EUR, define source, publication date, fallback if no rate is published, and whether VAT is calculated in NIS. The Bank of Israel describes representative rates as indicators with no obligatory legal status, so the agreement must define the chosen rate source.

**Error table**

| Symptom | Meaning | Drafting response |
|---|---|---|
| Missing currency | Currency not published in response | Use another official source or manual rate |
| No rate on payment date | Holiday/weekend | Use latest published representative rate if the contract says so |
| Dispute over rate time | Clause too vague | Define date and source in contract |
| API unavailable | Operational issue | Use fallback clause |

### 6. Privacy/data-security control evidence

**Possible source:** User questionnaires, vendor security exhibits, regulator guidance.

**Request/response template for internal intake**

```json
{
  "personal_data_processed": true,
  "data_categories": ["customer contact details", "service history"],
  "sensitive_data": false,
  "subprocessors": ["cloud hosting provider"],
  "security_controls": ["role-based access", "password policy", "backup"],
  "breach_notice_hours": 72
}
```

**Drafting output**

```json
{
  "privacy_schedule_required": true,
  "recommended_clauses": [
    "purpose limitation",
    "confidentiality",
    "access controls",
    "incident cooperation",
    "return or deletion at termination",
    "subprocessor approval"
  ],
  "legal_review": "required if sensitive data, children, health, finance, or large database"
}
```

## Validation examples for helper scripts

### Israeli ID checksum

**Request**

```json
{"id_number": "123456782"}
```

**Response**

```json
{"valid": true, "normalized": "123456782"}
```
