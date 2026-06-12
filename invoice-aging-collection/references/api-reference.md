# API, Regulation, and Integration Reference

This reference lists the Israeli legal/regulatory sources and integration surfaces relevant to invoice aging and collection reminders. Verify live URLs, rates, thresholds, and forms before production use because government services and statutory figures change.

## Verified 2026 figures and boundaries

The following figures were validated during the final web-validation pass on 02/06/2026. Treat them as operational guidance, not legal or accounting advice. Recheck before filing, sending formal legal notices, or issuing tax-sensitive documents.

| Topic | Validated value | Operational use |
|---|---:|---|
| Standard VAT rate | 18% | Do not calculate VAT inside this skill. Use only to flag that invoice totals may need accounting review. |
| Small-claims ceiling | ₪39,900 as of 01/01/2026 | Use only to decide whether to prepare a small-claims evidence pack. Recheck on filing day. |
| Small-claims filing fee | 1% of claim amount, minimum ₪50 | Show as a filing checklist item, not an automatic ledger charge. |
| Fixed-amount enforcement claim ceiling | ₪75,000 | Use only after legal review and qualifying documentation. |
| Enforcement opening fee, regular route | 1% of updated debt, minimum ₪109 | Verify in the current fee table before opening a file. |
| Enforcement opening fee, short route | 1% of updated debt, minimum ₪103, plus ₪78 management fee | Verify in the current fee table before opening a file. |
| Israel Invoice allocation threshold | Above ₪10,000 before VAT from 01/01/2026; above ₪5,000 before VAT from 01/06/2026 | Relevant to tax-invoice systems, not to reminder generation. |
| Israel Invoice approval endpoint | `https://ita-api.taxes.gov.il/shaam/production/Invoices/v2/Approval` | Use only from certified/accounting software with OAuth2. |
| Israel Invoice confirmation endpoint | `https://openapi.taxes.gov.il/shaam/production/invoice-information/v1/confirmationNumber` | Use only to verify allocation numbers in accounting workflows. |
| WhatsApp messages endpoint pattern | `https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages` | Do not hardcode an old Graph API version in production. |
| WhatsApp template language code for Hebrew | `he` | Use approved Hebrew templates for outbound reminders outside the service window. |
| WhatsApp webhook subscription field | `messages` | Use webhook payloads to log inbound messages and delivery statuses. |

## Israeli regulations and legal sources

| Source | Hebrew name | Collection relevance | Operational rule |
|---|---|---|---|
| Payment Ethics to Suppliers Law, 5777-2017 | חוק מוסר תשלומים לספקים, תשע״ז-2017 | Sets payment timing norms and late-payment consequences for supplier invoices. | Calculate lateness from the agreed/statutory due date, not from issue date. |
| Interest and Linkage Adjudication Law, 5721-1961 | חוק פסיקת ריבית והצמדה, תשכ״א-1961 | Governs interest/linkage awarded by a court or judgment context. | Do not use as a pre-lawsuit invented rate. |
| Execution Law, 5727-1967 | חוק ההוצאה לפועל, תשכ״ז-1967 | Governs enforcement of judgments, cheques, and enforceable documents. | Use only after judgment, negotiable instrument, or qualifying procedure. |
| Courts Law and Small Claims regulations | חוק בתי המשפט ותקנות שיפוט בתביעות קטנות | Governs small-claims procedure, representation limits, claim ceiling, and filing fee. | Verify the current ceiling and fee before recommending a filing route. |
| Value Added Tax Law and Israel Invoice model | חוק מס ערך מוסף ומודל חשבוניות ישראל | Relevant when the underlying bookkeeping system issues tax invoices. | This skill must not issue tax invoices or bypass allocation-number checks. |
| Protection of Privacy Law, 5741-1981 | חוק הגנת הפרטיות, תשמ״א-1981 | Applies to storage of client contact details, debt data, messages, and evidence files. | Store only necessary data, restrict access, and define retention periods. |
| Communications Law anti-spam provisions, section 30A | חוק התקשורת, סעיף 30א | Mainly targets advertising messages, but collection messages must still avoid spam-like behavior. | Send debt-related operational messages only to verified contacts and with proper purpose. |
| Evidence law and civil procedure principles | דיני ראיות וסדר דין אזרחי | Reminder logs, WhatsApp exports, email headers, contracts, and delivery proofs may support claims. | Preserve original files and metadata where possible. |
| Consumer Protection Law, 5741-1981 | חוק הגנת הצרכן, תשמ״א-1981 | Relevant when the debtor is a consumer. | Use restrained collection language and avoid misleading pressure. |

