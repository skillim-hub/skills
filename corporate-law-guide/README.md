# Corporate-Law Guide

A neutral, bilingual skill package for practical Israeli corporate-law workflows. It supports small businesses, freelancers, consumers, founders, shareholders, and directors who need structured guidance on company formation, governance, shareholder agreements, Companies Authority procedures, and corporate recordkeeping.

## Important notice

This package provides general information and workflow support. It is not legal advice and does not replace an Israeli lawyer, CPA, tax adviser, or official regulator guidance. Verify current forms, fees, authentication requirements, and filing channels before submission.

## Install

```bash
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

## Quick start with chained case ID

Create a case, extract the `case_id`, and use it in the next command:

```bash
CASE_ID="$(
  python scripts/corporate-law-guide-cli.py --env sandbox create-case \
    --owners 2 \
    --activity "software platform" \
  | python -c 'import json,sys; print(json.load(sys.stdin)["case_id"])'
)"

python scripts/corporate-law-guide-cli.py --env sandbox case-checklist \
  --case-id "$CASE_ID" \
  --action incorporation \
  --owners 2 \
  --activity "software platform"
```

The installed console command works after `pip install -e .`:

```bash
corporate-law-guide --env sandbox classify \
  --owners 2 \
  --liability-risk high \
  --fundraising yes \
  --activity "software platform"
```

## Python quick start

```python
from corporate_law_guide import CorporateLawGuideClient

client = CorporateLawGuideClient(environment="sandbox")
case = client.create_case(
    business_activity="software platform",
    owners_count=2,
)
checklist = client.build_incorporation_checklist(
    owners_count=2,
    business_activity="software platform",
    case_id=case.case_id,
)
print(checklist.to_json())
```

## File index

```text
SKILL.md                                      English operational guide
SKILL_HE.md                                   Hebrew operational guide
references/api-reference.md                   Israeli regulatory and workflow reference
references/workflow-guide.md                  End-to-end workflows
references/troubleshooting.md                 Troubleshooting playbook
references/test-scenarios.md                  Concrete test scenarios
references/migration-checklist.md             Upgrade and records migration checklist
references/branding-audit.md                  Neutrality and visual-asset audit
references/hebrew-qa-log.md                   Hebrew quality-assurance log
references/verification-log.md                Web validation and skeptical re-validation log
corporate_law_guide/                          Installable Python package
scripts/corporate_law_guide_client.py         Typed sync and async helper client
scripts/corporate-law-guide-cli.py            CLI helper
scripts/test_corporate_law_guide_client.py    Pytest suite
scripts/examples/                             Runnable scenario examples
metadata.json                                 Skill metadata
CHANGELOG.md                                  Keep a Changelog release notes
LICENSE                                       MIT license
pyproject.toml                                Python project configuration
requirements-dev.txt                          Development requirements
```

## CLI examples

Classify entity structure:

```bash
python scripts/corporate-law-guide-cli.py --env sandbox classify \
  --owners 2 \
  --liability-risk high \
  --fundraising yes \
  --regulated no \
  --activity "B2B SaaS"
```

Generate annual-report checklist:

```bash
python scripts/corporate-law-guide-cli.py --env sandbox annual-report \
  --company-number 516000000 \
  --year 2026 \
  --has-changes yes
```

Validate company number:

```bash
python scripts/corporate-law-guide-cli.py --env sandbox validate-company-number 516000000
```

Generate incorporation checklist:

```bash
python scripts/corporate-law-guide-cli.py --env sandbox checklist incorporation \
  --owners 2 \
  --activity "consumer ecommerce"
```

## Development

```bash
python -m pip install -e .
python -m pip install -r requirements-dev.txt
pytest
python -m compileall scripts/ -q
```

The client uses only the Python standard library. The CLI uses argparse and is also exposed as an installed console command.

## Localization

- English guide: `SKILL.md`
- Hebrew guide: `SKILL_HE.md`
- Israeli dates: `DD/MM/YYYY`
- Currency: `₪`
- Official terms: רשות התאגידים, רשם החברות, תקנון, מרשם בעלי מניות, דירקטוריון

