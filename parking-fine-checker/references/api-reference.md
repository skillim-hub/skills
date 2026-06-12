# API and Regulation Reference

This reference describes official-source categories, legal anchors, request/response models, and safe integration patterns for Israeli parking, traffic, and toll fine workflows. Many Israeli issuers use official web forms rather than public JSON APIs. When no public API exists, treat the official web form, downloadable receipt, official payment voucher, or written issuer confirmation as the authoritative interface.

Do not bypass authentication, CAPTCHA, rate limits, robots controls, or terms of use. Integrate only with published APIs, written issuer permission, or internal middleware operated with authority.

## Source-of-truth hierarchy

1. Official issuer portal or official government payment service.
2. Official downloadable receipt, payment voucher, or appeal confirmation.
3. Written confirmation from issuer or toll operator.
4. Collection agent statement verified against the original issuer.
5. Internal spreadsheet or employee message.

Only the first three should close a case without additional verification.

## Israeli legal and regulatory anchors

Verify current wording before using these anchors in a legal dispute.

| Area | Anchor | Relevance |
|---|---|---|
| Municipal enforcement | Municipal bylaws and local-authority powers | Parking restrictions, resident permits, signs, local fine procedures. |
| Traffic enforcement | Traffic Ordinance and Traffic Regulations | Police traffic tickets, points, summons, driver and vehicle rules. |
| Administrative fines | Administrative offense frameworks where applicable | Payment, contest, and hearing paths for certain fines. |
| Collection | Municipal collection procedures and collection law mechanisms | Escalation, linkage, interest, collection costs, enforcement. |
| Privacy | Protection of Privacy Law, 5741-1981 and security obligations | ID numbers, vehicle records, driver logs, photos, receipts. |
| Payments | Payment services and card-processing rules | Failed payments, refunds, receipts, duplicate charges. |
| Toll roads | Road-specific toll legislation/concession arrangements | Road 6, tunnels, fast-lane charges, subscriptions, owner liability. |
| Labor/payroll | Wage protection and employment principles | Employee reimbursement or salary deduction. |
| Tax/accounting | Income tax, VAT, and bookkeeping rules | Deductibility, documentation, reimbursement, vehicle expenses. |
| Evidence | Evidence rules and court procedure | Photos, timestamps, envelopes, portal screenshots, metadata. |

## Municipal lookup model

Example request:

```json
{
  "issuer_type": "municipality",
  "issuer_name": "Example Municipality",
  "vehicle_number": "1234567",
  "notice_number": "987654321",
  "recipient_identifier": "*****1234"
}
```

Example response:

```json
{
  "status": "verified_unpaid",
  "amount_ils": "250.00",
  "currency": "ILS",
  "notice_date": "2026-03-10",
  "due_date": "2026-06-08",
  "location": "Example Street 10",
  "payment_allowed": true,
  "appeal_allowed": true
}
```

## Police/state fine model

Example request:

```json
{
  "issuer_type": "police",
  "notice_number": "30201234567",
  "vehicle_number": "1234567",
  "recipient_identifier": "*****1234"
}
```

Example response:

```json
{
  "status": "verified_unpaid",
  "amount_ils": "500.00",
  "due_date": "2026-06-01",
  "points_possible": true,
  "court_option": true,
  "payment_allowed": true
}
```

Escalate when points, summons, court date, accident, injury, license risk, or driver identity dispute appears.

## Road 6 and toll operator model

Example request:

```json
{
  "issuer_type": "toll",
  "operator": "Road 6",
  "vehicle_number": "1234567",
  "account_number": "optional",
  "notice_number": "optional"
}
```

Example response:

```json
{
  "status": "verified_unpaid",
  "principal_toll_ils": "42.80",
  "enforcement_fee_ils": "65.00",
  "collection_fee_ils": "0.00",
  "total_amount_ils": "107.80",
  "trips": [
    {"date": "2026-02-11", "entry": "Interchange A", "exit": "Interchange B", "amount_ils": "21.40"}
  ],
  "payment_allowed": true
}
```

## Collection-stage model

Example:

```json
{
  "collection_agent": "Example Collection Office",
  "original_issuer": "Example Municipality",
  "original_notice_number": "1234567890",
  "vehicle_number": "1234567",
  "principal_amount_ils": "250.00",
  "linkage_interest_ils": "18.40",
  "collection_costs_ils": "75.00",
  "total_amount_ils": "343.40"
}
```

Block payment until original issuer, original notice, amount breakdown, and closure effect are verified.

## Authorized HTTP examples

### Lookup

```http
POST /fines/lookup HTTP/1.1
Content-Type: application/json
Authorization: Bearer <token>
Idempotency-Key: lookup-case-001

{
  "issuer_type": "municipality",
  "issuer_name": "Example Municipality",
  "vehicle_number": "1234567",
  "notice_number": "987654321"
}
```

Success:

```json
{
  "case_id": "issuer-987654321",
  "status": "verified_unpaid",
  "amount_ils": "250.00",
  "due_date": "2026-06-08",
  "payment_allowed": true,
  "appeal_allowed": true
}
```