## Government and public service reference links

These links are operational starting points. Confirm the current page before use.

| Service | URL | Use |
|---|---|---|
| VAT history | `https://www.gov.il/he/pages/vat-history` | Verify the standard VAT rate. |
| Tax terminology | `https://www.gov.il/he/pages/taxes-glossary` | Verify Hebrew and English tax terminology. |
| Israel Invoice topic | `https://www.gov.il/he/departments/topics/israel-invoice` | Verify tax-invoice allocation-number rules. |
| Israel Invoice API description | `https://www.gov.il/BlobFolder/generalpage/hor-software-other/he/vat_software-houses-180724.pdf` | Verify endpoint paths and request/response schemas for accounting software. |
| Small claim filing service | `https://www.gov.il/he/service/filing_a_small_claim` | File a small claim or confirm current ceiling and fee. |
| Enforcement and Collection Authority | `https://www.gov.il/he/departments/enforcement_and_collection_authority/govil-landing-page` | Confirm enforcement process and forms. |
| Opening an enforcement file for a monetary judgment or fixed amount claim | `https://www.gov.il/he/service/claim_for_a_specified_amount_opening_file` | Check threshold, required forms, and process. |
| Enforcement fee table | `https://www.gov.il/he/pages/fees-table-eca` | Confirm current fees before opening a file. |
| Courts Authority services | `https://www.gov.il/he/departments/the_judicial_authority/govil-landing-page` | Confirm court forms and procedural updates. |
| Accountant General | `https://www.gov.il/he/departments/general/accountant_general` | Verify current Accountant General late-payment rates when relevant. |
| Bank of Israel statistics/data portal | `https://www.boi.org.il/` | Verify macro rates when needed; do not confuse policy rate with statutory late-payment rates. |
| Israel Postal Company registered mail | `https://israelpost.co.il/` | Send and track registered demand letters. |

## Integration surfaces

### 1. Ledger JSON file

Use the local JSON ledger as the canonical integration format when an accounting API is unavailable.

#### Request example: ledger import

```json
{
  "business": {
    "name": "סטודיו דוגמה",
    "payment_instructions": "בנק 12, סניף 345, חשבון 67890",
    "default_currency": "ILS"
  },
  "clients": [
    {
      "client_id": "c-100",
      "name": "לקוח לדוגמה בע"מ",
      "email": "client@example.co.il",
      "whatsapp": "+972501234567",
      "mailing_address": "רחוב הדוגמה 1, תל אביב"
    }
  ],
  "invoices": [
    {
      "invoice_id": "INV-100",
      "client_id": "c-100",
      "issue_date": "01/01/2026",
      "due_date": "31/01/2026",
      "amount": "2500.00",
      "currency": "ILS",
      "status": "open",
      "partial_payments": [
        {"date": "10/03/2026", "amount": "500.00"}
      ]
    }
  ],
  "blocked_dates": ["23/04/2026"]
}
```

#### Response example: aging summary

```json
{
  "as_of": "15/04/2026",
  "totals": {
    "open_invoices": 1,
    "outstanding_amount": "2000.00",
    "currency": "ILS"
  },
  "invoices": [
    {
      "invoice_id": "INV-100",
      "client_name": "לקוח לדוגמה בע"מ",
      "due_date": "31/01/2026",
      "age_days": 74,
      "bucket": "60",
      "stage": "formal_email",
      "outstanding_amount": "2000.00",
      "requires_human_review": true
    }
  ]
}
```

