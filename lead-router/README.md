# Lead Router

Route inbound leads to the right person, department, or queue using language, Israeli region, product interest, urgency, channel, and consent signals.

This package contains a bilingual skill guide, integration reference, operational workflows, troubleshooting playbooks, test scenarios, migration checklist, a typed Python client, a Typer CLI, tests, and runnable examples.

## Install for local use

```bash
cd lead-router
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

On Windows PowerShell:

```powershell
cd lead-router
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with create and route

Create a local lead record, extract the returned ID, then route that same record.

```bash
STORE=.lead-router-leads.json

CREATE_RESPONSE=$(lead-router create \
  '{"name":"דנה","phone":"052-1234567","message":"צריכה הצעת מחיר להתקנה באזור חיפה","channel":"whatsapp","consent_marketing":false}' \
  --store "$STORE" \
  --env sandbox)

LEAD_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["lead_id"])' <<< "$CREATE_RESPONSE")

lead-router route-stored --id "$LEAD_ID" --store "$STORE" --env sandbox
```

Expected routing output includes `assignee`, `department`, `priority`, `sla_minutes`, `language`, `region`, `product_interest`, `confidence`, `reason_codes`, `warnings`, and `handoff_note`.

## Quick start in Python

```python
from lead_router import LeadRouterClient

router = LeadRouterClient()
created = router.create_lead({
    "name": "דנה",
    "phone": "052-1234567",
    "message": "צריכה הצעת מחיר להתקנה באזור חיפה",
    "channel": "whatsapp",
    "consent_marketing": False,
}, ".lead-router-leads.json")

result = router.route_stored_lead(created["lead_id"], ".lead-router-leads.json")
print(result.to_json())
```

## CLI examples

Route one lead from flags:

```bash
lead-router route \
  --name "דנה" \
  --phone "052-1234567" \
  --message "צריכה הצעת מחיר להתקנה באזור חיפה" \
  --channel whatsapp \
  --no-marketing-consent \
  --env sandbox
```

Route from JSON:

```bash
lead-router route-json '{"name":"Marina","message":"Устройство не работает","city":"חיפה"}' --env sandbox
```

Route a CSV file:

```bash
lead-router batch leads.csv routed-leads.jsonl --env sandbox
```

Validate a custom config:

```bash
lead-router validate-config routing-config.json --env sandbox
```

## Package index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide with examples, edge cases, decision trees, anti-patterns, and production checklist |
| `SKILL_HE.md` | Hebrew operating guide with Israeli terminology and local formatting |
| `lead_router/client.py` | Typed sync and async client |
| `lead_router/cli.py` | Typer CLI implementation |
| `scripts/lead_router_client.py` | Compatibility import wrapper for script-based usage |
| `scripts/lead_router_cli.py` | Compatibility CLI wrapper for script-based usage |
| `scripts/test_lead_router_client.py` | Pytest suite with 20+ tests |
| `scripts/examples/` | Runnable scenario scripts |
| `references/api-reference.md` | Integration and regulation reference |
| `references/workflow-guide.md` | End-to-end operational workflows |
| `references/troubleshooting.md` | Troubleshooting runbooks |
| `references/test-scenarios.md` | 20+ concrete routing scenarios |
| `references/migration-checklist.md` | Migration plan from manual routing or legacy forms |
| `references/branding-audit.md` | Branding, author, logo, badge, and emoji audit |
| `references/hebrew-qa-log.md` | Hebrew quality assurance change log |
| `references/verification-log.md` | Web validation log for official Israeli and platform sources |
| `CHANGELOG.md` | Keep a Changelog release notes |
| `LICENSE` | MIT license |

## Environment variables

| Variable | Meaning |
|---|---|
| `LEAD_ROUTER_ENV` | Default runtime profile for examples: `sandbox` or `production` |
| `LEAD_ROUTER_CONFIG` | Optional routing configuration JSON path |
| `LEAD_ROUTER_STORE` | Local JSON lead store path for `create` and `route-stored` |
| `LEAD_ROUTER_PHONE` | Example lead phone override |
| `LEAD_ROUTER_MESSAGE` | Example lead message override |
| `LEAD_ROUTER_CHANNEL` | Example lead source channel override |

The runtime profile is explicit to prevent accidental production routing while testing. The local helper does not send data to external services. Re-verify tax, privacy, anti-spam, accessibility, and platform requirements before production launch because official guidance can change.

## Development checks

```bash
pytest
python -m compileall scripts/ -q
python -m compileall lead_router/ -q
```

## Design principles

Keep routing deterministic, auditable, and reversible. Prefer explicit fields over inference. Treat mobile phone prefixes as contact information, not location proof. Preserve original text for multilingual handoff. Do not send marketing messages without explicit consent.
