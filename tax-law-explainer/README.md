# Tax-Law Explainer

Practical bilingual skill package for explaining common Israeli tax-law situations for small businesses, freelancers, and consumers. The package covers recurring questions under the Israeli Income Tax Ordinance, VAT Law, and Real Estate Taxation Law, with decision trees, examples, CLI helpers, test scenarios, and troubleshooting references.

The material is educational and operational. Verify amounts, dates, thresholds, forms, and filing duties against current Israel Tax Authority publications, professional advisers, and the exact statutory text before making a filing or signing a transaction.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Run the CLI in sandbox mode:

```bash
python scripts/tax-law-explainer-cli.py explain \
  --topic vat-registration \
  --business-type freelancer \
  --annual-turnover 120000 \
  --profession "graphic designer" \
  --facts-json '{"activity_type":"design","start_date":"02/06/2026"}' \
  --env sandbox \
  --json
```

Run a workflow checklist:

```bash
python scripts/tax-law-explainer-cli.py checklist \
  --workflow freelancer-onboarding \
  --env sandbox \
  --json
```

Use the installable module and chain the identifier from the create-style response into the next step:

```python
from tax_law_explainer import TaxLawExplainerClient

client = TaxLawExplainerClient()
created = client.explain(
    "vat-registration",
    user_type="freelancer",
    facts={
        "activity_type": "design",
        "profession": "graphic designer",
        "annual_turnover": 120000,
        "start_date": "02/06/2026",
    },
)
created_id = created.topic
next_step = client.checklist("freelancer-onboarding")
print(created_id)
print(next_step["steps"][0])
print(client.reference_values()["standard_vat_rate_percent"])
```

For external systems, store `topic`, `language`, and the fact payload together as the scenario identifier.

Run tests:

```bash
pytest scripts/test_tax_law_explainer_client.py -q
python -m compileall scripts/ -q
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide, examples, decision trees, anti-patterns, checklist |
| `SKILL_HE.md` | Hebrew operating guide with Israeli terminology and ₪/DD/MM/YYYY localization |
| `references/api-reference.md` | Statutory and portal reference, structured request/response examples, error table |
| `references/workflow-guide.md` | End-to-end workflows for freelancers, VAT, withholding, property, audits |
| `references/troubleshooting.md` | Diagnostic playbooks for common tax-law explainer failures |
| `references/test-scenarios.md` | More than 20 scenario prompts with expected handling |
| `references/migration-checklist.md` | Migration checklist for older neutral or branded skill packages |
| `references/branding-audit.md` | Branding, author, logo, badge, and emoji audit |
| `references/hebrew-qa-log.md` | Hebrew localization and terminology QA log |
| `references/verification-log.md` | Two-pass web validation log with source snippets |
| `tax_law_explainer/` | Installable Python package |
| `scripts/tax_law_explainer_client.py` | Compatibility wrapper for direct script users |
| `scripts/tax-law-explainer-cli.py` | Typer-based command-line interface |
| `scripts/examples/` | Runnable example scripts |
| `scripts/test_tax_law_explainer_client.py` | Pytest suite |
| `pyproject.toml` | Project packaging and tool configuration |
| `requirements-dev.txt` | Development dependencies |
| `CHANGELOG.md` | Keep a Changelog format |
| `LICENSE` | MIT license |

## Development

```bash
pip install -e .
pip install -r requirements-dev.txt
pytest -q
python scripts/examples/scenario_01_freelancer_vat.py --env sandbox
```

## Content principles

Use neutral, imperative language. Present decision support, not legal representation. Separate facts supplied by the user from assumptions. Flag missing data, deadlines, documentation gaps, and situations that require a certified public accountant, tax adviser, attorney, or official ruling.