### Payment preparation

```http
POST /fines/payment-intents HTTP/1.1
Content-Type: application/json
Authorization: Bearer <token>
Idempotency-Key: payprep-case-001

{
  "case_id": "issuer-987654321",
  "amount_ils": "250.00",
  "return_url": "https://business.example/fines/callback"
}
```

Response:

```json
{
  "payment_intent_id": "pi_123",
  "official_payment_url": "https://issuer.example/pay/pi_123",
  "expires_at": "2026-05-14T14:00:00+03:00"
}
```

### Appeal submission

```json
{
  "case_id": "issuer-987654321",
  "appeal_type": "cancellation",
  "grounds": "Paid parking app session covered the exact enforcement time.",
  "evidence": [
    {"type": "parking_app_receipt", "file_name": "receipt.pdf", "sha256": "..."}
  ]
}
```

Response:

```json
{
  "appeal_reference": "APL-2026-0001",
  "status": "appeal_submitted",
  "submitted_at": "2026-05-14T11:22:00+03:00"
}
```

## Error table

| Code | HTTP | Meaning | Retry | Action |
|---|---:|---|---|---|
| `VALIDATION_ERROR` | 400 | Missing or malformed field | No | Fix request. |
| `UNAUTHORIZED` | 401 | Invalid credentials | No | Refresh token. |
| `FORBIDDEN` | 403 | Not allowed | No | Confirm authority. |
| `FINE_NOT_FOUND` | 404 | No matching fine | No | Retry identifiers, contact issuer. |
| `CONFLICTING_STATUS` | 409 | Local and official status differ | No | Reconcile. |
| `DUPLICATE_PAYMENT_RISK` | 409 | Possible previous payment | No | Verify receipt. |
| `RATE_LIMITED` | 429 | Too many requests | Yes | Back off. |
| `PORTAL_UNAVAILABLE` | 503 | Issuer unavailable | Yes | Retry and document outage. |
| `PAYMENT_PROVIDER_ERROR` | 502 | Payment provider failed | Maybe | Check settlement before retry. |
| `COLLECTION_BREAKDOWN_REQUIRED` | 422 | Missing itemization | No | Request breakdown. |
| `LEGAL_ESCALATION_REQUIRED` | 422 | Points/court/summons risk | No | Escalate. |

## Field rules

| Field | Rule |
|---|---|
| `vehicle_number` | Strip spaces and hyphens; accept 5-8 digits. |
| `notice_number` | Trim, preserve letters and digits. |
| `amount_ils` | Decimal string with two digits. |
| `notice_date` | ISO internally; Hebrew display may use `DD/MM/YYYY`. |
| `issuer_type` | `municipality`, `police`, `toll`, `collection`, `other`. |
| `status` | Use canonical statuses from `SKILL.md`. |

## Non-API workflow

1. Open the official portal manually.
2. Enter the minimum required identifiers.
3. Save the result as PDF or screenshot.
4. Record status, amount, due date, and URL domain.
5. Download receipt or confirmation.
6. Archive evidence in the case folder.



## Case creation and chained lookup

Create a local or middleware case first, then pass the returned `case_id` into lookup, payment preparation, or appeal submission.

```http
POST /fines/cases HTTP/1.1
Content-Type: application/json
Authorization: Bearer <token>

{
  "issuer_type": "municipality",
  "issuer_name": "Example Municipality",
  "vehicle_number": "1234567",
  "notice_number": "1001",
  "amount_ils": "250.00",
  "notice_date": "2026-03-10",
  "due_date": "2026-06-08"
}
```

Response:

```json
{
  "case_id": "20260602-1234567-1001-1a2b3c4d",
  "issuer_type": "municipality",
  "issuer_name": "Example Municipality",
  "vehicle_number": "1234567",
  "notice_number": "1001",
  "status": "new",
  "amount_ils": "250.00"
}
```

Use the returned value in the next request:

```json
{
  "case_id": "20260602-1234567-1001-1a2b3c4d",
  "issuer_type": "municipality",
  "vehicle_number": "1234567",
  "notice_number": "1001"
}
```


## Public API and webhook validation

The package does not claim that Israeli municipalities, Israel Police, Road 6, Carmel Tunnels, or Fast Lane publish a single public JSON API for fine lookup and payment. The current official sources checked on 2026-06-02 expose official portals, web forms, payment systems, call centers, and account areas.

The endpoint paths used in this reference, such as `/fines/lookup`, `/fines/payment-intents`, and `/fines/appeals`, are example paths for authorized internal middleware. Do not label them as official issuer endpoints unless the issuer or operator gives written integration documentation.

No official public webhook event names were confirmed for parking, traffic, or toll fine workflows. Use internal event names only inside controlled business systems, for example:

```json
{
  "event": "fine.lookup.completed",
  "case_id": "20260602-1234567-1001-1a2b3c4d",
  "status": "verified_unpaid"
}
```

Internal event names must not be represented as official Israeli government, municipal, or toll-road webhook names.
