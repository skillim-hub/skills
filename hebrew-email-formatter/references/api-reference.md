# Reference: Schemas, Validation Codes, and Israeli Context

This formatter does not call official systems and does not send email. It accepts structured facts and returns a reviewable Hebrew draft. Use this reference for integration contracts, warning codes, and Israeli terminology.

## Israeli context references

| Area | Why it matters | Reference target |
|---|---|---|
| VAT and invoices | Price wording, `כולל מע"מ`, `לא כולל מע"מ`, `חשבונית מס`, `חשבונית מס/קבלה` | Israel Tax Authority public guidance |
| Bookkeeping records | Invoice, receipt, and payment documentation wording | Israel Tax Authority public guidance |
| Consumer protection | Complaints, cancellation requests, refunds, and written responses | Consumer Protection and Fair Trade Authority public guidance |
| Privacy | Data minimization in email drafts | Privacy Protection Authority public guidance |
| Marketing consent | Keep transactional email separate from promotional content unless consent is reviewed | Israeli communications law resources |
| Business identifiers | Correct use of `ח.פ.`, `ח.צ.`, `עוסק מורשה`, `עוסק פטור`, `עמותה` | Tax and corporations public guidance |
| Currency | Use `₪` in Israeli-facing correspondence | Bank of Israel currency information |

Verify current law, tax rates, thresholds, official forms, and Tax Authority API instructions before relying on regulatory wording.


## Web-validated current values

Access date: 2026-06-03

| Item | Verified value | Drafting implication |
|---|---|---|
| VAT rate | 18% from 01/01/2025, still used as the current standard rate in the 2026 cross-check | Keep `בתוספת מע"מ כדין` and use 18% only for helper calculations; do not give tax advice |
| Israel Invoices threshold | As of 03/06/2026, allocation-number relevance begins above 5,000 ₪ before VAT | Mention only as contextual review note; official systems must handle allocation requests |
| Exempt dealer ceiling | 2026 public guidance mentions about 122,833 ₪ | Do not infer whether a sender is `עוסק פטור` or `עוסק מורשה` |
| Official APIs | Tax Authority API services exist, but this package does not call endpoints | Keep endpoint paths, hosts, authentication, and webhook event names out of formatter logic |


## Request schema

```json
{
  "purpose": "payment_reminder",
  "formality": "neutral",
  "environment": "sandbox",
  "recipient": {
    "name": "דנה כהן",
    "gender": "female",
    "organization": "כהן אדריכלים",
    "is_company": false
  },
  "sender": {
    "name": "יואב לוי",
    "gender": "male",
    "business_name": "יואב לוי סטודיו",
    "role": "מעצב מוצר",
    "phone": "050-1234567",
    "email": "yoav@example.co.il",
    "business_id": "עוסק מורשה 123456789",
    "website": "https://example.co.il"
  },
  "facts": {
    "invoice_number": "2026-041",
    "invoice_date": "01/05/2026",
    "due_date": "31/05/2026",
    "amount": "3500",
    "vat_status": "לא כולל מע\"מ",
    "payment_terms": "שוטף + 30",
    "requested_action_date": "06/06/2026"
  },
  "signature_style": "business"
}
```

## Response schema

```json
{
  "id": "hef_1234567890abcdef",
  "subject": "תזכורת לתשלום חשבונית 2026-041",
  "body": "שלום דנה כהן,\n\nרציתי לוודא שחשבונית 2026-041 מיום 01/05/2026 התקבלה אצלכם.\n\nסכום לתשלום: 3,500 ₪\nתאריך פירעון: 31/05/2026\nתנאי תשלום: שוטף + 30\n\nאשמח לקבל עדכון לגבי מועד התשלום הצפוי.\n\nתודה,\nיואב לוי",
  "warnings": [],
  "metadata": {
    "locale": "he-IL",
    "currency": "ILS",
    "date_format": "DD/MM/YYYY",
    "formality": "neutral",
    "purpose": "payment_reminder",
    "environment": "sandbox"
  }
}
```

## CLI request examples

### Create a saved draft and reuse the returned identifier

```bash
CREATE_RESPONSE=$(hebrew-email-formatter create \
  --purpose payment_reminder \
  --recipient "דנה כהן" \
  --recipient-gender female \
  --sender "יואב לוי" \
  --sender-gender male \
  --amount 3500 \
  --invoice-number 2026-041 \
  --invoice-date 01/05/2026 \
  --due-date 31/05/2026 \
  --payment-terms "שוטף + 30" \
  --env sandbox \
  --json)

DRAFT_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")

hebrew-email-formatter show "$DRAFT_ID"
```

### Format amount and date

```bash
hebrew-email-formatter amount 12345.5 --agorot
hebrew-email-formatter date 2026-06-03
```

## Error and warning table

| Code | Severity | Trigger | Resolution |
|---|---|---|---|
| `HEF001_MISSING_PURPOSE` | error | No purpose is provided | Provide a supported purpose |
| `HEF002_MISSING_RECIPIENT` | warning | Recipient name is missing | Use a general greeting or add recipient name |
| `HEF003_MISSING_SENDER` | warning | Sender name is missing | Add sender name before sending |
| `HEF004_INVALID_DATE` | error | Date cannot be parsed | Use `DD/MM/YYYY`, `DD-MM-YYYY`, or `YYYY-MM-DD` |
| `HEF005_INVALID_AMOUNT` | error | Amount is not numeric | Use a decimal-compatible value |
| `HEF006_VAT_STATUS_UNKNOWN` | warning | Price is quoted without VAT status | Add `כולל מע"מ`, `לא כולל מע"מ`, or `בתוספת מע"מ כדין` |
| `HEF007_INVOICE_MISSING_DUE_DATE` | warning | Payment reminder lacks due date | Add due date or terms |
| `HEF008_GENDER_UNKNOWN` | info | Recipient gender is unknown | Use neutral phrasing |
| `HEF009_LEGAL_REVIEW` | warning | Legal escalation is requested | Use approved wording after review |
| `HEF010_PRIVACY_MINIMIZATION` | warning | Sensitive personal data appears | Remove unnecessary data |
| `HEF011_MARKETING_CONSENT` | warning | Transactional email includes promotion | Separate promotional content or review consent |
| `HEF012_ATTACHMENT_UNCONFIRMED` | warning | Draft mentions an attachment not confirmed | Attach the file or remove the claim |
| `HEF013_AMBIGUOUS_DOCUMENT_TYPE` | warning | Document type is unclear | Use exact document type or a placeholder |
| `HEF014_OVERDUE_FIRMNESS` | info | Delay is long | Consider firm factual wording |
| `HEF015_UNSUPPORTED_PURPOSE` | error | Purpose is not recognized | Choose a supported purpose |

## Data handling guidance

- Store only the draft and minimal metadata needed for review.
- Avoid logging full identification numbers, payment-card details, medical details, or private addresses.
- Prefer placeholders for bank details.
- Treat attachments outside the formatter unless a secure integration handles them.
- Keep promotional content separate from transactional messages unless consent has been reviewed.
