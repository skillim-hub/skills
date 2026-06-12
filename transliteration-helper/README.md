# Transliteration Helper

Local Hebrew-to-Latin transliteration helper for Israeli passport-aware names, built for small businesses, freelancers, consumers, and operations teams that need consistent customer-name handling.

## What it does

- Transliterates Hebrew personal names to Latin script.
- Uses common Israeli name overrides for stronger unpointed Hebrew output.
- Supports pointed Hebrew when available in source data.
- Emits warning codes for ambiguous input instead of silently hiding risk.
- Provides a typed synchronous/asynchronous Python client.
- Provides a Click-based CLI for single names, batch files, validation, and local record storage.
- Includes examples, workflows, troubleshooting, migration guidance, and tests.

## Install for local development

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

The helper runs locally. No remote service or government API is required. The CLI depends on `click`; tests depend on `pytest` and `pytest-asyncio`.

## Quick start

Single name:

```bash
python scripts/transliteration-helper-cli.py transliterate "דוד כהן"
```

JSON with rule trace:

```bash
python scripts/transliteration-helper-cli.py transliterate --format json --explain "בן־דוד"
```

Create a local review record, extract its `id`, then use that `id` in the next step:

```bash
CREATE_RESPONSE=$(python scripts/transliteration-helper-cli.py create \
  --store ./tmp/transliteration-records.jsonl \
  "שרה לוי")

RECORD_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")

python scripts/transliteration-helper-cli.py show \
  --store ./tmp/transliteration-records.jsonl \
  "$RECORD_ID"
```

Batch text file:

```bash
python scripts/transliteration-helper-cli.py batch -i names.txt --format text
```

Batch CSV file:

```bash
python scripts/transliteration-helper-cli.py batch \
  -i customers.csv \
  --input-column hebrew_name \
  --format csv \
  -o customers_latin.csv
```

## Python usage

Install the package with `pip install -e .`, then import the module directly.

```python
from transliteration_helper_client import TransliterationClient

client = TransliterationClient()
result = client.transliterate("שרה לוי", output_case="title")
print(result.latin)
```

Async:

```python
import asyncio
from transliteration_helper_client import TransliterationClient

async def main():
    client = TransliterationClient()
    result = await client.transliterate_async("משה כהן")
    print(result.to_json())

asyncio.run(main())
```

Local record storage:

```python
from transliteration_helper_client import TransliterationClient

client = TransliterationClient()
created = client.create_record("דוד כהן", store_path="./tmp/records.jsonl")
loaded = client.get_record(created["id"], "./tmp/records.jsonl")
print(loaded["result"]["latin"])
```


## Official-source boundary

Use the helper as a local data-quality tool, not as an official spelling authority. Israeli travel-document rules permit several bases for Latin spelling, including simple Hebrew-to-Latin transliteration rules, established Latin spelling tradition, phonetic preservation, and accepted spelling in the applicant's country of birth or residence. Preserve an existing passport, bank, contract, or customer-confirmed legal spelling exactly.

The current verification log is in `references/verification-log.md`.

## Run tests

```bash
pytest
python -m compileall scripts/ -q
```

## File index

| File | Purpose |
|---|---|
| `SKILL.md` | English operating guide |
| `SKILL_HE.md` | Hebrew operating guide |
| `references/api-reference.md` | Local interface, schemas, warnings, errors, and standards context |
| `references/workflow-guide.md` | End-to-end operational workflows |
| `references/troubleshooting.md` | Warning and failure resolution |
| `references/test-scenarios.md` | QA scenarios and manual review samples |
| `references/migration-checklist.md` | Migration and rollout checklist |
| `references/branding-audit.md` | Neutrality audit report |
| `references/hebrew-qa-log.md` | Hebrew quality-assurance log |
| `references/verification-log.md` | Web validation log |
| `scripts/transliteration_helper_client.py` | Typed sync/async client and local record helpers |
| `scripts/transliteration_helper_cli.py` | Importable CLI implementation |
| `scripts/transliteration-helper-cli.py` | Executable CLI wrapper |
| `scripts/test_transliteration_helper_client.py` | pytest suite |
| `scripts/examples/` | Runnable scenarios |
| `metadata.json` | Skill metadata |
| `CHANGELOG.md` | Version history |
| `LICENSE` | MIT license |
| `pyproject.toml` | Install and test configuration |
| `requirements-dev.txt` | Development dependencies |

## Privacy and review

Process data locally. Do not treat generated spelling as an official legal spelling when a passport, bank record, signed contract, or government document is available. Preserve official spelling exactly and store a source label.
