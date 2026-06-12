# Test Scenarios

Use these scenarios for sandbox verification, unit tests, and production readiness review.

| # | Scenario | Input | Expected result |
|---|---|---|---|
| 1 | Israeli mobile normalization | `050-123-4567` | `+972501234567` |
| 2 | Israeli landline normalization | `03-555-1234` | `+97235551234` |
| 3 | International prefix | `00972501234567` | `+972501234567` |
| 4 | Invalid phone | `123` | Validation error |
| 5 | Email normalization | ` DANA@EXAMPLE.CO.IL ` | `dana@example.co.il` |
| 6 | WhatsApp alias | `wa` | `whatsapp` |
| 7 | SMS alias | `מסרון` | `sms` |
| 8 | Localized date | `18/02/2026` | Parsed date |
| 9 | Quote request | `אפשר לקבל הצעת מחיר?` | `sales` |
| 10 | Complaint | `המוצר תקול ולא הגיע בזמן` | `support` |
| 11 | Invoice request | `נא לשלוח חשבונית מס וקבלה` | `admin` |
| 12 | Appointment request | `אפשר לקבוע תור?` | `appointment` |
| 13 | Opt-out Hebrew | `הסר` | Suppression signal true |
| 14 | Opt-out English | `STOP` | Suppression signal true |
| 15 | Explicit opt-in feminine | `אני מאשרת לקבל עדכונים` | Opt-in evidence detected |
| 16 | Explicit opt-in masculine | `אני מסכים לקבל מבצעים` | Opt-in evidence detected |
| 17 | ID number redaction | `123456789` | `[REDACTED_ID]` |
| 18 | Card number redaction | `4580 1234 1234 1234` | `[REDACTED_CARD]` |
| 19 | Duplicate messages | Same source id twice | One message kept |
| 20 | Message sorting | 10:00 before 09:00 in input | 09:00 stored first |
| 21 | Missing identifier | Name only | Validation error |
| 22 | Marketing run without opt-in | `marketing_action=true` and false consent | Consent error |
| 23 | Marketing opt-in without evidence | true consent and empty evidence | Consent error |
| 24 | Monday dry-run payload | Board id `123` | `create_item` payload generated |
| 25 | HubSpot dry-run payload | Email and phone | Contact properties generated |
| 26 | Salesforce dry-run payload | Base URL provided | Lead payload generated |
| 27 | Provider 429 | Rate response | Rate limit error |
| 28 | Non-JSON provider error | 500 text body | Provider error with body |
| 29 | Async dry-run | One valid thread | Planned sync without network |
| 30 | Audit writing | One event | JSONL line written |
| 31 | Business hours Sunday | Sunday 09:00 | true |
| 32 | Business hours Saturday | Saturday 09:00 | false |
| 33 | Direction inference outbound | Sender is business number | outbound |
| 34 | Direction inference inbound | Sender is customer number | inbound |
| 35 | Production env missing token | HubSpot production without token | Validation error |
| 36 | Sandbox env missing token | HubSpot sandbox without token | Dry-run client created |

## Scenario template

```json
{
  "name": "quote request from WhatsApp",
  "input": {
    "source_channel": "whatsapp",
    "source_thread_id": "wa-1001",
    "contact": {
      "full_name": "דנה כהן",
      "phone": "050-123-4567"
    },
    "messages": [
      {
        "id": "wa-1",
        "sent_at": "18/02/2026 09:44:00",
        "body": "אפשר לקבל הצעת מחיר?"
      }
    ]
  },
  "expected": {
    "contact_key": "phone:+972501234567",
    "business_purpose": "sales",
    "dry_run": true
  }
}
```
