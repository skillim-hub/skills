# Migration Checklist

Use this checklist when moving from an earlier package version or from ad-hoc search notes.

## Files and imports

- Replace any hyphenated Python client file with the underscored importable module.
- Use `from real_estate_search import RealEstateSearchClient, SearchCriteria` after installation.
- Keep direct CLI use through `real-estate-search` or `scripts/real-estate-search-cli.py`.
- Remove local path hacks from examples and notebooks.
- Install the package with `pip install -e .`.

## Command changes

Old ad-hoc pattern:

```bash
python scripts/real-estate-search-client.py --city "חיפה"
```

Current pattern:

```bash
real-estate-search create --city "חיפה" --deal-type rent --output plan.json
PLAN_ID=$(python -c "import json; print(json.load(open('plan.json', encoding='utf-8'))['plan_id'])")
real-estate-search show --file plan.json --plan-id "$PLAN_ID"
```

## Data changes

- Store `deal_type` as one of `rent`, `sale`, `commercial_rent`, or `commercial_sale`.
- Store dates as `YYYY-MM-DD` internally; accept `DD/MM/YYYY` and `DD-MM-YYYY` from Israeli users.
- Store neighborhoods as a list or comma-separated string.
- Store source names as `yad2`, `madlan`, and `komo`.
- Add `plan_id` to every saved search response.

## Documentation changes

- Use `SKILL.md` for English operating guidance.
- Use `SKILL_HE.md` for Hebrew guidance.
- Use `references/api-reference.md` for schema and source behavior.
- Use `references/workflow-guide.md` for end-to-end cases.
- Use `references/troubleshooting.md` before changing code.
- Use `references/test-scenarios.md` when adding or changing features.

## Quality gates

Run these commands before packaging:

```bash
pip install -e .
pip install -r requirements-dev.txt
pytest
python -m compileall scripts/ -q
```

## Behavior changes

- Generated links are treated as manual-review helpers, not private APIs. For Komo, migrate any old `/search` links to verified city-page patterns under `/code/nadlan/`.
- Commercial searches require permitted-use, municipal classification, VAT, and licensing checks.
- Purchase workflows require official rights and planning verification.
- Rental workflows include first-month cash and recurring monthly cost checks.
- Examples read environment variables and preserve Hebrew in JSON output.
