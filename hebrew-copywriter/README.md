# Hebrew Copywriter enhanced package

Neutral bilingual skill package for writing Hebrew marketing copy for Israeli audiences. Includes English and Hebrew guides, Israeli reference material, workflows, troubleshooting, tests, a typed client, a CLI, and runnable examples.

## What it does

- Generates structured Hebrew copy for small businesses, freelancers, מסחר מקוון, local services, and consumer campaigns.
- Helps choose Israeli register, gender form, and channel format.
- Adds practical checks for prices, VAT, DD/MM/YYYY dates, direct marketing consent, privacy microcopy, accessibility, and regulated claims.
- Provides deterministic helper scripts for briefs, prompts, validation, and simple copy drafts.

## File index

```text
SKILL.md
SKILL_HE.md
metadata.json
README.md
CHANGELOG.md
LICENSE
pyproject.toml
requirements-dev.txt
hebrew_copywriter/
  __init__.py
  client.py
hebrew_copywriter_cli.py
references/
  api-reference.md
  branding-audit.md
  hebrew-grammar-quick-ref.md
  hebrew-qa-log.md
  migration-checklist.md
  test-scenarios.md
  troubleshooting.md
  verification-log.md
  workflow-guide.md
scripts/
  __init__.py
  hebrew-copywriter-cli.py
  hebrew_copywriter_cli.py
  hebrew_copywriter_client.py
  test_hebrew_copywriter_client.py
  examples/
    b2c_sale.py
    מסחר מקוון_product.py
    freelancer_quote.py
    retention_sms.py
    service_launch.py
```

## Install for local testing

```bash
cd hebrew-copywriter
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Run tests

```bash
python -m pytest scripts -q
python -m compileall scripts/ -q
```

## Quick start with saved brief id

Create a brief, extract the id from the JSON response, then use that id in the next command.

```bash
CREATE_RESPONSE=$(python scripts/hebrew-copywriter-cli.py create-brief \
  --business-name "סטודיו נועה" \
  --business-type "פילאטיס" \
  --offer "קבוצת בוקר קטנה" \
  --audience "נשים אחרי לידה" \
  --channel whatsapp \
  --gender feminine \
  --price 220 \
  --include-vat \
  --include-unsubscribe)

BRIEF_ID=$(python -c 'import json,sys; print(json.loads(sys.stdin.read())["id"])' <<< "$CREATE_RESPONSE")

python scripts/hebrew-copywriter-cli.py generate-id "$BRIEF_ID"
```

## Other CLI commands

```bash
python scripts/hebrew-copywriter-cli.py brief-template
```

```bash
python scripts/hebrew-copywriter-cli.py quick \
  --business-name "סטודיו נועה" \
  --business-type "פילאטיס" \
  --offer "קבוצת בוקר קטנה" \
  --audience "נשים אחרי לידה" \
  --channel whatsapp \
  --gender feminine \
  --price 220 \
  --include-vat \
  --include-unsubscribe
```

```bash
python scripts/hebrew-copywriter-cli.py prompt brief.json
```

```bash
python scripts/hebrew-copywriter-cli.py check "מבצע מטורף ללא אפשרות הסרה"
```

## Python client quick start

```python
from hebrew_copywriter import (
    Channel,
    CopyBrief,
    GenderMode,
    HebrewCopywriterClient,
)

brief = CopyBrief(
    business_name="סטודיו נועה",
    business_type="פילאטיס",
    offer="קבוצת בוקר קטנה",
    audience="נשים אחרי לידה",
    channel=Channel.INSTAGRAM,
    gender_mode=GenderMode.FEMININE,
    proof_points=["עד 8 משתתפות", "מדריכה מוסמכת"],
)

client = HebrewCopywriterClient()
print(client.generate_copy(brief)["headline"])
```

## Runnable examples

Each example accepts `--env sandbox|production`, reads optional environment variables, and prints JSON with `ensure_ascii=False`.

```bash
HEBREW_COPYWRITER_BUSINESS_NAME="סטודיו נועה" python scripts/examples/service_launch.py --env sandbox
```

## Production note

The package provides copywriting support and compliance prompts, not legal, accounting, tax, medical, or financial advice. Verify current legal requirements, VAT rates, public datasets, platform rules, and sector-specific regulations before publication.
