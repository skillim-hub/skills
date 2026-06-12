# Property-Management Scheduler

Local-first toolkit for coordinating maintenance, rent collection, and tenant communication for Israeli landlords, property managers, freelancers, and small offices. Use it as a skill guide, Python package, command-line helper, and testable workflow reference.

## Install

```bash
unzip property-management-scheduler-enhanced-v3.zip
cd property-management-scheduler
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a property, extract the returned id, then reuse that id in the next command.

```bash
property-management-scheduler property-add \
  --address "הירקון 12" \
  --city "תל אביב-יפו" \
  --apartment "8" \
  --store ./demo.json \
  --env sandbox > property.json

PROPERTY_ID=$(python - <<'PY'
import json
print(json.load(open('property.json', encoding='utf-8'))['id'])
PY
)

property-management-scheduler tenant-add \
  --property-id "$PROPERTY_ID" \
  --full-name "דנה כהן" \
  --email dana@example.com \
  --store ./demo.json \
  --env sandbox > tenant.json

TENANT_ID=$(python - <<'PY'
import json
print(json.load(open('tenant.json', encoding='utf-8'))['id'])
PY
)

property-management-scheduler lease-create \
  --property-id "$PROPERTY_ID" \
  --tenant-id "$TENANT_ID" \
  --start-date 01/01/2026 \
  --end-date 31/12/2026 \
  --monthly-rent-ils 5200 \
  --due-day 5 \
  --store ./demo.json \
  --env sandbox > lease.json

LEASE_ID=$(python - <<'PY'
import json
print(json.load(open('lease.json', encoding='utf-8'))['id'])
PY
)

property-management-scheduler rent-generate \
  --lease-id "$LEASE_ID" \
  --from-date 01/01/2026 \
  --months 3 \
  --store ./demo.json \
  --env sandbox

property-management-scheduler reference-values --as-of 01/06/2026
```

## Python quick start

```python
from property_management_scheduler import PropertyManagementScheduler

client = PropertyManagementScheduler("demo.json", environment="sandbox")
prop = client.create_property("הירקון 12", "תל אביב-יפו", "8")
tenant = client.add_tenant(prop["id"], "דנה כהן", email="dana@example.com")
lease = client.create_lease(prop["id"], tenant["id"], "01/01/2026", "31/12/2026", "5200", due_day=5)
charges = client.schedule_rent(lease["id"], "01/01/2026", months=3)
```

## Runnable examples

Each example accepts `--env sandbox|production`, reads environment variables, and prints JSON with `ensure_ascii=False` and `indent=2`.

```bash
python scripts/examples/onboard_property.py --env sandbox
python scripts/examples/rent_collection.py --env sandbox
python scripts/examples/maintenance_triage.py --env sandbox
python scripts/examples/lease_renewal.py --env sandbox
python scripts/examples/accounting_pack.py --env sandbox
```

Useful environment variables include `PMS_ENV`, `PMS_STORE_PATH`, `PMS_DATA_DIR`, `PMS_TENANT_EMAIL`, `PMS_TENANT_PHONE`, `PMS_RENT_ILS`, and `PMS_DUE_DATE`.

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide with examples, decision trees, anti-patterns, and checklist. |
| `SKILL_HE.md` | Hebrew operating guide localized for Israel with ₪ and DD/MM/YYYY dates. |
| `references/api-reference.md` | Integration and regulatory reference with request and response examples. |
| `references/workflow-guide.md` | End-to-end workflows for onboarding, rent collection, maintenance, and accounting preparation. |
| `references/troubleshooting.md` | Failure modes, root causes, and fixes. |
| `references/test-scenarios.md` | More than 20 concrete scenarios for validation. |
| `references/migration-checklist.md` | Migration steps from spreadsheets, calendars, and ad hoc notes. |
| `references/branding-audit.md` | Neutrality and public Markdown audit report. |
| `references/hebrew-qa-log.md` | Hebrew quality review and correction log. |
| `references/verification-log.md` | Two-pass web validation log with sources, snippets, status, and package actions. |
| `property_management_scheduler/client.py` | Typed local-first sync and async client. |
| `property_management_scheduler/cli.py` | Typer command-line interface. |
| `scripts/property_management_scheduler_client.py` | Script-level import helper for the client package. |
| `scripts/property-management-scheduler-cli.py` | Executable command-line wrapper. |
| `scripts/test_property_management_scheduler_client.py` | Pytest suite with sync and async coverage. |
| `scripts/examples/` | Runnable scenario examples. |

## Development checks

```bash
python -m compileall scripts/ -q
pytest -q
```

## Data handling

Store only the minimum tenant data required for operations. Mask identity numbers, protect phone and email details, and restrict access to the JSON store. Do not use automated messaging for sensitive legal notices without manual review.
