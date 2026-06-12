# Migration checklist

Use this checklist when upgrading from an earlier local package layout to version 2.1.0.

## Package layout changes

| Previous layout | Version 2.1.0 layout | Action |
| --- | --- | --- |
| `scripts/social-security-benefit-checker-client.py` | removed | replace with `scripts/social_security_benefit_checker_client.py` |
| ad hoc imports from script paths | installable package import | use `from social_security_benefit_checker import ...` |
| one-off CLI behavior | Typer CLI package entry point | use `social-security-benefit-checker` after `pip install -e .` |
| narrow unemployment-only examples | multi-benefit examples | update tests and support scripts to include all supported benefits |
| static quick-start without id reuse | chained profile workflow | extract `profile_id` from `create-profile` response and pass it to `check` |

## Required import changes

Replace direct hyphenated file references with the package import:

```python
from social_security_benefit_checker import ApplicantProfile, SocialSecurityBenefitChecker
```

For direct script inspection, use:

```python
# file path: scripts/social_security_benefit_checker_client.py
```

Do not attempt this import:

```python
import social-security-benefit-checker-client
```

Python module names cannot contain hyphens.

## Installation changes

Use editable installation from the project root:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

The development requirements include `pytest-asyncio` for async tests.

## CLI changes

Use a two-step chain when saving profiles:

```bash
CREATE_RESPONSE="$(social-security-benefit-checker create-profile --file profile.json --env sandbox)"
PROFILE_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["profile_id"])' <<< "$CREATE_RESPONSE")"
social-security-benefit-checker check --profile-id "$PROFILE_ID" --benefit all --env sandbox
```

Use `check-file` for one-off checks that do not need local storage:

```bash
social-security-benefit-checker check-file --file profile.json --benefit child_allowance --env sandbox
```

## Data model changes

Review these fields in existing sample data:

| Field | Migration action |
| --- | --- |
| `children` | use `children_count`; the loader still accepts `children` as an alias |
| `single_parent` | prefer `household_type: "single_parent"` |
| old termination values with hyphens | use underscore values such as `laid_off` and `end_of_contract` |
| free-text employment status | map to normalized values from README |
| missing child birth dates | add `birth_dates` for better child allowance screening |
| disability notes only | add `medical_disability_percent` and `work_capacity_loss_percent` when known |
| revenue field | convert to current monthly profit for self-employed income checks |

## Documentation changes

Confirm the following files exist after migration:

- `SKILL.md`
- `SKILL_HE.md`
- `README.md`
- `CHANGELOG.md`
- `LICENSE`
- `references/api-reference.md`
- `references/workflow-guide.md`
- `references/troubleshooting.md`
- `references/test-scenarios.md`
- `references/migration-checklist.md`
- `references/branding-audit.md`
- `references/hebrew-qa-log.md`

## Test migration

Run:

```bash
pytest
python -m compileall scripts/ -q
python -m compileall social_security_benefit_checker/ -q
```

Expected result:

- all tests pass
- compile commands finish without output
- no import uses a hyphenated client file

## Operational migration

Before replacing an older workflow:

1. Retest all examples.
2. Update support scripts to accept `--env sandbox|production`.
3. Set `BENEFIT_CHECKER_STORE` for the intended local storage directory.
4. Confirm no sensitive files are stored in sample data.
5. Verify official source dates.
6. Review Hebrew wording.
7. Train operators on the four status values.
8. Add manual review for exceptions.
9. Update internal forms to capture missing fields separately from negative reasons.
10. Record the package version in each case note.
