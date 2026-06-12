# API and Compliance Reference

This is a reference contract for integrating the Lead Router with forms, CRMs, ticketing systems, WhatsApp inboxes, phone logs, or spreadsheets. The router can run without external APIs. Treat the contracts below as stable internal interfaces.

Regulatory notes are operational awareness, not legal advice. Verify current legal obligations before production use.


## Web-validated source notes

Access date for the sources below: 04/06/2026.

| Area | Validated source | Endpoint, host, or practical reference | Implementation note |
|---|---|---|---|
| VAT | Israel Tax Authority tax terminology and VAT rate pages | `https://www.gov.il/en/pages/taxes-glossary`; `https://www.gov.il/en/pages/vat-rate-amount-new` | Standard VAT validated as 18% from 01/01/2025 for this release. Do not compute invoices in the router; route billing matters to qualified finance staff. |
| Open government data | Israel Government Data Portal CKAN documentation | `https://data.gov.il/docs`; `https://data.gov.il/api/3/action/datastore_search` | Use only as optional enrichment. Cache locality data and record dataset date. |
| Localities | Government locality list and CBS locality files | `data.gov.il` locality datasets; CBS locality files | Prefer explicit user-provided city; use official locality lists only for normalization. |
| Companies and partnerships | Israeli Corporations Authority data services | `https://www.gov.il/he/service/database-companies-partnership`; `data.gov.il` Companies Registrar dataset | Use only for lawful enterprise enrichment. Do not block lead routing if enrichment fails. |
| Privacy | Protection of Privacy Law and Privacy Protection Authority guidance | `https://www.gov.il/he/pages/privacy_law`; `https://www.gov.il/en/pages/data_security_eng` | Minimize data, restrict access, document purpose, and review Amendment 13 obligations before launch. |
| Direct marketing | Communications Law anti-spam guidance | `https://www.gov.il/he/pages/17052018_7` | Store opt-in evidence before promotional messaging. Service replies and marketing messages must stay separate. |
| Telephone numbers | Ministry of Communications numbering plan | Ministry numbering-plan PDF and numbering-services topic page | Treat fixed-line area codes as weak routing hints. Treat mobile prefixes as contact data, not location evidence. |
| Meta Lead Ads | Meta Lead Ads and Webhooks documentation | `https://developers.facebook.com/docs/graph-api/webhooks/getting-started/webhooks-for-leadgen/`; Graph API host `https://graph.facebook.com` | If importing from Meta, subscribe to the Page `leadgen` field and then fetch full lead data using approved permissions. |
| WhatsApp Business | Meta/WhatsApp Business Platform documentation | `developers.facebook.com` WhatsApp docs; `whatsappbusiness.com` platform pricing and categories | Use service replies for user-initiated support. Use approved marketing templates only with opt-in and platform compliance. |

## Core route endpoint contract

### Request

`POST /lead-router/route`

```json
{
  "lead_id": "lead_20260604_0001",
  "name": "דנה לוי",
  "phone": "052-1234567",
  "email": "dana@example.co.il",
  "message": "צריכה הצעת מחיר להתקנה באזור חיפה",
  "language": "he",
  "city": "חיפה",
  "region": null,
  "product_interest": "installation",
  "channel": "whatsapp",
  "budget": 7500,
  "is_urgent": false,
  "consent_marketing": false,
  "created_at": "2026-06-04T09:30:00+03:00",
  "metadata": {"campaign": "summer-installations", "utm_source": "google"}
}
```

### Response

```json
{
  "lead_id": "lead_20260604_0001",
  "assignee": "North Service Queue",
  "department": "installation",
  "priority": "high",
  "sla_minutes": 30,
  "language": "HE",
  "region": "HAIFA",
  "product_interest": "installation",
  "confidence": 0.91,
  "reason_codes": ["LANG_HE", "REGION_HAIFA", "PRODUCT_INSTALLATION", "CHANNEL_WHATSAPP"],
  "warnings": ["MARKETING_CONSENT_MISSING"],
  "handoff_note": "HE lead from HAIFA about installation. Reply in Hebrew. First response within 30 minutes. Marketing follow-up is not allowed without consent."
}
```

## Required fields

At least one contact method is required:

```json
{"phone": "0521234567"}
```

or:

```json
{"email": "lead@example.co.il"}
```

At least one routing signal should be present:

```json
{"message": "צריך התקנה בירושלים"}
```

or:

```json
{"product_interest": "installation", "city": "ירושלים"}
```

## Data dictionary

