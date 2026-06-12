# Lease Agreement Drafter

A neutral package for drafting and auditing Israeli apartment and office lease agreement drafts. The package includes bilingual skill instructions, legal-reference notes, workflows, troubleshooting, tests, examples, and an installable Python module.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a draft and save the Markdown file:

```bash
CREATE_RESPONSE=$(lease-agreement-drafter draft \
  --env sandbox \
  --input scripts/examples/apartment_standard_input.json \
  --output draft.md)

DRAFT_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")

lease-agreement-drafter audit \
  --env sandbox \
  --draft-id "$DRAFT_ID" \
  --input draft.md
```

Use the module directly:

```python
from lease_agreement_drafter import LeaseAgreementDrafterClient

client = LeaseAgreementDrafterClient.from_env(environment="sandbox")
result = client.draft({
    "landlord": {"name": "דנה כהן"},
    "tenant": {"name": "נועם לוי"},
    "property": {"property_type": "apartment", "address": "הרצל 10", "city": "חיפה"},
    "terms": {"start_date": "01/08/2026", "end_date": "31/07/2027", "monthly_rent_ils": 5200, "security_deposit_ils": 10400},
    "language": "he",
})
print(result.id)
```

## Environment variables

| Variable | Purpose |
| --- | --- |
| `LEASE_DRAFTER_ENV` | `sandbox` or `production` |
| `LEASE_DRAFTER_API_KEY` | Optional token for deployments that wrap the local module behind a service |
| `LEASE_DRAFTER_LOCALE` | Defaults to `he-IL` |

## File index

| Path | Purpose |
| --- | --- |
| `SKILL.md` | English operating guide |
| `SKILL_HE.md` | Hebrew operating guide |
| `references/api-reference.md` | Local API, CLI, regulation, request, response, and error reference |
| `references/workflow-guide.md` | End-to-end drafting workflows |
| `references/troubleshooting.md` | Common problems and fixes |
| `references/test-scenarios.md` | More than 20 concrete validation scenarios |
| `references/migration-checklist.md` | Migration from earlier package layouts |
| `references/branding-audit.md` | Branding, authorship, brand image, and public Markdown audit |
| `references/hebrew-qa-log.md` | Hebrew localization and terminology review log |
| `lease_agreement_drafter/` | Installable Python package |
| `scripts/` | Wrappers, examples, and pytest suite |

## Development checks

```bash
pytest -q
python -m compileall scripts/ -q
```

## Legal and tax caution

Verify the current version of Israeli law and the specific facts before signing. Escalate protected tenancy, luxury apartment, planning, tax, accessibility, eviction, insolvency, or cross-border issues for professional review.
