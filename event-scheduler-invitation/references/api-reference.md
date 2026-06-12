# Israeli API and Regulation Reference

This skill is designed as an operational planning helper. It does not depend on a single public Israeli event API. Treat the following interfaces as adapter contracts, reference checklists, and integration boundaries. Verify current official requirements before production use, payment, registration, or message distribution.

## Source-of-record principles

| Topic | Source of record | Use in event planning |
|---|---|---|
| Marriage registration | Local Religious Council / Chief Rabbinate service channels | Verify marriage-file window, documents, fee, kashrut certificate, and ceremony requirements |
| Music performance license | ACUM event licensing/payment portal | Check whether music played at a family/commercial event requires a license and confirm payment deadline |
| Privacy | Protection of Privacy Law, 5741-1981; Protection of Privacy Regulations (Data Security), 5777-2017 | Minimize guest data, limit access, delete unneeded sensitive notes |
| Message consent | Communications Law (Telecommunications and Broadcasting), 5742-1982, section 30A | Avoid unsolicited advertising messages; include opt-out where messages could be promotional |
| Accessibility | Equal Rights for Persons with Disabilities Law, 5758-1998; accessibility regulations applicable to public places/services | Confirm accessible route, toilets, parking, seating, website/form accessibility where relevant |
| Tax/VAT documentation | VAT Law, 5736-1975; Israel Tax Authority rules; invoice allocation requirements where applicable | Track invoices, receipts, VAT, supplier identity, and allocation numbers when required |
| Municipal licensing/noise | Local authority bylaws and business licensing conditions | Confirm closing time, noise limits, outdoor amplification, security, police/municipal constraints |
| Food/kashrut | Local Rabbinate/kashrut certificate or chosen supervision body | Confirm certificate validity, menu scope, and event-date applicability |
| Medical ceremony constraints | Licensed physician/mohel/medical professional | For brit milah, medical clearance overrides the planned date |



## Web-validated values as of 04/06/2026

Treat these values as planning checkpoints, not as legal or accounting advice. Recheck the official source before issuing a payment, invoice, invitation campaign, venue commitment, or public-event request.

| Area | Current value or terminology | Source to recheck | Operational use |
|---|---:|---|---|
| VAT rate | 18% from 01/01/2025 and still current in the 2026 validation pass | Israel Tax Authority VAT glossary and VAT history | Budget quotes, supplier invoices, customer-event billing |
| Israel invoice allocation | ₪10,000 before VAT from 01/01/2026; ₪5,000 before VAT from 01/06/2026 | Israel Tax Authority allocation-number service | Flag supplier/customer invoices for allocation-number follow-up |
| ACUM family event | ₪395.30 including VAT for a single family event; arrange up to 72 hours before the event | ACUM family-event portal | Wedding, bar/bat mitzvah, birthday, brit/brita, henna, and similar family events |
| ACUM business event | Separate 2026 tariff by audience tier and music use | ACUM business-event portal | Customer events, company events, client evenings, paid promotional gatherings |
| Event-hall noise monitor | Noise limiter/monitor checkpoint, including 95 dB average threshold in current Ministry guidance | Ministry of Environmental Protection | Venue due-diligence question before deposit |
| Brit milah mohel fee reference | Recommended fee: certified mohel ₪1,000; expert mohel ₪1,500 | Chief Rabbinate national mohel list | Budget estimate only; medical clearance overrides ceremony pressure |
| WhatsApp webhooks | Meta integrations subscribe to `messages`; provider statuses include `sent`, `delivered`, `read`, `failed` | Meta WhatsApp Business Platform docs | Map external provider status to internal RSVP/message logs |

### Corrected during final web validation

An older Israel Invoices API PDF listed future thresholds of ₪15,000 for 2026, ₪10,000 for 2027, and ₪5,000 for 2028. The current Israel Tax Authority service page and Hebrew service page state that the applicable 2026 thresholds are ₪10,000 from 01/01/2026 and ₪5,000 from 01/06/2026. Use the current service page as the source of record for operational planning.

## Adapter: Guest RSVP store

Use this adapter for local files, spreadsheets, CRM records, or a small business database.

### Request: create or update guest

```http
PUT /rsvp/guests/{guest_id}
Content-Type: application/json
```

