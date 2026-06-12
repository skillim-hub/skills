# Insurance Coverage Analyzer

Analyze and compare Israeli health, home, and life insurance policies at policy level. Use the package for local structured workflows, a Typer CLI, a typed sync and async client, pytest validation, and runnable scenario scripts.

The tool helps Israeli consumers, freelancers, and small businesses compare policy terms, not only premium. It flags gaps, duplicates, exclusions, waiting periods, deductibles, mortgage assignment, beneficiary issues, and renewal negotiation actions.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

Run tests:

```bash
pytest
python -m compileall scripts/ -q
```

## Quick start

Create `policies.json`:

```json
{
  "profile": {
    "segment": "consumer",
    "supplementary_health_plan": "unknown"
  },
  "policies": [
    {
      "policy_id": "health-a",
      "policy_type": "health",
      "insurer": "Insurer A",
      "premium_monthly_nis": 180,
      "coverages": {
        "private_surgery_israel": {"covered": true, "limit_nis": 1000000, "deductible_nis": 0},
        "drugs_outside_basket": {"covered": true, "limit_nis": 2000000}
      },
      "exclusions": ["left knee condition"],
      "waiting_period_days": 90
    },
    {
      "policy_id": "health-b",
      "policy_type": "health",
      "insurer": "Insurer B",
      "premium_monthly_nis": 145,
      "coverages": {
        "private_surgery_israel": {"covered": true, "limit_nis": 750000, "deductible_nis": 500}
      },
      "waiting_period_days": 120
    }
  ]
}
```

Create a saved analysis record, extract the identifier from the create response, then use it in the next command:

```bash
CREATE_RESPONSE="$(insurance-coverage-analyzer create policies.json --store-dir .ica_runs)"
echo "$CREATE_RESPONSE"
ANALYSIS_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["analysis_id"])' <<< "$CREATE_RESPONSE")"
insurance-coverage-analyzer show "$ANALYSIS_ID" --store-dir .ica_runs --format markdown
```

Direct comparison without saving:

```bash
insurance-coverage-analyzer compare policies.json --format markdown
insurance-coverage-analyzer compare policies.json --format json
insurance-coverage-analyzer compare policies.json --format markdown --locale he-IL
```

## Python usage

```python
from insurance_coverage_analyzer import InsuranceCoverageAnalyzer

policies = [
    {"policy_id": "life-a", "policy_type": "life", "premium_monthly_nis": 95,
     "coverages": {"death_benefit": {"covered": True, "limit_nis": 1000000}, "beneficiaries": True}},
    {"policy_id": "life-b", "policy_type": "life", "premium_monthly_nis": 130,
     "coverages": {"death_benefit": {"covered": True, "limit_nis": 750000}, "beneficiaries": True}},
]

result = InsuranceCoverageAnalyzer().compare(policies)
print(result.to_markdown())
```

## CLI commands

```bash
insurance-coverage-analyzer validate policies.json
insurance-coverage-analyzer compare policies.json --format json
insurance-coverage-analyzer compare policies.json --format markdown --locale he-IL
insurance-coverage-analyzer create policies.json --store-dir .ica_runs
insurance-coverage-analyzer show ica-example123 --store-dir .ica_runs --format markdown
insurance-coverage-analyzer duplicates policies.json
insurance-coverage-analyzer checklist --policy-type health
insurance-coverage-analyzer sample --output sample.json
```

The script wrapper remains available after installation:

```bash
python scripts/insurance-coverage-analyzer-cli.py sample --output sample.json
python scripts/insurance-coverage-analyzer-cli.py compare sample.json --format markdown
```

## Scenario examples

Each example reads environment variables, accepts `--env sandbox|production`, and prints JSON with `ensure_ascii=False` and indentation.

```bash
ICA_LOCALE=he-IL python scripts/examples/compare_health_family.py --env sandbox
ICA_MORTGAGE_STRUCTURE_NIS=1250000 python scripts/examples/compare_home_mortgage.py --env production
ICA_DEPENDENTS=3 python scripts/examples/compare_life_freelancer.py --env sandbox
python scripts/examples/duplicate_coverages.py --env sandbox
ICA_CURRENT_PREMIUM=120 ICA_RENEWAL_PREMIUM=150 python scripts/examples/renewal_negotiation.py --env production
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English guide |
| `SKILL_HE.md` | Hebrew guide |
| `insurance_coverage_analyzer/` | Installable Python package |
| `insurance_coverage_analyzer/client.py` | Typed sync and async analyzer |
| `insurance_coverage_analyzer/cli.py` | Typer CLI implementation |
| `references/api-reference.md` | Israeli regulatory and structured data reference |
| `references/workflow-guide.md` | End-to-end workflows |
| `references/troubleshooting.md` | Diagnostic guide |
| `references/test-scenarios.md` | Concrete validation scenarios |
| `references/migration-checklist.md` | Migration checklist |
| `references/branding-audit.md` | Branding, author, logo, and emoji audit |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization review |
| `references/verification-log.md` | Web validation log with two-pass source checks |
| `scripts/insurance_coverage_analyzer_client.py` | Underscored client implementation copy for script-level use |
| `scripts/insurance-coverage-analyzer-cli.py` | CLI script wrapper |
| `scripts/test_insurance_coverage_analyzer_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenarios |
| `metadata.json` | Skill metadata |
| `CHANGELOG.md` | Keep-a-Changelog history |
| `LICENSE` | MIT license |
| `pyproject.toml` | Project configuration |
| `requirements-dev.txt` | Development dependencies |

## Verification

Version 2.1.0 adds a two-pass web validation log for official Israeli source claims, rates, terminology, portal posture, and API or webhook applicability. Review `references/verification-log.md` before adapting regulatory statements.

## Privacy

Keep processing local when possible. Redact full Israeli ID numbers, full policy numbers, medical records, and government login artifacts before sharing. Do not automate identity-bound portals or request one-time passwords.

## Professional review triggers

Request licensed review before cancellation or replacement when health or life coverage requires underwriting, an old policy may have grandfathered terms, a known medical condition exists, a mortgage bank assignment exists, beneficiaries are unclear, or a business agreement relies on coverage.
