# Brand Reputation Monitor

Neutral Hebrew and mixed Hebrew-English brand reputation monitoring for permitted exports and local analysis. Use it for Israeli small businesses, freelancers, service providers, and consumer-facing teams that need practical sentiment, topic, risk, and response triage.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with chained configuration

Create a local monitor configuration, extract the returned `id`, and use that same `id` in the next step.

```bash
export BRM_BRAND_TERMS="המאפייה של דנה,Dana Bakery"
CREATE_RESPONSE=$(python -m brand_reputation_monitor.cli config-create --name "daily-monitor" --env sandbox --require-brand-match)
CONFIG_ID=$(python -c 'import json,sys; print(json.loads(sys.stdin.read())["id"])' <<< "$CREATE_RESPONSE")
python -m brand_reputation_monitor.cli analyze examples/comments.json --env sandbox --config-id "$CONFIG_ID"
```

Analyze one mention without a saved configuration:

```bash
python -m brand_reputation_monitor.cli single "המשלוח איחר אבל השירות היה אדיב" --env sandbox
```

Generate a report:

```bash
python -m brand_reputation_monitor.cli report data/comments.csv reputation-report.md --env sandbox
```

Use the package from Python:

```python
from brand_reputation_monitor import BrandReputationMonitor, Mention

monitor = BrandReputationMonitor()
result = monitor.analyze_mention(Mention(text="שירות מצוין, תודה רבה", source="facebook"))
print(result.sentiment.label)
```

## Input format

CSV requires a `text` column by default. Optional columns include:

```csv
date,source,brand,author,url,text,engagement,topic,branch
24/06/2026,facebook,המאפייה של דנה,@user,https://example/post,טעים אבל איחור רציני,15,delivery,תל אביב
```

JSON can be a list or an object with `mentions`:

```json
{
  "mentions": [
    {
      "date": "24/06/2026",
      "source": "x",
      "text": "לא מומלץ בכלל, חיוב כפול ולא עונים",
      "engagement": 19
    }
  ]
}
```

## Environment variables

| Variable | Purpose |
|---|---|
| `BRM_BRAND_TERMS` | Comma-separated brand terms used by examples and `config-create`. |
| `BRM_EXCLUDE_TERMS` | Comma-separated exclusions used by examples and `config-create`. |
| `BRM_CONFIG_DIR` | Optional directory for saved local monitor configurations. |
| `BRM_OUTPUT_DIR` | Optional output directory used by example scripts. |
| `BRM_INPUT_PATH` | Optional input path used by example scripts. |

## Run tests and syntax checks

```bash
pytest
python -m compileall scripts/ -q
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English usage guide, examples, decision trees, anti-patterns, troubleshooting, production checklist. |
| `SKILL_HE.md` | Hebrew guide with Israeli terminology, ₪, and DD/MM/YYYY localization. |
| `references/api-reference.md` | Israeli legal/regulatory map, source patterns, schemas, and error tables. |
| `references/workflow-guide.md` | End-to-end workflows. |
| `references/troubleshooting.md` | Debugging and tuning guidance. |
| `references/test-scenarios.md` | Concrete validation scenarios. |
| `references/migration-checklist.md` | Migration from spreadsheets, manual workflows, or legacy tooling. |

| `references/hebrew-qa-log.md` | Hebrew localization and terminology QA log. |
| `references/verification-log.md` | Two-pass web validation log with snippets, URLs, access dates, and package actions. |
| `brand_reputation_monitor/` | Installable Python package. |
| `scripts/brand_reputation_monitor_client.py` | Underscore client implementation mirror for script-based use. |
| `scripts/brand-reputation-monitor-cli.py` | Thin wrapper around the installable CLI. |
| `scripts/test_brand_reputation_monitor_client.py` | Pytest suite. |
| `scripts/examples/` | Runnable scenario scripts. |

## Safety notes

Use permitted data sources only. Do not scrape private areas, bypass platform controls, or send unsolicited marketing messages to people found through monitoring. Redact personal data before sharing reports. Escalate legal, safety, privacy, health, discrimination, media, and regulator-related mentions for human review.
