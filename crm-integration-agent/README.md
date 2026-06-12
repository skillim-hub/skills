# CRM Integration Agent

Neutral skill package for syncing WhatsApp, email, and SMS conversations into Monday, HubSpot, or Salesforce with live-validated 2026 API paths. Use it for Israeli small businesses, freelancers, clinics, service providers, studios, consultants, trades, and consumer-support teams that need reliable customer-history capture without unnecessary personal-data exposure.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a JSON thread file:

```json
{
  "source_channel": "whatsapp",
  "source_thread_id": "wa-1001",
  "subject": "בקשה להצעת מחיר",
  "contact": {
    "full_name": "דנה כהן",
    "phone": "050-123-4567",
    "company": "כהן עיצוב"
  },
  "messages": [
    {
      "id": "wa-1001-1",
      "sent_at": "18/02/2026 09:44:00",
      "direction": "inbound",
      "body": "אפשר לקבל הצעת מחיר עד ₪2,500?"
    }
  ],
  "consent": {
    "marketing_opt_in": false,
    "evidence": "פנייה יזומה של לקוחה"
  },
  "business_purpose": "sales"
}
```

Preview the write:

```bash
crm-integration-agent dry-run --provider hubspot --input thread.json --env sandbox
```

For a production create, write the create response to a file, extract the CRM id, then use that id in the audit step:

```bash
export HUBSPOT_API_TOKEN="replace-with-token"
crm-integration-agent sync --provider hubspot --input thread.json --env production --live > /tmp/create-response.json
CRM_ID=$(python -c "import json; print(json.load(open('/tmp/create-response.json'))['crm_object_id'])")
test -n "$CRM_ID"
crm-integration-agent audit-template --provider hubspot --crm-object-id "$CRM_ID" > /tmp/audit-event.json
```

## Python quick start

```python
from crm_integration_agent import CRMIntegrationClient, load_thread_file, result_to_dict

thread = load_thread_file("thread.json")
client = CRMIntegrationClient.from_env("hubspot", environment="sandbox")
result = client.sync_thread(thread)
print(result_to_dict(result))
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide with decision trees, examples, edge cases, troubleshooting, anti-patterns, and production checklist |
| `SKILL_HE.md` | Hebrew guide with Israeli terminology, ₪ examples, and DD/MM/YYYY date format |
| `references/api-reference.md` | CRM API examples, Israeli regulatory reference, payloads, and error tables |
| `references/workflow-guide.md` | End-to-end workflows for common Israeli business scenarios |
| `references/troubleshooting.md` | Operational diagnosis and fixes |
| `references/test-scenarios.md` | More than 20 concrete test scenarios |
| `references/migration-checklist.md` | Migration checklist for spreadsheets, inboxes, and legacy CRMs |
| `references/branding-audit.md` | Neutrality, attribution, visual-reference, and public-Markdown audit |
| `references/hebrew-qa-log.md` | Hebrew QA changes and localization review |
| `references/verification-log.md` | Web validation log with two-pass source checks and corrections |
| `crm_integration_agent/` | Installable Python package |
| `scripts/` | Compatibility wrappers, examples, and pytest suite |

## Development

```bash
python -m compileall scripts/ -q
python -m pytest -q
```

## Safety defaults

Run sandbox mode first. Store only service-relevant conversation content. Redact Israeli ID numbers, payment-card numbers, and short verification codes before writing notes to CRM. Require explicit evidence before treating any conversation as marketing consent.


## Current validated API defaults

Use these defaults for new integrations unless the provider account requires an older pinned version:

| Provider | Default path or host | Reason |
|---|---|---|
| Monday | `https://api.monday.com/v2` | GraphQL endpoint documented by Monday authentication guidance. |
| HubSpot | `https://api.hubapi.com/crm/objects/2026-03/contacts` | HubSpot 2026-03 date-versioned CRM Contacts endpoint for new integrations. |
| Salesforce | `/services/data/v67.0/sobjects/Lead` on the org My Domain host | Salesforce Summer 26 API version 67.0 with the sObject resource pattern. |

Override the HubSpot or Salesforce version in code only for a tested migration window.
