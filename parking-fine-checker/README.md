# Parking Fine Checker

A neutral skill package for checking, organizing, disputing, and preparing payment for Israeli parking, traffic, and toll fines.

The package is useful for small businesses, freelancers, consumers, fleet administrators, office managers, and finance teams that need a repeatable process for municipal fines, police traffic tickets, Road 6 and other toll-road notices, leasing-company fine charges, and collection letters.

## What is included

```text
SKILL.md                                  English operating guide
SKILL_HE.md                               Hebrew operating guide
references/api-reference.md               Official-channel and integration reference
references/workflow-guide.md              End-to-end workflows
references/troubleshooting.md             Troubleshooting guide
references/test-scenarios.md              20+ concrete validation scenarios
references/migration-checklist.md         Migration checklist
references/branding-audit.md              Branding, author, logo, badge, and emoji audit
references/hebrew-qa-log.md               Hebrew quality-assurance log
parking_fine_checker/client.py            Installable typed sync and async client
parking_fine_checker/cli.py               Installable Typer CLI
scripts/parking_fine_checker_client.py    Compatibility import
scripts/parking-fine-checker-cli.py       CLI wrapper
scripts/test_parking_fine_checker_client.py Pytest suite
scripts/examples/                         Runnable examples
metadata.json                             Skill metadata
CHANGELOG.md                              Keep a Changelog history
LICENSE                                   MIT license
pyproject.toml                            Python project config
requirements-dev.txt                      Development dependencies
```

## Install for local testing

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

Run the test suite:

```bash
pytest -q
```

Confirm imports work without path changes:

```bash
python - <<'PY'
from parking_fine_checker import ParkingFineClient, FineLookupRequest
print(ParkingFineClient, FineLookupRequest)
PY
```

## Environment variables

Examples and the CLI support `--env sandbox|production`.

```bash
export PARKING_FINE_BASE_URL_SANDBOX="mock://local"
export PARKING_FINE_BASE_URL_PRODUCTION="https://authorized-middleware.example/api"
export PARKING_FINE_TOKEN_SANDBOX=""
export PARKING_FINE_TOKEN_PRODUCTION="replace-with-token"
export PARKING_FINE_VEHICLE_NUMBER="12-345-67"
export PARKING_FINE_NOTICE_NUMBER="1001"
export PARKING_FINE_ISSUER_TYPE="municipality"
export PARKING_FINE_ISSUER_NAME="Example Municipality"
```

## Quick start with chained case ID

Create a case, extract the returned `case_id`, then pass that ID into the next command.

```bash
CREATE_RESPONSE="$(parking-fine-checker create \
  --env sandbox \
  --issuer-type municipality \
  --issuer-name "Example Municipality" \
  --vehicle-number "12-345-67" \
  --notice-number "1001" \
  --amount-ils 250.00 \
  --notice-date 10/03/2026 \
  --due-date 08/06/2026)"

CASE_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["case_id"])' <<< "$CREATE_RESPONSE")"

parking-fine-checker lookup \
  --env sandbox \
  --case-id "$CASE_ID" \
  --issuer-type municipality \
  --issuer-name "Example Municipality" \
  --vehicle-number "12-345-67" \
  --notice-number "1001"

parking-fine-checker checklist \
  --case-id "$CASE_ID" \
  --issuer-type municipality \
  --status verified_unpaid \
  --business-vehicle
```

## Python quick start

```python
from parking_fine_checker import FineLookupRequest, ParkingFineClient

api = ParkingFineClient(base_url="mock://local")
case = api.create_case(
    issuer_type="municipality",
    issuer_name="Example Municipality",
    vehicle_number="12-345-67",
    notice_number="1001",
    amount_ils="250.00",
    notice_date="10/03/2026",
    due_date="08/06/2026",
)
result = api.lookup_fine(
    FineLookupRequest(
        case_id=case.case_id,
        issuer_type="municipality",
        issuer_name="Example Municipality",
        vehicle_number="12-345-67",
        notice_number="1001",
    )
)
print(result.to_dict())
```

## Safety boundaries

- Use official portals and authorized integrations only.
- Do not scrape or bypass CAPTCHA.
- Do not store payment card numbers.
- Do not submit false driver declarations.
- Do not automatically pay fines without human approval.
- Redact identity numbers in logs and internal notes.

## Common statuses

- `new`
- `lookup_not_found`
- `verified_unpaid`
- `verified_paid`
- `contest_candidate`
- `appeal_submitted`
- `liability_transfer_requested`
- `approved_for_payment`
- `paid`
- `cancelled`
- `collection`
- `closed`

## Hebrew localization

The Hebrew guide uses Israeli professional terminology, `₪` currency formatting, and `DD/MM/YYYY` display dates. The scripts store dates internally as ISO `YYYY-MM-DD`.


## Web validation status

Version 2.2.0 adds a two-pass live-source verification log at `references/verification-log.md`.

Key corrections:

- The Israeli VAT rate is documented as 18% from 01/01/2025 and remains the current rate in the official 2026-facing sources checked.
- Official channels are primarily portals and web forms; no universal public JSON API or official webhook event names were confirmed.
- Middleware endpoint paths in `references/api-reference.md` are examples for authorized internal integrations, not official Israeli public endpoints.
- Municipal and toll-road deadlines are source-specific; verify the current issuer notice before relying on a deadline.
