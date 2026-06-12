# HR Compliance Advisor

Offline-first skill package for Israeli HR compliance triage. Use it to structure questions about Israeli labor-law obligations, identify risk, and prepare practical next steps for small businesses, service providers, employees, and consumers.

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English skill guide with examples, edge cases, decision trees, anti-patterns, and production checklist |
| `SKILL_HE.md` | Hebrew skill guide with Israeli terminology and localized formatting |
| `hr_compliance_advisor/` | Installable Python package |
| `references/api-reference.md` | Legal source map and structured request/response reference |
| `references/workflow-guide.md` | End-to-end operational workflows |
| `references/troubleshooting.md` | Diagnostic guide |
| `references/test-scenarios.md` | Concrete test scenarios |
| `references/migration-checklist.md` | Migration checklist |
| `references/branding-audit.md` | Neutrality and attribution audit |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization review log |
| `references/verification-log.md` | Web-validation log with Pass 1 and Pass 2 source checks |
| `scripts/hr_compliance_advisor_client.py` | Typed sync and async helper module |
| `scripts/hr-compliance-advisor-cli.py` | Typer command line interface |
| `scripts/test_hr_compliance_advisor_client.py` | Pytest suite |
| `scripts/examples/` | Runnable examples |
| `pyproject.toml` | Installable project metadata and tool config |
| `requirements-dev.txt` | Development dependencies |
| `CHANGELOG.md` | Keep-a-Changelog release notes |
| `LICENSE` | MIT license |

## Install for local development

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a case, extract the returned identifier, and use it in the next command.

```bash
python scripts/hr-compliance-advisor-cli.py scenario retail-minimum-wage > /tmp/hr-facts.json
CREATE_RESPONSE=$(python scripts/hr-compliance-advisor-cli.py create-case --input /tmp/hr-facts.json --env sandbox)
CASE_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["case_id"])' <<< "$CREATE_RESPONSE")
python scripts/hr-compliance-advisor-cli.py review-case "$CASE_ID" --pretty
```

Run a direct analysis or the test suite.

```bash
python scripts/hr-compliance-advisor-cli.py analyze --input examples/facts.json --pretty --env sandbox
python -m pytest scripts/test_hr_compliance_advisor_client.py
```

Use the installable package.

```python
from hr_compliance_advisor import EmployeeFacts, HRComplianceClient

facts = EmployeeFacts(worker_type="employee", hourly_rate_ils=31)
report = HRComplianceClient().review(facts)
print(report["overall_risk"])
```

## Environment overrides

Default minimum wage values reflect the web-validated 04/06/2026 general adult snapshot. The helper reads optional variables such as `HR_COMPLIANCE_MIN_HOURLY_WAGE_ILS`, `HR_COMPLIANCE_MIN_MONTHLY_WAGE_ILS`, `HR_COMPLIANCE_REGULAR_WEEKLY_HOURS`, and `HR_COMPLIANCE_MAX_WEEKLY_OVERTIME_HOURS`. Treat every configured value as a period-specific assumption that must be checked against official Israeli publications.

## Legal and payroll caution

The helper uses configurable defaults for rates and thresholds. Verify current official Israeli rates, sector expansion orders, and legal requirements before action. Escalate critical or high-risk findings to a qualified Israeli professional.
