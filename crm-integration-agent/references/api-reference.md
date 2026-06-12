# API and Regulatory Reference

This reference lists provider payloads, response examples, operational errors, and Israeli regulatory checkpoints relevant to conversation synchronization. Endpoint paths and Israeli regulatory references were validated on 04/06/2026; verify legal advice with qualified counsel before production use.

## Israeli regulatory checkpoints

| Area | Source to review | Operational implication |
|---|---|---|
| Privacy and databases | Protection of Privacy Law, 5741-1981, Amendment 13 guidance | Store only data required for the service purpose. Define retention and access controls. Check whether database registration or notification duties apply. |
| Data security | Protection of Privacy Regulations, Data Security, 5777-2017 | Classify the database, restrict access, document incidents, and control exports. |
| Direct marketing and spam | Telecommunications Law, 5742-1982, section 30A, and Protection of Privacy Authority direct-mail guidance | Send marketing messages only with proper consent or another valid exception. Honor opt-out immediately. Keep source and consent evidence. |
| Consumer records | Consumer Protection Law, 5741-1981 | Keep service, quote, cancellation, and complaint records clear and retrievable. |
| Tax documents | VAT Law and Israel Tax Authority guidance | Current standard VAT rate is 18% from 01/01/2025. Do not treat CRM notes as the official accounting archive for חשבונית מס or קבלה. Store official tax documents in the accounting system. |
| Accessibility and service | Equal Rights for Persons with Disabilities Law and service-accessibility regulations | Keep communication records available for service continuity and accessibility requests. |

## Provider authentication

| Provider | Environment variable | Notes |
|---|---|---|
| Monday | `MONDAY_API_TOKEN` or `MONDAY_API_TOKEN_PRODUCTION` | Use board-specific permissions where possible. |
| HubSpot | `HUBSPOT_API_TOKEN` or `HUBSPOT_API_TOKEN_PRODUCTION` | Use private app scopes limited to CRM objects required by the workflow. |
| Salesforce | `SALESFORCE_API_TOKEN` or `SALESFORCE_API_TOKEN_PRODUCTION` | Use OAuth access tokens and a specific instance base URL. |

Sandbox runs allow missing tokens and never post to external providers.

## Normalized source request

```json
{
  "source_channel": "whatsapp",
  "source_thread_id": "wa-1001",
  "subject": "בקשה להצעת מחיר",
  "contact": {
    "full_name": "דנה כהן",
    "phone": "050-123-4567",
    "email": "dana@example.co.il",
    "company": "כהן עיצוב",
    "preferred_language": "he"
  },
  "messages": [
    {
      "source_message_id": "wa-1001-1",
      "sent_at": "2026-02-18T09:44:00+02:00",
      "direction": "inbound",
      "body": "אפשר לקבל הצעת מחיר עד ₪2,500?",
      "attachments": []
    }
  ],
  "consent": {
    "marketing_opt_in": false,
    "evidence": "פנייה יזומה של לקוחה",
    "channel": "whatsapp",
    "service_context": "בקשת הצעת מחיר"
  },
  "business_purpose": "sales"
}
```

## Normalized dry-run response

```json
{
  "provider": "hubspot",
  "dry_run": true,
  "action": "planned_sync",
  "contact_key": "phone:+972501234567",
  "crm_object_id": null,
  "message_count": 1,
  "warnings": ["marketing_opt_in_false"],
  "payload": {
    "properties": {
      "firstname": "דנה",
      "lastname": "כהן",
      "phone": "+972501234567",
      "email": "dana@example.co.il",
      "company": "כהן עיצוב"
    }
  }
}
```

## Monday request

Endpoint:

```text
POST https://api.monday.com/v2
```

Payload:

```json
{
  "query": "mutation ($board: ID!, $group: String!, $name: String!, $values: JSON!) { create_item(board_id: $board, group_id: $group, item_name: $name, column_values: $values) { id name } }",
  "variables": {
    "board": "123456789",
    "group": "topics",
    "name": "דנה כהן",
    "values": "{\"phone\":{\"phone\":\"+972501234567\",\"countryShortName\":\"IL\"},\"channel\":{\"label\":\"Whatsapp\"},\"source_thread_id\":\"wa-1001\"}"
  }
}
```

Response:

```json
{
  "data": {
    "create_item": {
      "id": "444",
      "name": "דנה כהן"
    }
  }
}
```

## HubSpot request

Endpoint:

```text
POST https://api.hubapi.com/crm/objects/2026-03/contacts
```