| Field | Type | Required | Validation | Notes |
|---|---|---:|---|---|
| `lead_id` | string | no | Max 128 chars | Use source ID when available |
| `name` | string | no | Max 200 chars | Do not use for language inference |
| `phone` | string | conditionally | Israeli or international pattern preferred | Store original and normalized values |
| `email` | string | conditionally | Basic email syntax | Lowercase domain |
| `message` | string | no | Max configured size | Preserve original UTF-8 text |
| `language` | string | no | HE/EN/RU/AR or aliases | Explicit selection has high weight |
| `city` | string | no | Free text | Normalize to region but keep original |
| `region` | string | no | Region enum or alias | Explicit value overrides city |
| `product_interest` | string | no | Product enum or alias | Normalize using alias table |
| `channel` | string | no | Known channel enum | Unknown channel is allowed |
| `budget` | number | no | Must be >= 0 | Use ₪ for Israeli display |
| `is_urgent` | boolean | no | true/false | Combine with text signals |
| `consent_marketing` | boolean/null | no | true/false/null | Null means unknown |
| `created_at` | datetime | no | ISO-8601 recommended | Display to Israeli users as DD/MM/YYYY |

## Normalized enum values

### Languages

| Value | Meaning |
|---|---|
| `HE` | Hebrew |
| `EN` | English |
| `RU` | Russian |
| `AR` | Arabic |
| `UNKNOWN` | Not enough signal |

### Regions

| Value | Meaning |
|---|---|
| `CENTER` | Tel Aviv district and nearby central cities |
| `SHARON` | Sharon and coastal plain north of Gush Dan |
| `HAIFA` | Haifa and Krayot |
| `NORTH` | Galilee, Golan, Jezreel, Nazareth, Tiberias area |
| `JERUSALEM` | Jerusalem area and nearby towns |
| `SOUTH` | Ashdod, Ashkelon, Beersheba, Negev |
| `EILAT` | Eilat and Arava |
| `WEST_BANK` | Judea and Samaria / West Bank localities |
| `UNKNOWN` | Not enough signal |

### Product interests

| Value | Meaning |
|---|---|
| `sales` | Pricing, quote, purchase, plan selection |
| `installation` | On-site installation or technician visit |
| `support` | Fault, repair, service issue, troubleshooting |
| `billing` | Invoice, receipt, payment, refund, charge |
| `appointments` | Scheduling, callback, consultation |
| `enterprise` | Multi-branch, procurement, business rollout |
| `urgent` | Emergency or immediate attention |
| `general` | Unclear or missing product interest |

## Error and warning table

| Code | HTTP status | Meaning | Recovery |
|---|---:|---|---|
| `INVALID_JSON` | 400 | Request body is not valid JSON | Send UTF-8 JSON object |
| `MISSING_CONTACT` | 422 or warning | No usable phone or email | Ask for phone or email |
| `INVALID_PHONE` | 200 with warning | Phone cannot be normalized | Keep original and use email if present |
| `UNSUPPORTED_LANGUAGE` | 200 with warning | Detected language is not supported | Route to multilingual intake |
| `UNKNOWN_REGION` | 200 with warning | Region cannot be inferred | Ask for service location |
| `UNKNOWN_PRODUCT` | 200 with warning | Product interest is unclear | Route to qualification |
| `LOW_CONFIDENCE` | 200 with warning | Multiple rules nearly matched | Manual review or secondary qualification |
| `MARKETING_CONSENT_MISSING` | 200 with warning | Marketing follow-up is not permitted | Service response only |
| `DUPLICATE_RISK` | 200 with warning | Similar phone/email seen recently | Merge or route to existing owner |
| `CONFIG_INVALID` | deploy failure | Routing rule config is invalid | Run validation before deployment |

## CRM webhook example

```http
POST /crm/leads/lead_20260604_0001/route-result
Content-Type: application/json
```

```json
{
  "route_assignee": "North Service Queue",
  "route_department": "installation",
  "route_priority": "high",
  "route_sla_minutes": 30,
  "normalized_language": "HE",
  "normalized_region": "HAIFA",
  "normalized_product_interest": "installation",
  "route_confidence": 0.91,
  "route_reason_codes": ["LANG_HE", "REGION_HAIFA", "PRODUCT_INSTALLATION", "CHANNEL_WHATSAPP"],
  "route_warnings": ["MARKETING_CONSENT_MISSING"],
  "rule_version": "1.1.0",
  "routed_at": "2026-06-04T09:31:15+03:00"
}
```

Response:

```json
{
  "status": "accepted",
  "crm_owner_id": "queue_north_service",
  "first_response_due_at": "2026-06-04T10:01:15+03:00"
}
```

## WhatsApp Business handoff example

Use a human service reply when the lead requests service, support, or a quote. Use marketing templates only when proper marketing consent exists.

```json
{
  "to": "+972521234567",
  "language": "he",
  "template": "service_followup_quote_he",
  "parameters": {"first_name": "דנה", "department": "צוות התקנות צפון"}
}
```

