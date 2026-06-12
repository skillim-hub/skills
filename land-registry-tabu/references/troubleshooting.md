# Troubleshooting Guide

Use this guide when lookup, parsing, payment, address matching, or report generation fails.

## Fast triage

| Symptom | Likely cause | First action |
|---|---|---|
| Validation error before request | Invalid block, parcel, or subparcel | Normalize and re-enter numeric values |
| No record found | Wrong parcel, unregistered property, different registry | Verify source documents and registry type |
| Multiple address matches | Address is ambiguous | Request apartment, entrance, municipal bill, or previous extract |
| Unauthorized | Token or session expired | Refresh credentials |
| Payment required | Official extract requires fee | Complete payment through approved flow |
| Duplicate charge risk | Repeated order request | Use idempotency key and reconcile order status |
| Hebrew fields missing | Response uses different labels | Update field mapping |
| Owner missing | Response contains PDF, scanned data, or unusual structure | Preserve raw response and use manual review |
| Mortgage not parsed | Encumbrance appears under alternate key | Inspect raw encumbrance fields and Hebrew labels |
| CLI cannot import package | Package was not installed | Run `pip install -e .` from the package root |

## Input validation failures

### Block or parcel rejected

Check for:

- Leading words such as `גוש` or `חלקה`.
- Slash-delimited input not parsed before validation.
- Zero or negative numbers.
- Non-numeric apartment numbers used as subparcel.
- Copy and paste punctuation from PDF.

Fix:

```bash
land-registry-tabu --mock-file scripts/fixtures/sample_parcel_response.json parcel --block 30001 --parcel 12 --subparcel 4
```

### Israeli ID validation fails

The client validates the standard checksum for 9-digit Israeli personal IDs. Company numbers and foreign IDs may not pass that validation. Use ID validation only for personal ID numbers when appropriate.

## Lookup failures

### No record found

Possible reasons:

- Mistyped block or parcel.
- Property is registered under a different subparcel.
- Building is not registered as a condominium.
- Rights are held through Israel Land Authority, housing company, cooperative society, or another registry.
- Address-to-parcel mapping is wrong.
- Official service is unavailable or data is restricted.

Recommended response:

```text
No registry record was found for the supplied identifier. Verify the property identifier against a municipal bill, contract, previous extract, or official source before drawing conclusions.
```

### Multiple address matches

Do not select the first result automatically. Request:

- Entrance.
- Apartment or unit number.
- Floor.
- Municipal account details.
- Previous Tabu extract.
- Seller or landlord documents.
- Condominium order or plan.

## Authentication and payment failures

### 401 Unauthorized

Check:

- API key environment variable.
- Token expiry.
- User entitlement.
- Clock skew.
- Gateway configuration.

### 402 Payment required

Check:

- Fee status.
- Payment reference.
- Callback URL.
- Order ID.
- Idempotency key.

Never retry a paid order without reconciling the payment or order status.

### 403 Forbidden

Check whether:

- The service requires a different user role.
- The operation is not available through the configured gateway.
- The request violates an access policy.
- A document is restricted.

## Parsing failures

### Rights list is empty but raw payload contains owners

Update field mapping. Common alternatives:

- `rights`
- `owners`
- `holders`
- `בעלי זכויות`
- `זכויות`
- `בעלויות`

### Encumbrances are missed

Search the raw payload for:

- `mortgage`
- `lien`
- `attachment`
- `caveat`
- `easement`
- `משכנתה`
- `שעבוד`
- `עיקול`
- `הערת אזהרה`
- `זיקת הנאה`

### Dates fail validation

Expected display format for Hebrew-facing reports is `DD/MM/YYYY`. Some upstream services may return ISO dates. Normalize before generating reports.

## Report-quality failures

### Report sounds too certain

Replace legal conclusions with factual statements and review triggers.

Use:

```text
The retrieved extract lists a mortgage. Obtain a release or consent document before transfer.
```

Avoid:

```text
The property cannot be sold.
```

### Personal data appears in report

Mask ID numbers:

```text
123456782 -> ******782
```

Do not include full IDs unless there is a lawful, necessary, and documented reason.

## Safe retry policy

| Error | Retry | Guidance |
|---|---:|---|
| Local validation | No | Fix input |
| 401/403 | No | Fix credentials or permission |
| 402 | No blind retry | Reconcile payment |
| 404 | No | Verify identifier |
| 409 | No blind retry | Retrieve existing order |
| 422 | No | Resolve ambiguity |
| 429 | Yes | Backoff |
| 500/503 | Yes | Backoff and preserve request ID |
| Timeout | Yes | Retry idempotent reads only |

## Manual fallback

Use manual fallback when:

- The property is not registered in ordinary Tabu.
- The service returns a PDF or scanned document.
- The record uses historical deed references.
- Multiple registries may apply.
- A high-value transaction depends on interpretation.
- An attachment, caveat, or lien appears.

Manual fallback pack:

1. Raw extract.
2. Normalized property ID.
3. Address and source documents.
4. Counterparty identity.
5. Encumbrance list.
6. Questions for professional review.
