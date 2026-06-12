# Driving Test & License Renewal Booker

Neutral workflow package for Israeli driving-license renewal, Licensing Bureau appointment preparation, and practical driving-test coordination. Use it for consumers, freelancers, driving teachers, delivery fleets, and small offices that need a repeatable checklist around official Ministry of Transport and Road Safety services.

This package does not bypass identity checks, queue systems, payments, or government portals. Prepare validated payloads, reminders, and handoff records; complete final submission only through official channels. Practical driving-test dates are requested through the authorized driving teacher or driving school process; use this package to coordinate availability and record the confirmed result.

Validated service links in this release use the driver-license payment route at `https://ecom.gov.il/voucherspa/input/209`, the practical-test fee route at `https://ecom.gov.il/voucherspa/input/427`, and GoVisit for Ministry of Transport appointment handoff. Use only the validated driver-license route for driver-license renewal.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a renewal handoff record, extract the request id, then fetch the same record.

```bash
CREATE_RESPONSE=$(driving-license-booker create-renewal   --env sandbox   --state .demo-state.json   --name "Dana Levi"   --national-id 039456785   --phone 0501234567   --license-number 1234567   --expiry-date 2026-08-31)

REQUEST_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["request_id"])' <<< "$CREATE_RESPONSE")

driving-license-booker get --env sandbox --state .demo-state.json "$REQUEST_ID"
```

Python usage:

```python
import datetime as dt
from driving_license_booker import Applicant, DrivingLicenseBookerClient

client = DrivingLicenseBookerClient(environment="sandbox", state_path=".demo-state.json")
applicant = Applicant("Dana Levi", "039456785", "0501234567", license_number="1234567")
payload = client.build_renewal_payload(applicant, expiry_date=dt.date(2026, 8, 31))
response = client.create_booking({"kind": "license_renewal", **payload})
request_id = client.parse_create_response_id(response)
record = client.get_booking(request_id)
print(client.serialize(record))
```

## File index

| Path | Purpose |
| --- | --- |
| `SKILL.md` | English operating guide with examples, decision trees, troubleshooting, anti-patterns, and production checklist. |
| `SKILL_HE.md` | Hebrew operating guide with Israeli terminology, DD/MM/YYYY dates, and ₪ handling. |
| `references/api-reference.md` | Official-service reference, request and response examples, and error tables for adapter-based integrations. |
| `references/workflow-guide.md` | End-to-end workflows for consumers, freelancers, offices, and small fleets. |
| `references/troubleshooting.md` | Resolution steps for identity, payment, appointment, practical-test, and accessibility issues. |
| `references/test-scenarios.md` | Concrete validation scenarios for QA and acceptance tests. |
| `references/migration-checklist.md` | Migration checklist for replacing spreadsheets or old scripts. |
| `scripts/driving_license_booker_client.py` | Importable typed client implementation copy for script-based use. |
| `scripts/driving_license_booker_cli.py` | Command-line wrapper. |
| `scripts/examples/` | Runnable scenario scripts using environment variables and `--env sandbox|production`. |
| `src/driving_license_booker/` | Installable Python package used by `from driving_license_booker import ...`. |

## Test

```bash
python -m pytest -q --color=no
python -m compileall scripts/ -q
```

## Operating boundaries

Do not scrape protected portals, store passwords, auto-submit forms after CAPTCHA or identity verification, or charge a customer before official eligibility checks. Keep official receipts, confirmation numbers, and customer consent records with the business case file.