### 2. CSV import

Use CSV for exports from bookkeeping systems.

#### Required columns

```csv
invoice_id,client_id,client_name,issue_date,due_date,amount,currency,status,email,whatsapp,mailing_address
INV-100,c-100,לקוח לדוגמה בע"מ,01/01/2026,31/01/2026,2500.00,ILS,open,client@example.co.il,+972501234567,"רחוב הדוגמה 1, תל אביב"
```

#### Error table

| Code | Meaning | Fix |
|---|---|---|
| `CSV_MISSING_COLUMN` | Required column absent. | Add the missing column or map it before import. |
| `CSV_BAD_DATE` | Date not in ISO or DD/MM/YYYY format. | Convert to `DD/MM/YYYY` or `YYYY-MM-DD`. |
| `CSV_BAD_AMOUNT` | Amount is empty, negative, or not numeric. | Export numeric principal amount only. |
| `CSV_UNKNOWN_CLIENT` | Invoice references a missing client. | Add a client row or include client fields in each invoice row. |
| `CSV_UNSUPPORTED_CURRENCY` | Currency is not `ILS`. | Enable foreign currency handling or convert before import. |

### 3. WhatsApp Business Cloud API

Use only with a properly configured WhatsApp Business account and approved templates where required. Free-form collection messages may fail outside the customer-service window. Use the current Graph API version configured for the business; do not copy an old version string into production.

#### Outbound message request

```http
POST https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json
```

```json
{
  "messaging_product": "whatsapp",
  "to": "972501234567",
  "type": "template",
  "template": {
    "name": "invoice_payment_reminder_he",
    "language": {"code": "he"},
    "components": [
      {
        "type": "body",
        "parameters": [
          {"type": "text", "text": "לקוח לדוגמה בע"מ"},
          {"type": "text", "text": "INV-100"},
          {"type": "text", "text": "₪2,000.00"},
          {"type": "text", "text": "31/01/2026"}
        ]
      }
    ]
  }
}
```

#### Success response

```json
{
  "messaging_product": "whatsapp",
  "contacts": [{"input": "972501234567", "wa_id": "972501234567"}],
  "messages": [{"id": "wamid.example"}]
}
```

#### Webhook handling

Subscribe the app to the WhatsApp Business Platform `messages` field. Log inbound customer messages and delivery status payloads with the invoice ID, message ID, timestamp, and raw provider payload hash.

#### Error table

| HTTP | Code | Meaning | Fix |
|---:|---|---|---|
| 400 | `BAD_PHONE` | Phone number is invalid. | Normalize Israeli mobile to E.164. |
| 400 | `TEMPLATE_REJECTED` | Template missing or not approved. | Submit a neutral Hebrew template for approval. |
| 401 | `AUTH_FAILED` | Token invalid or expired. | Refresh credentials and rotate securely. |
| 429 | `RATE_LIMIT` | Send rate exceeded. | Back off and retry later. |
| 470 | `WINDOW_CLOSED` | Session window closed for free-form message. | Use an approved template. |

### 4. Email delivery

Use SMTP or an email API with SPF, DKIM, and DMARC configured. Keep message IDs and delivery logs. For bulk sending to large mailbox providers, authentication requirements are stricter; keep collection reminders low-volume, operational, and tied to verified debts.

#### SMTP-style request object

```json
{
  "to": "client@example.co.il",
  "subject": "דרישת תשלום עבור חשבונית INV-100",
  "body": "לכבוד לקוח לדוגמה בע"מ...
יתרת החוב: ₪2,000.00",
  "attachments": [
    {"filename": "INV-100.pdf", "content_type": "application/pdf"}
  ],
  "headers": {
    "X-Invoice-ID": "INV-100",
    "X-Collection-Stage": "formal_email"
  }
}
```