Payload:

```json
{
  "properties": {
    "firstname": "דנה",
    "lastname": "כהן",
    "phone": "+972501234567",
    "email": "dana@example.co.il",
    "company": "כהן עיצוב",
    "lifecyclestage": "lead",
    "crm_source_channel": "whatsapp",
    "crm_source_thread_id": "wa-1001",
    "crm_marketing_opt_in": "false",
    "hs_language": "he"
  }
}
```

Response:

```json
{
  "id": "251",
  "properties": {
    "email": "dana@example.co.il"
  },
  "createdAt": "2026-02-18T07:44:00Z"
}
```

## Salesforce request

Endpoint:

```text
POST https://example.my.salesforce.com/services/data/v67.0/sobjects/Lead
```

Payload:

```json
{
  "FirstName": "דנה",
  "LastName": "כהן",
  "Company": "כהן עיצוב",
  "Phone": "+972501234567",
  "LeadSource": "Whatsapp",
  "Source_Channel__c": "Whatsapp",
  "Source_Thread_ID__c": "wa-1001",
  "Marketing_Opt_In__c": false,
  "Consent_Evidence__c": "פנייה יזומה של לקוחה",
  "Description": "18/02/2026 inbound: אפשר לקבל הצעת מחיר עד ₪2,500?"
}
```

Response:

```json
{
  "id": "00Q5g00000ABCDe",
  "success": true,
  "errors": []
}
```

## Live-validation source notes

| Check | Current value | Validation note |
|---|---|---|
| Israeli VAT | 18% from 01/01/2025 | Confirmed against Israel Tax Authority VAT history and tax glossary. Use only as tax-rate context; do not calculate tax filings in this skill. |
| HubSpot contacts create | `/crm/objects/2026-03/contacts` | HubSpot introduced date-versioned APIs in 2026-03 and states new integrations should use the latest date version. |
| Salesforce lead create | `/services/data/v67.0/sobjects/Lead` | Salesforce Summer 26 API version 67.0 is current; the sObject resource pattern is used for record creation. |
| Monday item create | `POST https://api.monday.com/v2` with `create_item` mutation | Monday documents the GraphQL endpoint and create-item operation. |
| WhatsApp webhook field | `messages` | Meta describes messages sent from a WhatsApp user to a business and business message statuses through the messages webhook. |
| HubSpot webhook event names | `object.creation`, `contact.propertyChange`, `contact.deletion`, `contact.privacyDeletion` | HubSpot developer-platform webhook examples include these subscription types. |
| Twilio SMS inbound parameters | `MessageSid`, `From`, `To`, `Body`, `NumMedia` | Twilio documents URL-encoded inbound messaging webhook parameters. |
| SendGrid inbound parse | receiving domain and destination URL | Twilio SendGrid documents the Inbound Parse webhook setup and MX record requirements. |

See `references/verification-log.md` for pass-1 and pass-2 source details, snippets, URLs, and correction status.

## Error table

| Error | Source | Meaning | Handling |
|---|---|---|---|
| `ValidationError` | Local client | Missing or invalid input | Fix the source data before retry. |
| `ConsentRequiredError` | Local client | Marketing run lacks explicit opt-in evidence | Add consent evidence or run as service context only. |
| HTTP 400 | Provider | Invalid field, malformed payload, or missing custom property | Compare payload with destination schema. |
| HTTP 401 | Provider | Invalid or expired token | Rotate token and retry once. |
| HTTP 403 | Provider | Missing scope or object permission | Reduce scope or request required permission. |
| HTTP 404 | Provider | Board, property, object, or endpoint not found | Verify board id, property names, base URL, and object type. |
| HTTP 409 | Provider | Duplicate or conflict | Fetch existing record and update instead of create. |
| HTTP 429 | Provider | Rate limit | Back off, reduce batch size, and retry. |
| HTTP 500 to 599 | Provider | Provider fault | Retry with idempotency key and record pending audit state. |

## Audit event reference

```json
{
  "idempotency_key": "whatsapp:wa-1001:wa-1001-1:hubspot",
  "source_channel": "whatsapp",
  "source_thread_id": "wa-1001",
  "source_message_id": "wa-1001-1",
  "crm_provider": "hubspot",
  "crm_object_id": "251",
  "action": "sync_message",
  "status": "success",
  "redacted": false,
  "created_at": "2026-02-18T07:44:00Z"
}
```

Use JSONL for append-only audit output. Keep audit files outside public folders and rotate according to the business retention policy.
