# API and Regulation Reference

Use this reference to connect the package to an approved Israeli land-registry data source, internal adapter, or official portal workflow. Keep endpoint URLs configurable because service authentication, payment, routing, and output formats can change.

## Scope

The package supports this adapter model:

- `GET /tabu/parcel` for block, parcel, and optional subparcel lookup.
- `GET /tabu/address` for address-to-property lookup.
- `POST /tabu/extract-orders` for workflows that require payment, session handling, or document ordering.
- `GET /tabu/extract-orders/{order_id}` for status checks.
- Local fixture transport for testing and offline demonstrations.

The package does not assume that a single unauthenticated JSON endpoint exists for all official Tabu data. Web validation on 04/06/2026 did not confirm an official public Tabu JSON API host, official endpoint paths, or official webhook event names. Treat `/tabu/parcel`, `/tabu/address`, and `/tabu/extract-orders` as internal adapter examples only.

## Israeli sources and legal anchors to verify

Verify the current wording and operational details on official sources before production deployment.

| Area | Israeli source or regulation | Practical relevance |
|---|---|---|
| Land Registry services | Ministry of Justice, Land Registration and Settlement of Rights Department | Official Tabu extracts, ownership records, caveats, mortgages, liens, deeds |
| Government service portal | Government of Israel services portal | Online ordering, payment, identity verification, service routing |
| Government data catalog | Israel government data and API catalog where available | Endpoint discovery, open datasets, service metadata |
| Land Law | Land Law, 5729-1969 | Property rights framework and registration principles |
| Land registration regulations | Land Regulations, Management and Registration, 5772-2011 | Registry procedures, extracts, registration, deeds |
| Planning data | Planning Administration and municipal planning portals | Planning and zoning context; not a substitute for ownership registration |
| Israel Land Authority | Israel Land Authority | State land, leaseholds, non-Tabu arrangements, approvals |
| Housing company records | Housing company or project registration records | Properties not fully registered in Tabu |
| Privacy | Protection of Privacy Law, 5741-1981 and related regulations | Handling names, IDs, addresses, and raw extracts |
| Electronic records | Electronic Signature Law, 5761-2001 and official e-government requirements | Digital ordering, signed documents, audit trail |
| Consumer and real-estate transactions | Sale Law (Apartments), 5733-1973 and related consumer protections | Purchase due diligence and disclosures |
| Companies | Companies Registrar and Companies Law, 5759-1999 | Corporate owners, charges, and signatory authority |
| Mortgages and charges | Banking and pledge or corporate charge registries where applicable | Cross-checking mortgages, charges, and collateral |

## Data model

### Parcel identifier

```json
{
  "block": 30001,
  "parcel": 12,
  "subparcel": 4
}
```

| Field | Required | Type | Validation |
|---|---:|---|---|
| `block` | Yes | integer | 1 to 999999 |
| `parcel` | Yes | integer | 1 to 999999 |
| `subparcel` | No | integer or null | 1 to 999999 if supplied |

### Extract order

```json
{
  "order_id": "ORD-SANDBOX-0001",
  "status": "created",
  "created_at": "2026-06-04T12:00:00Z",
  "property": {
    "block": 30001,
    "parcel": 12,
    "subparcel": 4
  },
  "payment_reference": "PAY-SANDBOX-0001"
}
```

### Normalized extract

```json
{
  "property_id": {
    "block": 30001,
    "parcel": 12,
    "subparcel": 4
  },
  "address": "Example Street 10, Tel Aviv-Yafo",
  "retrieved_at": "2026-06-04T12:00:00Z",
  "rights": [
    {
      "owner_name": "Dana Cohen",
      "id_masked": "******782",
      "right_type": "ownership",
      "share": "1/2",
      "deed_date": "15/02/2022",
      "encumbrances": []
    }
  ],
  "warnings": [],
  "raw": {}
}
```

## Web-validated endpoint and webhook note

No official public Tabu JSON API host, official JSON endpoint path, or official webhook event name was confirmed in the 04/06/2026 two-pass validation. Keep all endpoint paths, hosts, callbacks, and event names configurable. Do not label adapter paths as official government endpoints unless a current official source explicitly confirms them.

## Request examples

### Parcel lookup

```http
GET /tabu/parcel?block=30001&parcel=12&subparcel=4 HTTP/1.1
Host: sandbox.example.internal.gov-adapter.local
Accept: application/json
Authorization: Bearer <token>
X-Request-Id: 4c8b8055-8e12-4a75-9bd8-6a0d9e7d7e71
```

