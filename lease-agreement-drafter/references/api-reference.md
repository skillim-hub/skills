# API and Regulation Reference

This is a non-network skill. It does not require a live government API. Treat the Python module and CLI as the local interface, and treat the cited Israeli statutes and public authority materials as legal reference points that must be checked against the current official text before signing.

## Local Python API

### Import

```python
from lease_agreement_drafter import LeaseAgreementDrafterClient
```

### Client

```python
client = LeaseAgreementDrafterClient.from_env(environment="sandbox")
```

Environment variables:

| Variable | Description |
| --- | --- |
| `LEASE_DRAFTER_ENV` | `sandbox` or `production` |
| `LEASE_DRAFTER_API_KEY` | Optional service token when wrapping the local package |
| `LEASE_DRAFTER_LOCALE` | Defaults to `he-IL` |

### Request example

```json
{
  "landlord": {"name": "דנה כהן", "id_number": "123456789"},
  "tenant": {"name": "נועם לוי", "id_number": "987654321"},
  "property": {
    "property_type": "apartment",
    "address": "הרצל 10",
    "city": "חיפה",
    "rooms": 3
  },
  "terms": {
    "start_date": "01/08/2026",
    "end_date": "31/07/2027",
    "monthly_rent_ils": 5200,
    "security_deposit_ils": 10400
  },
  "language": "he"
}
```

### Response example

```json
{
  "id": "lease_8f4a2c1b9e01",
  "status": "drafted",
  "title": "Apartment Lease: הרצל 10",
  "markdown": "# טיוטת הסכם שכירות - דירה",
  "findings": [],
  "checklist": ["Verify identity numbers and signing authority."],
  "environment": "sandbox"
}
```

### Public methods

| Method | Purpose |
| --- | --- |
| `from_env` | Build a client from environment variables |
| `validate` | Return structured findings for a request |
| `validate_async` | Async validation wrapper |
| `draft` | Generate a structured draft result |
| `draft_async` | Async draft wrapper |
| `scan_template` | Check an existing template for common missing clauses |
| `scan_template_async` | Async template scan wrapper |
| `render_clause_index` | Extract section headings from a draft |
| `export_markdown` | Save draft Markdown to disk |
| `production_checklist` | Return signing and operational checks |
| `request_schema` | Return a compact JSON schema outline |
| `error_catalog` | Return validation code descriptions |

## CLI reference

### Create draft

```bash
lease-agreement-drafter draft --env sandbox --input request.json --output draft.md
```

### Audit existing draft

```bash
lease-agreement-drafter audit --env sandbox --draft-id lease_8f4a2c1b9e01 --input draft.md
```

### Print schema

```bash
lease-agreement-drafter schema --env sandbox
```

### Print error catalog

```bash
lease-agreement-drafter error-catalog --env sandbox
```

## Error table

| Code | Severity | Trigger | Fix |
| --- | --- | --- | --- |
| `MISSING_PARTY_NAME` | error | Landlord or tenant name is empty | Add exact legal name |
| `MISSING_PROPERTY_ADDRESS` | error | Premises address is empty | Add street, number, city, and registry details if available |
| `INVALID_DATE_RANGE` | error | End date is not after start date | Correct the term dates |
| `MISSING_RENT` | error | Monthly rent is zero or negative | Add positive rent amount in ₪ |
| `RESIDENTIAL_DEPOSIT_CAP` | warning | Apartment security exceeds common residential cap | Reduce security or obtain legal review |
| `VAT_ON_APARTMENT` | warning | VAT marked on apartment lease | Residential rental up to 25 years is generally VAT-exempt; confirm any exception |
| `OFFICE_WITHOUT_USE` | warning | Office permitted use is missing | Define business activity |
| `NO_REPAIR_CLAUSE` | warning | Template lacks repair language | Add urgent and ordinary defect handling |
| `NO_HANDOVER_PROTOCOL` | warning | Template lacks delivery protocol | Add meter, key, photo, and inventory protocol |
| `NO_EARLY_TERMINATION_BALANCE` | warning | Template lacks balanced early termination | Add mutual or cause-based termination language |

## Israeli legal reference points

| Topic | Reference point | Drafting relevance |
| --- | --- | --- |
| General lease law | Lease and Loan Law, 5731-1971 | Basic lease obligations and remedies |
| Residential amendments | Lease and Loan Law amendments commonly known as Fair Rent Law amendments | Fit-for-residence, repairs, security limits, and mandatory terms for covered apartments |
| Contracts | Contracts Law General Part, 5733-1973 and Contracts Remedies Law, 5731-1970 | Formation, good faith, breach, remedies, damages |
| Real estate | Land Law, 5729-1969 | Rights in land, registry details, common property context |
| Protected tenancy | Tenant Protection Law consolidated version, 5732-1972 | Avoid accidental protected tenancy treatment |
| Tax | Value Added Tax Law, 5736-1975 and Israel Tax Authority guidance | Office lease VAT and invoice treatment |
| Municipal charges | Municipal bylaws and arnona notices | Allocation of arnona, signage, and local fees |
| Accessibility | Equal Rights for Persons with Disabilities Law and accessibility regulations | Office access and public reception implications |
| Business licensing | Business Licensing Law, 5728-1968 | Tenant use, permits, signage, and operating restrictions |
| Consumer context | Standard Contracts Law and consumer protection principles where relevant | Review one-sided landlord forms used with consumers |

## Official-source verification checklist

1. Check the current consolidated statute text on the official legislation database or another authoritative legal database.
2. Check current Israel Tax Authority guidance before deciding VAT language.
3. Check the municipality for arnona classification, signage, and local licensing constraints.
4. Check the land registry or ownership documentation when authority to lease is uncertain.
5. Check building bylaws and house committee rules for residential use, pets, parking, storage, and renovations.

## Request validation rules

| Field | Rule |
| --- | --- |
| `property.property_type` | Must be `apartment` or `office` |
| `terms.start_date` | Accepts DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD; stores DD/MM/YYYY |
| `terms.end_date` | Must be after start date |
| `terms.monthly_rent_ils` | Must be positive |
| `terms.security_deposit_ils` | Checked against the common residential cap when coverage likely applies |
| `terms.vat_applies` | Warning when used for apartment leases |
| `property.permitted_use` | Warning when missing for office leases |

## Non-goals

Do not use this package for eviction proceedings, protected tenancy creation or waiver, tax opinions, planning approvals, engineering defects, or final legal advice. Use it to prepare structured drafts and issue lists for professional review.