Service message:

```text
שלום דנה, קיבלנו את הבקשה שלך להצעת מחיר להתקנה באזור חיפה. צוות ההתקנות יחזור אלייך בהקדם.
```

Do not use promotional wording when `consent_marketing` is `false` or `unknown`.

## Meta lead ad import example

Source payload fragment:

```json
{
  "created_time": "2026-06-04T08:45:00+0000",
  "id": "1234567890",
  "field_data": [
    {"name": "full_name", "values": ["דנה לוי"]},
    {"name": "phone_number", "values": ["0521234567"]},
    {"name": "city", "values": ["חיפה"]},
    {"name": "service", "values": ["התקנה"]}
  ]
}
```

Normalized lead:

```json
{
  "lead_id": "meta_1234567890",
  "name": "דנה לוי",
  "phone": "0521234567",
  "city": "חיפה",
  "product_interest": "התקנה",
  "channel": "meta_lead_ad",
  "created_at": "2026-06-04T11:45:00+03:00",
  "consent_marketing": null
}
```

## CSV import contract

Input CSV:

```csv
name,phone,email,message,city,product_interest,channel,consent_marketing
דנה,0521234567,,צריכה התקנה,חיפה,installation,whatsapp,false
Marina,+972541112222,,Устройство не работает,חיפה,support,web_form,
```

Output JSONL:

```jsonl
{"assignee":"North Service Queue","department":"installation","priority":"high","language":"HE","region":"HAIFA","product_interest":"installation"}
{"assignee":"Russian Support Queue","department":"support","priority":"high","language":"RU","region":"HAIFA","product_interest":"support"}
```

## Optional Israeli data and service references

These references are common in Israeli operations. They may be relevant for enriching or validating leads. Keep enrichment optional and do not block routing when a public service is unavailable.

| Area | Reference | Use | Notes |
|---|---|---|---|
| Public datasets | Israel Government Data Portal (`data.gov.il`) and CKAN API (`/api/3/action/datastore_search`) | Locality lists, public registers, mapping tables | Cache normalized locality maps and record dataset date |
| Address/geography | Israel Survey and mapping services, municipal GIS datasets, and licensed map providers | City/region validation and branch allocation | Verify license and availability before use |
| Postal/address context | Israel Post address and postal-code tools where available | Delivery/service area checks | Do not treat postal code as consent or identity proof |
| Business identity | Israeli Companies Registrar and licensed data providers where applicable | Enterprise lead enrichment | Use only when needed and lawful |
| Holidays/work calendar | Israeli public holiday calendars and internal calendars | SLA adjustment | Configure holiday overrides manually when accuracy matters |

## Israeli regulatory and compliance touchpoints

| Topic | Relevant Israeli framework | Routing implication |
|---|---|---|
| Privacy and databases | Protection of Privacy Law, 5741-1981, and applicable privacy regulations | Collect only required routing data; secure access; document purpose and retention |
| Database security | Privacy Protection Regulations concerning data security | Limit access by role; log access to sensitive lead fields |
| Direct marketing and spam | Communications Law (Telecommunications and Broadcasts), including anti-spam provisions | Separate service response from promotional messaging; store opt-in evidence |
| Consumer transactions | Consumer Protection Law and related rules | Preserve quote details, terms, cancellation context, and consumer-facing claims |
| Accessibility | Equal Rights for Persons with Disabilities Law and accessibility regulations | Provide accessible alternatives and avoid routing barriers |
| Tax documentation | Israeli VAT invoice and receipt practices | Billing leads should route to qualified finance staff; show amounts in ₪ |

## Security requirements

- Use HTTPS for every webhook.
- Sign inbound webhooks where the source supports signatures.
- Avoid logging raw lead text in public logs.
- Redact phone, email, ID numbers, and payment details in debug traces.
- Limit CRM route update permissions to the routing service.
- Store a rule version in every result.
- Store manual overrides separately from automatic decisions.
- Rotate API credentials and remove access for former staff.

## External webhook field notes

The internal events below are local observability names, not official third-party webhook event names. For Meta Lead Ads imports, validate the external Page subscription field `leadgen` against current Meta documentation before production use.

## Observability events

| Event | When |
|---|---|
| `lead.received` | Raw lead accepted from source |
| `lead.normalized` | Language, region, and product inferred |
| `lead.routed` | Rule selected and handoff generated |
| `lead.low_confidence` | Confidence below threshold |
| `lead.warning` | Any warning added |
| `lead.manual_override` | User changes assignee or department |
| `lead.sla_missed` | No first response before SLA |
| `lead.closed` | Lead converted, lost, duplicate, or invalid |
