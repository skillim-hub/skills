# Social Security Benefit Checker

Offline-first preliminary checker for Israeli National Insurance benefits. The package screens profiles for unemployment benefit, general disability allowance, child allowance, and income supplement.

Use the output as a triage aid. Verify final entitlement, payment amount, and filing obligations against official National Insurance Institute and Employment Service instructions.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a profile JSON file:

```bash
cat > profile.json <<'JSON'
{
  "age": 42,
  "resident": true,
  "employment_status": "unemployed",
  "monthly_income": 8500,
  "spouse_income": 0,
  "children_count": 2,
  "household_type": "single_parent",
  "qualifying_months": 14,
  "termination_reason": "laid_off",
  "registered_employment_service": true,
  "birth_dates": ["12/04/2018", "30/09/2021"]
}
JSON
```

Create a local profile and extract its identifier:

```bash
CREATE_RESPONSE="$(social-security-benefit-checker create-profile --file profile.json --env sandbox)"
PROFILE_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["profile_id"])' <<< "$CREATE_RESPONSE")"
printf '%s\n' "$CREATE_RESPONSE"
```

Use the extracted identifier in the next step:

```bash
social-security-benefit-checker check --profile-id "$PROFILE_ID" --benefit all --env sandbox
```

Run a one-step workflow without storing the identifier manually:

```bash
social-security-benefit-checker workflow --file profile.json --env sandbox
```

## Python usage

```python
from social_security_benefit_checker import ApplicantProfile, SocialSecurityBenefitChecker

profile = ApplicantProfile.from_mapping(
    {
        "age": 42,
        "resident": True,
        "employment_status": "unemployed",
        "monthly_income": 8500,
        "children_count": 2,
        "qualifying_months": 14,
        "termination_reason": "laid_off",
        "registered_employment_service": True,
        "birth_dates": ["12/04/2018", "30/09/2021"],
    }
)

checker = SocialSecurityBenefitChecker(environment="sandbox")
created = checker.create_profile(profile)
profile_id = created["profile_id"]
results = checker.check_profile_id(profile_id)

for item in results["results"]:
    print(item["benefit"], item["status"])
```

## Async usage

```python
import asyncio
from social_security_benefit_checker import ApplicantProfile, SocialSecurityBenefitChecker

async def main():
    profile = ApplicantProfile(age=35, resident=True, children_count=1, birth_dates=["01/01/2020"])
    checker = SocialSecurityBenefitChecker(environment="sandbox")
    results = await checker.async_check_all(profile)
    print([result.to_dict() for result in results])

asyncio.run(main())
```

## Development commands

```bash
pytest
python -m compileall scripts/ -q
python -m compileall social_security_benefit_checker/ -q
```

## Environment variables

| Variable | Purpose |
| --- | --- |
| `BENEFIT_CHECKER_STORE` | Override the local JSON profile store directory |
| `BENEFIT_CHECKER_PROFILE_JSON` | Provide a profile to the CLI without a file |
| `BENEFIT_CHECKER_ENV` | Default environment for example scripts |
| `BENEFIT_CHECKER_OUTPUT` | Optional output path used by example scripts |
| `BENEFIT_CHECKER_DEFAULT_CITY` | Optional contextual note in example scripts |

The `sandbox` environment is intended for demonstrations and tests. The `production` environment changes the storage namespace and output metadata only; it does not connect to government services.

## File index

| Path | Description |
| --- | --- |
| `SKILL.md` | English operating guide with examples, edge cases, decision tree, anti-patterns, and production checklist |
| `SKILL_HE.md` | Hebrew guide with Israeli terminology, ₪ amounts, and DD/MM/YYYY dates |
| `references/api-reference.md` | Official source map, local interface examples, request and response samples, error tables |
| `references/workflow-guide.md` | End-to-end workflows for unemployment, disability, child allowance, income supplement, and combined household triage |
| `references/troubleshooting.md` | Operational troubleshooting and correction steps |
| `references/test-scenarios.md` | More than 20 concrete scenarios |
| `references/migration-checklist.md` | Upgrade checklist from earlier layouts |
| `references/branding-audit.md` | Neutrality audit and corrective actions |
| `references/hebrew-qa-log.md` | Hebrew quality review log |
| `scripts/social_security_benefit_checker_client.py` | Typed sync and async client helper |
| `scripts/social-security-benefit-checker-cli.py` | Direct script wrapper for the CLI |
| `scripts/examples/` | Runnable scenario scripts |
| `scripts/test_social_security_benefit_checker_client.py` | Pytest suite |
| `social_security_benefit_checker/` | Installable package used by imports and console command |

## Supported normalized values

Employment status:

```text
employee
self_employed
mixed
unemployed
not_working
unpaid_leave
business_owner
```

Termination reason:

```text
laid_off
fired
end_of_contract
resigned
resigned_justified
unpaid_leave
business_closed
unknown
```

Household type:

```text
single
couple
single_parent
```

Benefit name:

```text
unemployment
general_disability
child_allowance
income_supplement
```

## Web-validated 2026 constants

The local helper stores 2026 screening constants for offline triage only:

| Area | Constant used | Operational note |
| --- | --- | --- |
| VAT context | 18% from 01/01/2025 | Included in verification log for Israeli business context; not used in benefit calculations |
| Child allowance | ₪173 for first and fifth or later child; ₪219 for second through fourth child | Use official calculator when birth order or subsistence increments matter |
| General disability | ₪4,711 for full degree of incapacity; partial degrees use ₪2,718, ₪2,894, and ₪3,211 | Final amount depends on committee decisions and additions |
| Income support | 2026 work-income caps by age and household type | Exact entitlement and payment amount require the official calculator |
| Unemployment | ₪550.76 daily ceiling for first 125 payment days; ₪367.17 afterward | Official calculation depends on age, wage history, registration, and reporting days |

## Safety and compliance notes

Do not treat this package as an official entitlement engine. Add a human review step before advising a claimant to submit, delay, or withdraw a claim. Keep personal identifiers and medical files outside unsecured prompts and sample data.