#### Error table

| Code | Meaning | Fix |
|---|---|---|
| `EMAIL_BOUNCE` | Address rejected. | Verify contact and retry only after correction. |
| `EMAIL_SPAM_REJECT` | Domain authentication or content problem. | Fix SPF/DKIM/DMARC and simplify language. |
| `EMAIL_ATTACHMENT_BLOCKED` | Attachment rejected. | Send a secure link or compressed PDF when permitted. |
| `EMAIL_RATE_LIMIT` | Provider throttled sending. | Queue messages and retry with backoff. |

### 5. Israel Invoice API reference for accounting integrations

This package does not call these APIs. Include this section so implementers do not confuse reminder generation with issuing tax invoices.

#### Approval request endpoint

```http
POST https://ita-api.taxes.gov.il/shaam/production/Invoices/v2/Approval
Authorization: Bearer {OAUTH2_ACCESS_TOKEN}
Content-Type: application/json
Accept: application/json
```

```json
{
  "id_invoice": "internal-unique-id-100",
  "type_invoice": 305,
  "number_vat": 512345678,
  "invoice_reference_number": "INV-100",
  "amount_before_discount": 2500.00,
  "amount_discount": 0.00,
  "amount_payment": 2500.00,
  "amount_vat": 450.00,
  "invoice_date": "2026-06-01"
}
```

#### Confirmation lookup endpoint

```http
POST https://openapi.taxes.gov.il/shaam/production/invoice-information/v1/confirmationNumber
Authorization: Bearer {OAUTH2_ACCESS_TOKEN}
Content-Type: application/json
Accept: application/json
```

```json
{
  "Customer_VAT_Number": 512345678,
  "Vat_Number": 513333333,
  "Payment_Amount": 2500.00,
  "VAT_Amount": 450.00,
  "Invoice_Date": "2026-06-01",
  "Invoice_Reference_Number": "INV-100"
}
```

#### API error table

| HTTP | Meaning | Fix |
|---:|---|---|
| 400 | Request syntax or field validation failed. | Validate JSON schema, data types, invoice date, VAT number, and unique ID. |
| 401 | OAuth2 token missing or expired. | Refresh the token through the Tax Authority authorization process. |
| 403 | Missing permission for the service. | Verify software-house registration and taxpayer authorization. |
| 404 | URI or resource not found. | Check endpoint path and environment. |
| 406 | Content negotiation failed. | Send `Accept: application/json` and `Content-Type: application/json`. |

### 6. Registered-mail tracking

Use registered mail for final demand letters when evidence of dispatch matters.

#### Request object

```json
{
  "recipient_name": "לקוח לדוגמה בע"מ",
  "recipient_address": "רחוב הדוגמה 1, תל אביב",
  "document_type": "final_demand_letter",
  "invoice_ids": ["INV-100"],
  "tracking_number": "RR123456789IL",
  "sent_date": "15/04/2026"
}
```

#### Response object

```json
{
  "tracking_number": "RR123456789IL",
  "status": "sent",
  "evidence_required": [
    "signed demand letter",
    "postal receipt",
    "tracking screenshot or delivery confirmation"
  ]
}
```

#### Error table

| Code | Meaning | Fix |
|---|---|---|
| `ADDRESS_INCOMPLETE` | Missing city, street, or number. | Confirm mailing address before dispatch. |
| `DOCUMENT_UNSIGNED` | Demand letter lacks signature. | Sign and date before mailing. |
| `TRACKING_MISSING` | Tracking number not recorded. | Record postal receipt before closing the task. |

## Security and evidence requirements

- Keep client phone numbers, emails, and debt amounts in restricted storage.
- Mask phone numbers and emails in logs unless full detail is required.
- Keep sent messages, provider IDs, and delivery status separately from editable templates.
- Hash exported evidence bundles so later changes are detectable.
- Store legal review approvals for formal stages.