```json
{
  "guest_id": "G-00042",
  "household_name": "משפחת לוי",
  "contact_name": "דנה לוי",
  "phone": "+972501234567",
  "email": "dana@example.com",
  "party_size_invited": 4,
  "party_size_confirmed": 3,
  "status": "confirmed",
  "group": "כלה",
  "children_count": 1,
  "dietary": ["טבעוני"],
  "accessibility": ["גישה לכיסא גלגלים"],
  "transport": "needs_shuttle",
  "language": "he",
  "updated_at": "2026-06-01T12:30:00+03:00"
}
```

### Response

```json
{
  "ok": true,
  "guest_id": "G-00042",
  "normalized_phone": "+972501234567",
  "warnings": [
    "party_size_confirmed lower than invited; confirm children count separately"
  ]
}
```

### Errors

| Code | Meaning | Recovery |
|---|---|---|
| `PHONE_INVALID` | Phone number cannot be normalized to an Israeli or international format | Call the guest or request correction |
| `STATUS_INVALID` | Status is not one of the allowed values | Map free text to `confirmed`, `declined`, `tentative`, `no_response` |
| `PARTY_SIZE_OVER_INVITED` | Confirmed count exceeds invited count | Confirm whether extra guest is allowed |
| `DUPLICATE_GUEST` | Same phone/household appears more than once | Merge records and keep history |
| `SENSITIVE_DATA_EXCESS` | Notes contain unnecessary medical or personal data | Replace with operational tags only |

## Adapter: Hebrew RSVP message sender

Use this adapter for SMS, WhatsApp Business, email, or manual copy/paste workflows. For automated distribution, verify consent, opt-out requirements, platform rules, and message logs.

### Request: send invitation

```http
POST /messages/send
Content-Type: application/json
```

```json
{
  "channel": "whatsapp",
  "purpose": "event_rsvp",
  "recipient": {
    "name": "דנה לוי",
    "phone": "+972501234567",
    "language": "he"
  },
  "message": "שלום דנה, נשמח לאישור הגעה לחתונה של מאיה ויונתן בתאריך 18/06/2026. נא להשיב במספר המגיעים, ילדים, רגישויות למזון וצורך בהסעה. להסרה מרשימת עדכונים כתבו \"הסר\".",
  "consent_basis": "event_relationship",
  "contains_marketing": false,
  "opt_out_text": "הסר"
}
```

### Response

```json
{
  "ok": true,
  "message_id": "MSG-20260601-0001",
  "queued_at": "2026-06-01T09:15:00+03:00",
  "delivery_status": "queued"
}
```

### Errors

| Code | Meaning | Recovery |
|---|---|---|
| `CONSENT_REQUIRED` | Message appears promotional or unrelated to the event | Obtain consent or remove promotional content |
| `OPT_OUT_MISSING` | Bulk message lacks removal path | Add clear Hebrew opt-out text |
| `CHANNEL_RATE_LIMIT` | Platform throttled sends | Slow down and prioritize no-response guests |
| `TEMPLATE_REJECTED` | WhatsApp/SMS provider rejected wording | Use approved template or manual message |
| `LANGUAGE_MISMATCH` | Guest language differs from message language | Send correct language version |


### Optional WhatsApp provider webhook mapping

This package does not implement a live WhatsApp webhook. If an external provider or Meta WhatsApp Business Platform is connected, keep provider events separate from internal RSVP status.

| External item | Verified terminology | Internal mapping |
|---|---|---|
| Subscribed field | `messages` | Message receipt/status ingestion |
| Status payload values | `sent`, `delivered`, `read`, `failed` | Delivery audit trail; do not treat as RSVP confirmation |
| Incoming text/button reply | Messages webhook payload | Parse into `confirmed`, `declined`, `tentative`, or `no_response` only after explicit guest answer |

## Adapter: Venue availability and quote

Many Israeli venues do not expose public APIs. Use this schema for comparing quotes collected by email, phone, portal, or PDF.



### Venue verification checkpoints

Ask for written confirmation of business-license status, accessibility arrangements, kashrut certificate scope, insurance, closing hour, outdoor-sound restrictions, and whether the venue uses the required noise monitor/limiter where applicable. Ministry guidance for event spaces includes a 95 dB average threshold for the noise-monitor checkpoint.

### Request: quote capture

```json
{
  "venue_name": "גן אירועים לדוגמה",
  "city": "רחובות",
  "event_date": "18/06/2026",
  "event_type": "wedding",
  "guest_count_expected": 250,
  "guest_count_minimum": 240,
  "per_plate_nis": 330,
  "vat_included": true,
  "kosher_certificate": "local_rabbinate",
  "accessibility_confirmed": true,
  "parking_spaces": 160,
  "rain_backup": "indoor_hall",
  "sound_end_time": "23:30",
  "cancellation_terms": "deposit retained after 30 days before event"
}
```