### Address lookup

```http
GET /tabu/address?city=Tel%20Aviv-Yafo&street=Example%20Street&house=10 HTTP/1.1
Host: sandbox.example.internal.gov-adapter.local
Accept: application/json
Authorization: Bearer <token>
```

### Create extract order

```http
POST /tabu/extract-orders HTTP/1.1
Host: sandbox.example.internal.gov-adapter.local
Content-Type: application/json
Authorization: Bearer <token>
Idempotency-Key: 9e10d1f7-76c7-4d8a-9c9b-6af0e1a6f6c8

{
  "property_id": {
    "block": 30001,
    "parcel": 12,
    "subparcel": 4
  },
  "language": "he",
  "purpose": "purchase_due_diligence",
  "payment_reference": "PAY-SANDBOX-0001"
}
```

### Read order status

```http
GET /tabu/extract-orders/ORD-SANDBOX-0001 HTTP/1.1
Host: sandbox.example.internal.gov-adapter.local
Accept: application/json
Authorization: Bearer <token>
```

## Error table

| HTTP/status | Code | Meaning | Action |
|---:|---|---|---|
| 400 | `VALIDATION_ERROR` | Invalid block, parcel, subparcel, address, or date | Correct the request before retrying |
| 401 | `UNAUTHORIZED` | Missing or invalid token, or expired session | Refresh credentials |
| 402 | `PAYMENT_REQUIRED` | Extract order requires fee payment | Complete payment once; do not blind-retry |
| 403 | `FORBIDDEN` | User lacks permission or service is restricted | Confirm entitlement and legal basis |
| 404 | `NOT_FOUND` | No record found for identifier | Verify block/parcel mapping and registry type |
| 409 | `CONFLICT` | Payment, session, or order already exists | Use idempotency key and retrieve existing order |
| 422 | `AMBIGUOUS_ADDRESS` | Address maps to multiple parcels | Request apartment, entrance, municipal bill, or seller documents |
| 429 | `RATE_LIMITED` | Too many requests | Back off and retry later |
| 500 | `UPSTREAM_ERROR` | Official or internal gateway error | Retry with backoff and preserve correlation ID |
| 503 | `SERVICE_UNAVAILABLE` | Portal or API unavailable | Retry later; use manual workflow if urgent |

## Field mapping

| Normalized field | Common English key | Common Hebrew key |
|---|---|---|
| `block` | `block`, `gush` | `גוש` |
| `parcel` | `parcel`, `helka` | `חלקה` |
| `subparcel` | `subparcel`, `tat_helka` | `תת חלקה`, `תת-חלקה` |
| `address` | `address` | `כתובת` |
| `rights` | `rights`, `owners`, `holders` | `בעלי זכויות`, `זכויות`, `בעלויות` |
| `owner_name` | `owner_name`, `name`, `holder_name` | `שם`, `שם בעל זכות` |
| `id` | `id`, `identifier`, `identity_number` | `תעודת זהות`, `מספר מזהה`, `ח.פ.` |
| `right_type` | `right_type`, `type` | `סוג זכות` |
| `share` | `share`, `fraction` | `חלק`, `חלק יחסי` |
| `encumbrances` | `encumbrances`, `restrictions` | `שעבודים`, `מגבלות`, `הערות` |
| `warnings` | `warnings`, `risk_flags` | `אזהרות`, `דגלי סיכון` |

## Security and privacy controls

- Minimize personal data.
- Mask Israeli ID numbers in summaries.
- Store raw extracts only where there is a business need.
- Encrypt files at rest.
- Log only normalized property identifiers and request IDs.
- Do not send extracts to third parties without a lawful basis.
- Separate official facts from legal interpretation.
- Keep audit metadata: retrieval time, input identifier, gateway endpoint, response hash, and operator.

## Idempotency guidance

Use idempotency keys for paid or asynchronous order workflows.

Retry policy:

| Operation | Retry? | Notes |
|---|---:|---|
| `GET /tabu/parcel` | Yes | Retry transient 429/500/503 with exponential backoff |
| `GET /tabu/address` | Yes | Retry transient errors; do not treat ambiguous result as failure |
| `POST /tabu/extract-orders` | Carefully | Use idempotency key; never duplicate payment intentionally |
| Payment redirect or callback | No blind retry | Reconcile by order ID and payment reference |
| Document download | Yes | Retry with checksum validation |
