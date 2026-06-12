# Prescription Renewal Assistant

A neutral, web-validated prescription-renewal workflow package for Israel. It helps organize Kupat Cholim renewal requests, doctor or clinic messages, pharmacy pickup, delivery verification, privacy-safe caregiver support, and small-business logistics.

This package does not provide medical advice, diagnose, prescribe, change dosage, select substitutes, or guarantee renewal approval.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with chained case ID

Create a case, extract the generated ID, and use it in the next step:

```bash
CASE_ID="$(
  prescription-renewal-assistant create \
    --kupat-cholim Maccabi \
    --medication-name "as shown in portal" \
    --supply-days 5 \
    --repeats-left 0 \
    --valid-until 22-06-2026 \
    --preferred-fulfillment delivery \
    --pharmacy Super-Pharm \
    --consent-confirmed \
  | python -c 'import json,sys; print(json.load(sys.stdin)["case_id"])'
)"

prescription-renewal-assistant message --case-id "$CASE_ID" --language en
prescription-renewal-assistant checklist --case-id "$CASE_ID"
```

Equivalent script form:

```bash
python scripts/prescription-renewal-assistant-cli.py create \
  --kupat-cholim Clalit \
  --medication-name "as shown in portal" \
  --supply-days 2 \
  --repeats-left 0 \
  --consent-confirmed
```

## Development

```bash
pytest
python -m compileall scripts/ -q
```

## Examples

Each example reads environment variables and accepts `--env sandbox|production`:

```bash
PRA_DEFAULT_KUPAT_CHOLIM=Maccabi python scripts/examples/routine_refill.py --env sandbox
PRA_DEFAULT_PHARMACY=Super-Pharm python scripts/examples/urgent_no_repeats.py --env sandbox
```

Useful environment variables:
- `PRA_DEFAULT_KUPAT_CHOLIM`
- `PRA_DEFAULT_PHARMACY`
- `PRA_CASE_STORE`
- `PRA_API_BASE_URL`
- `PRA_API_TOKEN`

The examples do not submit prescription requests to providers. They create local workflow objects and print JSON.

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English guide with examples, decision trees, edge cases, anti-patterns, and checklist |
| `SKILL_HE.md` | Hebrew guide localized for Israel with ₪ and `DD/MM/YYYY` |
| `references/api-reference.md` | API-equivalent and regulatory reference |
| `references/workflow-guide.md` | End-to-end workflows |
| `references/troubleshooting.md` | Triage and issue resolution |
| `references/test-scenarios.md` | 30 concrete scenarios |
| `references/migration-checklist.md` | Migration checklist |
| `references/branding-audit.md` | Branding and logo audit |
| `references/hebrew-qa-log.md` | Hebrew QA log |
| `prescription_renewal_assistant/client.py` | Typed sync and async workflow helper |
| `prescription_renewal_assistant/cli.py` | Typer CLI implementation |
| `scripts/prescription-renewal-assistant-cli.py` | CLI wrapper |
| `scripts/test_prescription_renewal_assistant_client.py` | Pytest suite |
| `scripts/examples/` | Runnable examples |

## Privacy posture

Do not paste portal credentials, one-time codes, full ID numbers, diagnosis, payment-card details, or full prescription files into the tool.


## Web-validated corrections in v3

- Super-Pharm digital-prescription ordering remains supported with eligibility and delivery restrictions.
- Be must be verified in the current app or branch before assuming prescription delivery.
- Newpharm must be treated as a legacy/local reference unless a current licensed pharmacy confirms support.
- General Israeli VAT was verified as 18% in 2026, but the tool records receipt totals and does not calculate tax.
