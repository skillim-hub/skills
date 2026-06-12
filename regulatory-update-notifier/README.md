# Regulatory Update Notifier

Neutral skill package for monitoring and summarizing Israeli legal and regulatory changes relevant to small businesses, freelancers, consumers, and industry-specific operations.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with chained profile id

Create sandbox source configuration:

```bash
python -m regulatory_update_notifier.cli make-config sources.json --env sandbox
```

Create a monitoring profile and save the response:

```bash
CREATE_RESPONSE=$(python -m regulatory_update_notifier.cli create-profile \
  --name "Online shop" \
  --industry ecommerce \
  --keyword "cancellation" \
  --output profile.json \
  --env sandbox)
```

Extract the id from the create response:

```bash
PROFILE_ID=$(printf '%s' "$CREATE_RESPONSE" | python -c 'import json,sys; print(json.load(sys.stdin)["id"])')
```

Use the extracted id in the next step:

```bash
python -m regulatory_update_notifier.cli scan \
  --config sources.json \
  --profile profile.json \
  --profile-id "$PROFILE_ID" \
  --env sandbox \
  --output updates.json
```

Build a Hebrew digest:

```bash
python -m regulatory_update_notifier.cli digest \
  --input updates.json \
  --locale he \
  --output digest.md
```

Run tests:

```bash
pytest -q
python -m compileall scripts/ -q
```

## Python quick start

```python
from regulatory_update_notifier import RegulatoryMonitorClient, create_profile, default_sources

profile = create_profile(
    name="חנות מקוונת",
    industries=["ecommerce"],
    keywords=["ביטול עסקה"],
    locale="he",
    environment="sandbox",
)

updates = RegulatoryMonitorClient(default_sources("sandbox")).collect_updates(profile=profile)
for update in updates:
    print(update.title, update.score)
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide |
| `SKILL_HE.md` | Hebrew operating guide with Israeli localization |
| `references/api-reference.md` | Israeli source and endpoint reference |
| `references/verification-log.md` | Two-pass web validation for official sources, rates, thresholds, endpoint paths, and terminology |
| `references/workflow-guide.md` | End-to-end workflow examples |
| `references/troubleshooting.md` | Failure modes and fixes |
| `references/test-scenarios.md` | Validation scenarios |
| `references/migration-checklist.md` | Migration checklist for older workflows |
| `references/branding-audit.md` | Branding, attribution, visual asset, and emoji audit report |
| `references/hebrew-qa-log.md` | Hebrew quality review log |
| `regulatory_update_notifier/` | Installable Python package |
| `scripts/regulatory_update_notifier_client.py` | Underscored client implementation mirror |
| `scripts/regulatory-update-notifier-cli.py` | CLI wrapper |
| `scripts/regulatory_update_notifier_cli.py` | Underscored CLI wrapper |
| `scripts/test_regulatory_update_notifier_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenario scripts |
| `metadata.json` | Skill metadata |
| `CHANGELOG.md` | Keep-a-Changelog release notes |
| `LICENSE` | MIT license |
| `pyproject.toml` | Project metadata and dependencies |
| `requirements-dev.txt` | Test and development dependencies |

## Source configuration format

```json
{
  "environment": "sandbox",
  "sources": [
    {
      "name": "Consumer Protection publications",
      "url": "https://www.gov.il/he/departments/consumer_protection_and_fair_trade_authority",
      "source_type": "html",
      "regulator": "Consumer Protection and Fair Trade Authority",
      "tags": ["consumer", "ecommerce"],
      "industries": ["ecommerce", "retail", "consumers"]
    }
  ]
}
```

## Safety and review

Do not treat generated summaries as formal legal advice. Use manual review for critical alerts, unclear legal status, tax positions, penalties, licensing, employment disputes, privacy incidents, and regulated finance or healthcare matters.


## Source validation

Before production use, review `references/verification-log.md`. Recheck VAT, Israel Invoice thresholds, official forms, endpoint paths, and authority terminology against live official sources when the output will affect tax, legal, employment, privacy, or consumer-compliance decisions.
