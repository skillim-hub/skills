# API and Regulatory Reference

## Reference status

Treat prescription renewal in Israel as a human-in-the-loop workflow unless a provider grants documented API access under a contract. Do not infer endpoints from browser traffic. Do not automate consumer portals without permission.

The references below describe categories that must be checked against current official sources before production use.

## Regulatory and service categories

| Category | Relevance | Control |
|---|---|---|
| Ministry of Health | Pharmacy rules, patient rights, digital health policy | Verify current official guidance |
| Kupot Cholim | Prescription lists, doctor messaging, renewals, digital prescriptions | Use official portal, app, phone, clinic, or contracted API |
| Licensed pharmacies | Dispensing, stock, pickup, delivery, pharmacist consultation | Confirm branch and delivery terms |
| Privacy regulation | Health data, consent, minimization, data security | Collect minimum data and restrict access |
| Consumer transaction terms | Price, delivery, substitution, refunds | Confirm total price in ₪ before payment |
| Employment privacy | Employee support and medical confidentiality | Handle logistics only unless a lawful basis exists |

## Non-public API position

No public consumer API is assumed for:
- Clalit prescription renewal.
- Maccabi prescription renewal.
- Meuhedet prescription renewal.
- Leumit prescription renewal.
- Super-Pharm prescription fulfillment.
- Be prescription fulfillment.
- Newpharm prescription fulfillment.

Use provider-approved API documentation only when formally available.

## Internal workflow API example

The following examples are for a private internal workflow service. They are not provider endpoints.

### Create case

Request:

```json
{
  "kupat_cholim": "Maccabi",
  "medication_name": "as shown in portal",
  "strength_form": "10 mg tablets",
  "supply_days": 5,
  "repeats_left": 0,
  "valid_until": "22-06-2026",
  "preferred_fulfillment": "delivery",
  "pharmacy": "Super-Pharm",
  "consent_confirmed": true
}
```

Response:

```json
{
  "case_id": "RX-20260604-0001",
  "urgency": "soon",
  "recommended_path": "doctor_renewal",
  "next_actions": [
    "Submit a doctor or clinic renewal request",
    "Confirm pharmacy stock after renewal",
    "Record confirmation and follow-up date"
  ]
}
```

### Generate message

Request:

```json
{
  "case_id": "RX-20260604-0001",
  "language": "he",
  "recipient_type": "doctor"
}
```

Response:

```json
{
  "subject": "בקשה לחידוש מרשם",
  "body": "שלום... תודה.",
  "redactions": ["diagnosis", "full_id_number", "password", "otp"]
}
```

### Redact text

Request:

```json
{
  "text": "ID 123456789 phone 050-1234567",
  "mask_id": true,
  "mask_phone": true
}
```

Response:

```json
{
  "redacted_text": "ID ********* phone 050-***4567",
  "redacted_fields": ["israeli_id", "phone"]
}
```

## Error table

| Code | Meaning | Action |
|---|---|---|
| `CONSENT_MISSING` | Another adult is involved without consent | Stop and obtain official authority |
| `PORTAL_CREDENTIAL_REQUESTED` | Password or one-time code was supplied | Remove it and let the user log in directly |
| `NO_ACTIVE_PRESCRIPTION` | Prescription is not active | Prepare doctor or clinic request |
| `NO_REPEATS_LEFT` | Repeat count is zero | Request renewal |
| `VALIDITY_EXPIRED` | Prescription date expired | Request reissue or renewal |
| `SUPPLY_CRITICAL` | 0-2 days remain | Use urgent channel |
| `DELIVERY_UNAVAILABLE` | Pharmacy cannot deliver | Try pickup or another licensed pharmacy |
| `COLD_CHAIN_UNCONFIRMED` | Refrigeration handling is unknown | Do not proceed until confirmed |
| `CONTROLLED_MEDICATION` | Special handling may apply | Use official pharmacy and HMO rules |
| `PRICE_MISMATCH` | Cost differs from expectation | Confirm itemized price in ₪ |
| `PROFILE_MISMATCH` | Wrong family member selected | Stop and switch profile |
| `SYNC_DELAY` | Portal and pharmacy data differ | Wait briefly, then contact support |

## Security requirements

- Use official authentication only.
- Never store portal passwords or one-time codes.
- Encrypt workflow storage that contains health data.
- Restrict staff access.
- Keep audit logs with minimal medical detail.
- Require manual review before outbound messages.
- Disable automated submission by default.
- Provide deletion and redaction tools.


## Web-validated operational notes, 2026

| Topic | Verified status | Package rule |
|---|---|---|
| VAT | General Israeli VAT rate verified as 18% in 2026 | Store receipt totals in ₪; do not auto-calculate VAT |
| Maccabi Pharm | Digital prescription must have at least 72 hours validity for online order | Warn users to verify validity before ordering |
| Maccabi delivery fees | Public page listed ₪35 base delivery and ₪17.50 for a benefit tier | Treat as changeable provider fee |
| Meuhedet delivery | Public page listed ₪14.90 delivery | Treat as changeable provider fee |
| Leumit delivery | Public page listed ₪15 delivery and Sunday-Thursday delivery | Treat as changeable provider fee |
| Super-Pharm | Digital-prescription order flow verified for selected Kupot Cholim | Verify HMO eligibility, address, payment, and restrictions |
| Super-Pharm restricted medicines | Delivery terms and FAQ exclude dangerous/psychotropic categories | Keep controlled-medication escalation |
| Be | Current official prescription-delivery support not confirmed | Verify in app/branch before use |
| Newpharm | Current Israeli prescription-delivery support not confirmed | Treat as legacy/local and verify licensed pharmacy |
| Public APIs/webhooks | No public renewal endpoints or event names confirmed | Keep non-API, human-in-the-loop design |
