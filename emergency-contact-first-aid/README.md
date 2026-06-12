# Emergency Contact and First-Aid Info

Local bilingual emergency contact and first-aid profile toolkit for Israeli small businesses, freelancers, households, and consumer-facing sites.

The toolkit stores data locally, validates emergency profiles, renders wallet cards, creates redacted public sheets, and provides scenario-based first-aid prompts that prioritize calling 101.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with chained profile id

Create a local sandbox profile and capture the response:

```bash
CREATE_RESPONSE=$(emergency-contact-first-aid create-profile \
  --profile-name "North Workshop" \
  --address "HaTaasiya 4, entrance A" \
  --locality "Haifa" \
  --contact-name "Noa Amir" \
  --contact-phone "050-111-2222" \
  --store-dir ./.ecfa-sandbox \
  --env sandbox)
```

Extract the id from the create response:

```bash
PROFILE_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")
```

Use the id in the next step:

```bash
emergency-contact-first-aid validate --profile-id "$PROFILE_ID" --store-dir ./.ecfa-sandbox --env sandbox
emergency-contact-first-aid wallet-card --profile-id "$PROFILE_ID" --store-dir ./.ecfa-sandbox --env sandbox
```

## Direct script usage

```bash
python scripts/emergency_contact_first_aid_client.py validate templates/emergency-profile.example.json
python scripts/emergency_contact_first_aid_client.py triage --scenario stroke
python scripts/emergency_contact_first_aid_cli.py numbers
```

## Python usage

```python
from emergency_contact_first_aid import EmergencyInfoClient

client = EmergencyInfoClient()
profile = client.load_profile("templates/emergency-profile.example.json")
result = client.validate_profile(profile)
print(result.to_mapping())
```

## Tests and syntax checks

```bash
python -m pytest scripts/test_emergency_contact_first_aid_client.py -q
python -m compileall scripts/ -q
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operational guide |
| `SKILL_HE.md` | Hebrew operational guide |
| `references/api-reference.md` | Data contract, local command reference, Israeli regulatory checklist |
| `references/workflow-guide.md` | End-to-end workflows |
| `references/troubleshooting.md` | Validation, operations, privacy, and CLI troubleshooting |
| `references/test-scenarios.md` | More than 20 concrete drill scenarios |
| `references/migration-checklist.md` | Migration from paper, spreadsheets, and messages |
| `references/branding-audit.md` | Branding, logo, badge, and attribution audit |
| `references/hebrew-qa-log.md` | Hebrew quality correction log |
| `references/verification-log.md` | Two-pass web validation log with source snippets |
| `src/emergency_contact_first_aid/` | Installable Python module |
| `scripts/emergency_contact_first_aid_client.py` | Structured CLI helper |
| `scripts/emergency_contact_first_aid_cli.py` | Typer CLI wrapper |
| `scripts/examples/` | Runnable scenario scripts |
| `templates/` | Example profile and print templates |
| `schemas/emergency-profile.schema.json` | JSON Schema |


## Web validation

The v3 package includes `references/verification-log.md`, which records two-pass validation for emergency numbers, MDA first-aid guidance, United Hatzalah 1221, privacy/accessibility references, and the non-operational VAT check requested during review.