### Response

```json
{
  "ok": true,
  "estimated_total_nis": 82500,
  "capacity_status": "ok",
  "risks": [
    "parking_spaces lower than expected vehicles",
    "confirm whether sound_end_time applies to outdoor area only"
  ]
}
```

### Errors

| Code | Meaning | Recovery |
|---|---|---|
| `QUOTE_NOT_ITEMIZED` | VAT, service, security, or menu tiers unclear | Request itemized quote |
| `MINIMUM_TOO_HIGH` | Guaranteed minimum exceeds realistic attendance | Negotiate minimum or choose another date |
| `ACCESSIBILITY_UNVERIFIED` | Venue gave generic accessibility claim only | Verify route, toilet, parking, and seating |
| `KASHRUT_SCOPE_UNCLEAR` | Certificate does not clearly cover event/date/menu | Request current certificate |
| `WEATHER_BACKUP_MISSING` | Outdoor event lacks backup | Add indoor/covered alternative before deposit |

## Adapter: Calendar event creation

Calendar APIs are not Israel-specific, but the event payload must respect Israeli date/time conventions and holidays.

### Request

```json
{
  "title": "חתונה - מאיה ויונתן",
  "start": "2026-06-18T19:00:00+03:00",
  "end": "2026-06-19T01:00:00+03:00",
  "timezone": "Asia/Jerusalem",
  "location": "רחובות",
  "description": "קבלת פנים 19:00, חופה 20:30, איש קשר: דנה 050-1234567",
  "reminders": [
    {"method": "popup", "minutes": 10080},
    {"method": "popup", "minutes": 1440}
  ]
}
```

### Response

```json
{
  "ok": true,
  "calendar_event_id": "cal_abc123",
  "warnings": [
    "event crosses midnight; verify supplier end dates"
  ]
}
```

### Errors

| Code | Meaning | Recovery |
|---|---|---|
| `TIMEZONE_MISSING` | Time interpreted outside Israel time | Set `Asia/Jerusalem` |
| `HOLIDAY_CONFLICT` | Event may conflict with holiday/Shabbat/custom | Verify with a calendar and relevant authority |
| `MIDNIGHT_SPLIT` | Supplier tasks after midnight have wrong date | Store explicit start and end timestamps |
| `REMINDER_TOO_LATE` | Reminder occurs after supplier deadline | Add earlier reminder |

## Adapter: ACUM music license checkpoint

The ACUM portal is the source of record for current licensing requirements and fees. Use this adapter only to track an internal checkpoint.



### Verified ACUM planning values

| Event class | Planning value | Action |
|---|---:|---|
| Family event using ACUM repertoire | ₪395.30 including VAT for a single event | Arrange and pay up to 72 hours before the event |
| Business/customer event | Separate 2026 tariff by audience size and music use | Check the business-event ACUM page before quoting |

Do not reuse the family-event fee for a company, customer, employee-committee, or promotional event.

### Request

```json
{
  "event_type": "wedding",
  "event_date": "18/06/2026",
  "venue_name": "גן אירועים לדוגמה",
  "music_type": "dj",
  "public_performance": true,
  "license_checked_at": "2026-06-10T10:00:00+03:00",
  "payment_status": "pending"
}
```

### Response

```json
{
  "ok": true,
  "required_action": "verify_and_pay_on_official_portal",
  "deadline_hint": "complete before the portal deadline; many event workflows use at least 72 hours buffer"
}
```

### Errors

| Code | Meaning | Recovery |
|---|---|---|
| `LICENSE_STATUS_UNKNOWN` | No proof of license/payment | Verify in official portal |
| `EVENT_TYPE_UNCLEAR` | Family/private/commercial classification unclear | Confirm with ACUM or legal adviser |
| `PAYMENT_PROOF_MISSING` | Payment made but receipt unavailable | Store receipt and license number |
| `DEADLINE_RISK` | License check too close to event | Escalate immediately |

## Adapter: Marriage-registration checkpoint

Local procedures can differ. Use this adapter to track documents and deadlines, not to determine eligibility.

### Request

