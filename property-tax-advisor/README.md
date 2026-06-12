# Property Tax Advisor

A bilingual skill package for practical Israeli property-tax triage. It helps structure Arnona checks, Mas Rechush compensation questions, purchase-tax estimates, betterment-levy exposure, and common municipal-charge workflows for consumers, freelancers, and small businesses.

## Install for local use

```bash
cd property-tax-advisor
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

For Windows PowerShell:

```powershell
cd property-tax-advisor
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

List sample municipalities:

```bash
property-tax-advisor rates --municipalities --json-output
```

Create a local workflow case, extract its id, and use it in the next command:

```bash
CREATE_RESPONSE=$(property-tax-advisor case-create \
  --tax-type arnona \
  --subject "Tel Aviv Arnona bill has wrong area" \
  --taxpayer-type small_business \
  --env sandbox \
  --json-output)

CASE_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["case_id"])' <<< "$CREATE_RESPONSE")

property-tax-advisor case-next-steps \
  --case-id "$CASE_ID" \
  --tax-type arnona \
  --json-output
```

Estimate Arnona with sample rates:

```bash
property-tax-advisor arnona \
  --municipality tel-aviv \
  --area 80 \
  --zone A \
  --usage residential \
  --months 2 \
  --discount senior \
  --json-output
```

Estimate purchase tax with sample brackets:

```bash
property-tax-advisor purchase-tax \
  --price 2400000 \
  --buyer-profile additional_home \
  --contract-date 15/03/2026 \
  --json-output
```

Estimate betterment levy:

```bash
property-tax-advisor betterment-levy \
  --planning-uplift 300000 \
  --ownership-share 1 \
  --json-output
```

Route a Mas Rechush question:

```bash
property-tax-advisor mas-rechush \
  --property-kind apartment \
  --damage-type war_direct \
  --incident-date 15/03/2026 \
  --json-output
```

Run tests:

```bash
python -m pytest scripts/test_property_tax_advisor_client.py
```

## Python import

```python
from property_tax_advisor import calculate_arnona, estimate_purchase_tax

result = calculate_arnona({
    "municipality": "tel-aviv",
    "area_sqm": 80,
    "zone": "A",
    "usage": "residential",
    "months": 2,
})
print(result.to_dict())
```

## Runnable examples

Each example reads environment variables, accepts `--env sandbox|production`, and prints JSON using `json.dumps(..., ensure_ascii=False, indent=2)`.

```bash
python scripts/examples/freelancer_home_office.py --env sandbox
PTA_PRICE=3200000 python scripts/examples/purchase_tax_additional_home.py --env production
```


## Verification log

The final package includes `references/verification-log.md`, a two-pass live-source validation table covering official Israeli VAT, Arnona, Mas Rechush, purchase tax, betterment levy, declaration forms, CKAN API patterns, and webhook status.

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide with examples, decision trees, edge cases, troubleshooting, anti-patterns, and production checklist |
| `SKILL_HE.md` | Hebrew operating guide with Israeli professional terminology and localized examples |
| `references/api-reference.md` | Regulations, official services, structured helper request/response examples, and error tables |
| `references/workflow-guide.md` | End-to-end workflows for bills, appeals, freelancers, stores, transactions, betterment levy, and damage claims |
| `references/troubleshooting.md` | Diagnostic guide for common user problems |
| `references/test-scenarios.md` | Manual test and QA scenarios |
| `references/migration-checklist.md` | Migration checklist from older Arnona-only packages |
| `references/branding-audit.md` | Neutrality and public Markdown audit |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization correction log |
| `property_tax_advisor/client.py` | Typed synchronous and asynchronous helper implementation |
| `property_tax_advisor/cli.py` | Click-based installable CLI implementation |
| `scripts/property_tax_advisor_client.py` | Underscored compatibility import module |
| `scripts/property-tax-advisor-cli.py` | Script wrapper for the CLI |
| `scripts/test_property_tax_advisor_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenario scripts |
| `metadata.json` | Skill metadata without creator field |
| `CHANGELOG.md` | Keep-a-Changelog release notes |
| `LICENSE` | MIT license |
| `pyproject.toml` | Installable project metadata and tool configuration |
| `requirements-dev.txt` | Development and test dependencies |

## Important limitations

- Sample rates and brackets are illustrative.
- Official municipal Arnona orders and Israel Tax Authority publications control production calculations.
- High-value disputes, deadlines, litigation, exemptions, complex ownership, and property transactions require professional review.
