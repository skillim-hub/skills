# Privacy-Compliance Checker

A neutral offline package for checking privacy workflows used by Israeli small businesses, freelancers, consumers, and lightweight cloud services. It covers Israeli Privacy Protection Law workflows, Privacy Protection (Data Security) Regulations, Privacy Protection Authority expectations, GDPR touchpoints, direct marketing, transfer review, processor contracts, breach triage, retention, and data-subject rights.

This package provides compliance guidance and deterministic local tooling. It does not replace legal advice.

## Install for local use

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Run a built-in assessment without saving state:

```bash
privacy-compliance-checker assess --scenario customer-club --format markdown
```

Create a saved assessment, extract the ID from the create response, then use that ID in the next step:

```bash
ID=$(privacy-compliance-checker --env sandbox create --scenario customer-club --format json | python -c 'import json,sys; print(json.load(sys.stdin)["id"])')
privacy-compliance-checker --env sandbox get "$ID" --format markdown
```

Create a JSON template, assess it, and save JSON output:

```bash
privacy-compliance-checker template --scenario clinic > clinic.json
privacy-compliance-checker assess --file clinic.json --format json --output clinic-report.json
```

Validate a file:

```bash
privacy-compliance-checker validate clinic.json
```

Print checklist only:

```bash
privacy-compliance-checker checklist clinic.json --format markdown
```

Run tests and syntax checks:

```bash
pytest
python -m compileall scripts/ -q
```

## Python usage

```python
from privacy_compliance_checker import PrivacyComplianceCheckerClient, get_scenario

payload = get_scenario("customer-club")
client = PrivacyComplianceCheckerClient(environment="sandbox")
result = client.assess(payload)

print(result.to_markdown())
```

Async:

```python
from privacy_compliance_checker import AsyncPrivacyComplianceCheckerClient, get_scenario

client = AsyncPrivacyComplianceCheckerClient(environment="sandbox")
result = await client.assess(get_scenario("saas-transfer"))
print(result.to_json())
```

## Environment variables

| Variable | Purpose |
|---|---|
| `PCC_ENV` | Default environment: `sandbox` or `production` |
| `PCC_STATE_DIR` | Directory for saved assessment records |
| `PCC_PROFILE` | Optional label consumed by example scripts |

## Example scripts

Each example reads environment variables, accepts `--env sandbox|production`, and prints `json.dumps(..., ensure_ascii=False, indent=2)` output.

```bash
python scripts/examples/01_customer_club.py --env sandbox
python scripts/examples/02_freelancer_crm.py --env sandbox
python scripts/examples/03_private_clinic.py --env production
python scripts/examples/04_breach_triage.py --env sandbox
python scripts/examples/05_saas_gdpr_transfer.py --env production
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English guide with examples, edge cases, decision trees, troubleshooting, anti-patterns, and production checklist |
| `SKILL_HE.md` | Hebrew guide with Israeli terminology, ₪ examples, and DD/MM/YYYY dates |
| `references/api-reference.md` | Non-API interface and regulation reference, request and response examples, and error tables |
| `references/workflow-guide.md` | End-to-end workflows for stores, freelancers, clinics, marketing cleanup, cloud services, rights requests, breaches, and consumer complaints |
| `references/troubleshooting.md` | Operational troubleshooting guide |
| `references/test-scenarios.md` | More than 20 concrete test scenarios |
| `references/migration-checklist.md` | Migration plan from ad hoc privacy handling to a controlled workflow |
| `references/branding-audit.md` | Branding, attribution, visual asset, and emoji audit report |
| `references/hebrew-qa-log.md` | Hebrew localization and terminology QA log |
| `references/verification-log.md` | Two-pass web validation log with source snippets and correction status |
| `privacy_compliance_checker/client.py` | Installable typed sync and async client implementation |
| `privacy_compliance_checker/cli.py` | Installable Click CLI implementation |
| `scripts/privacy_compliance_checker_client.py` | Underscored compatibility shim for local script imports |
| `scripts/privacy_compliance_checker_cli.py` | Source-tree CLI entry point |
| `scripts/test_privacy_compliance_checker_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenario scripts |
| `metadata.json` | Skill metadata without attribution fields |
| `CHANGELOG.md` | Keep a Changelog history |
| `LICENSE` | MIT license |
| `pyproject.toml` | Installable package configuration |
| `requirements-dev.txt` | Development test requirements |

## Operational limits

- Treat the output as a structured checklist, not legal advice.
- Verify current Israeli filing and notification duties before relying on final conclusions.
- Re-run assessments after adding suppliers, fields, purposes, trackers, overseas access, or automated decisions.
- Store generated reports with the evidence file for each database or workflow.