```json
{
  "event_type": "wedding",
  "wedding_date": "18/06/2026",
  "religious_council": "רחובות",
  "documents": {
    "id_cards": true,
    "passport_photos": true,
    "parents_ketubah": true,
    "single_status_certificate": false,
    "venue_kashrut_certificate": true
  },
  "registration_status": "not_started"
}
```

### Response

```json
{
  "ok": true,
  "next_action": "book appointment with local Religious Council",
  "warnings": [
    "single status certificate may be required when registering outside place of residence",
    "verify current fee and discount eligibility"
  ]
}
```

### Errors

| Code | Meaning | Recovery |
|---|---|---|
| `WINDOW_RISK` | Registration may be outside required timing window | Contact Religious Council immediately |
| `DOCUMENT_MISSING` | Required document not present | Obtain official copy before appointment |
| `KASHRUT_NOT_ACCEPTED` | Venue certificate may not satisfy council | Ask venue and council for written confirmation |
| `ELIGIBILITY_COMPLEX` | Conversion, divorce, widowhood, immigration, or kohen issue present | Seek qualified guidance before booking dependent steps |

## Adapter: Tax and supplier documentation

Use this adapter for small businesses/freelancers coordinating supplier payments or billing customers. As of the 04/06/2026 validation pass, use 18% as the planning VAT rate and flag allocation-number follow-up for relevant authorized-dealer invoices above ₪10,000 before VAT from 01/01/2026 through 31/05/2026 and above ₪5,000 before VAT from 01/06/2026. Recheck the Israel Tax Authority portal before issuing or deducting an invoice.

### Request

```json
{
  "supplier_name": "צילום לדוגמה בע\"מ",
  "supplier_id": "512345678",
  "category": "photography",
  "quote_nis": 12000,
  "invoice_amount_before_vat_nis": 10169.49,
  "vat_rate": 0.18,
  "vat_included": true,
  "deposit_paid_nis": 3000,
  "payment_method": "bank_transfer",
  "invoice_received": true,
  "invoice_number": "2026-1042",
  "allocation_number": "required_if_over_current_threshold",
  "allocation_threshold_before_vat_nis": 5000
}
```

### Response

```json
{
  "ok": true,
  "open_balance_nis": 9000,
  "documentation_status": "complete",
  "warnings": [
    "invoice requires allocation-number follow-up under current 2026 threshold"
  ]
}
```



### Israel invoice allocation threshold table

| Invoice date | Planning threshold before VAT | Action |
|---|---:|---|
| 01/01/2025-31/12/2025 | ₪20,000 | Check allocation-number requirement above threshold |
| 01/01/2026-31/05/2026 | ₪10,000 | Check allocation-number requirement above threshold |
| From 01/06/2026 | ₪5,000 | Check allocation-number requirement above threshold |

The Python helper exposes this as `israel_invoice_allocation_threshold()` and `tax_documentation_check()`.

### Errors

| Code | Meaning | Recovery |
|---|---|---|
| `INVOICE_MISSING` | Payment lacks receipt/invoice | Request documentation |
| `VAT_UNCLEAR` | Quote does not state VAT included/excluded | Request corrected quote |
| `SUPPLIER_ID_MISSING` | Supplier identity incomplete | Request licensed business details |
| `ALLOCATION_REQUIRED_UNKNOWN` | Invoice allocation applicability unclear | Check current Israel Tax Authority guidance |
| `CASH_RISK` | Cash-only payment creates documentation risk | Use documented payment or written receipt |

## Data retention matrix

| Data type | Example | Keep until | Notes |
|---|---|---|---|
| RSVP status | Confirmed count | Event closeout + dispute window | Delete or anonymize after no longer needed |
| Dietary need | Gluten-free | Event closeout | Do not store broad medical history |
| Accessibility need | Wheelchair access | Event closeout | Share only with venue/event manager as needed |
| Payment record | Supplier invoice | Accounting retention period | Follow accountant guidance |
| Marketing consent | Customer event opt-in | Until revoked or no longer needed | Keep opt-out log |
| Sensitive family note | Seating conflict | Event closeout | Limit access tightly |

## Production validation checklist

- [ ] Official portal or authority checked for every binding requirement.
- [ ] All dynamic fees treated as estimates until verified.
- [ ] Guest data export protected with limited access.
- [ ] Bulk message includes purpose, sender identity, and opt-out when appropriate.
- [ ] Venue claims verified in writing.
- [ ] Supplier quote states VAT and invoice terms.
- [ ] Music license, marriage registration, medical clearance, and accessibility checks assigned to named owners.
