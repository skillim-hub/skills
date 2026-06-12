# Troubleshooting guide

Use this guide when a result looks wrong, a workflow stops, or a test fails.

## General diagnostic sequence

1. Validate the profile.
2. Read `missing_info` before reading amount estimates.
3. Confirm normalized field values.
4. Check whether the case belongs to a supported benefit.
5. Verify official rules if the case depends on an exception.
6. Keep calculations separate from official entitlement decisions.

## Validation problems

| Symptom | Cause | Correction |
| --- | --- | --- |
| `AGE_OUT_OF_RANGE` | Age is negative, too high, or not an integer | Enter age at claim date as an integer |
| `RESIDENT_MUST_BE_BOOLEAN` | Residency is not true or false | Use `true` or `false` |
| negative income error | An amount was entered below zero | Use zero for no income |
| percent out of range | Disability or capacity percent is below 0 or above 100 | Use a value from 0 to 100 |
| claim date invalid | Unsupported date format | Use DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD |

## Unemployment issues

### Result is not likely for a self-employed person

Cause: current self-employment generally does not match the ordinary employee unemployment pathway.

Correction:

- Check whether the business closed.
- Add `business_closed: true` only with evidence.
- Use `termination_reason: "business_closed"` only when official rules support that pathway.
- Check income supplement separately.

### Result is insufficient information

Common missing fields:

- `QUALIFYING_MONTHS`
- `EMPLOYMENT_SERVICE_REGISTRATION`
- `TERMINATION_REASON`

Correction:

- Count recognized employment months.
- Confirm registration with the Employment Service.
- Enter a normalized reason such as `laid_off`, `fired`, `end_of_contract`, `resigned`, `resigned_justified`, `unpaid_leave`, or `business_closed`.

### Voluntary resignation looks too favorable

Cause: the checker marks resignation as possible when other data supports a path, but adds a warning.

Correction:

- Require evidence for justified resignation.
- Check waiting-period rules.
- Record the official source date before advising.

### Late registration warning appears

Cause: `registered_within_3_months` is false.

Correction:

- Verify the actual registration date.
- Check whether entitlement days are reduced.
- Document why registration was delayed.

## General disability issues

### Missing medical information

Cause: `medical_disability_percent` or `work_capacity_loss_percent` is absent.

Correction:

- Collect committee decisions if already issued.
- If no decision exists, collect medical documents and mark the case as preliminary.
- Avoid promising a result before the medical committee.

### Capacity loss below threshold

Cause: `work_capacity_loss_percent` is below the verified preliminary threshold.

Correction:

- Review whether the percent is official or estimated.
- Collect evidence of functional limitations.
- Consider appeal or reassessment only with qualified review.

### Applicant near retirement age

Cause: the general disability pathway has an age boundary.

Correction:

- Check old-age, nursing, mobility, or special-services paths.
- Do not force the profile into general disability when another benefit is more appropriate.

## Child allowance issues

### Result is possible instead of likely

Cause: `children_count` exists but `birth_dates` is empty.

Correction:

- Add birth dates in DD/MM/YYYY.
- Verify each child is under 18 at the relevant date.
- Confirm registry status.

### No eligible child found

Cause: all entered birth dates indicate age 18 or older, or child count is zero.

Correction:

- Check for date entry mistakes.
- Use DD/MM/YYYY to prevent month and day confusion.
- Verify whether a different family benefit applies.

### Payment recipient is uncertain

Cause: separation, guardianship, foster care, or institutional care can affect routing.

Correction:

- Request custody or guardianship documents.
- Verify payment account in the official personal service area.
- Escalate disputes to human review.

## Income supplement issues

### Income appears below threshold but result is insufficient information

Cause: work-test registration or exemption is missing.

Correction:

- Add `registered_employment_service: true` when registration exists.
- Document an exemption separately in the case file.
- Review whether current employment status requires registration.

### Result is not likely due to assets

Cause: `assets_exceed_limit` is true.

Correction:

- Verify official asset rules.
- Check whether the asset is exempt.
- Update the profile only after evidence is reviewed.

### Vehicle warning appears

Cause: `vehicle_value_exceeds_limit` is true.

Correction:

- Check the current vehicle rules.
- Review medical, work, disability, or family exceptions.
- Keep the case in human review until the exception is confirmed.

### Household income conflicts with the applicant statement

Cause: spouse income, pension, alimony, or self-employed profit may be missing or misunderstood.

Correction:

- Rebuild the monthly household income calculation.
- Use profit for self-employment, not gross receipts.
- Add alimony or pension income when relevant.
- Retest after changes.

## CLI problems

| Message | Cause | Correction |
| --- | --- | --- |
| `Provide --file, --json, or BENEFIT_CHECKER_PROFILE_JSON` | no input profile supplied | pass a file, JSON string, or environment variable |
| `Profile not found` | identifier does not exist in the selected store | use the identifier from the create response or set the same `--store-dir` |
| command not found | package was not installed | run `pip install -e .` |
| import error | installation was not completed or wrong environment is active | activate the virtual environment and reinstall |

## Test failures

### Async tests fail

Cause: `pytest-asyncio` is missing.

Correction:

```bash
pip install -r requirements-dev.txt
pytest
```

### Hyphenated import error

Cause: Python cannot import a module using a hyphenated file name.

Correction:

- Import `social_security_benefit_checker`.
- Use `scripts/social_security_benefit_checker_client.py` for direct script import.
- Keep the hyphenated CLI file only as an executable wrapper.

### Syntax compilation fails

Cause: a script contains invalid Python syntax.

Correction:

```bash
python -m compileall scripts/ -q
python -m compileall social_security_benefit_checker/ -q
```

Fix the reported file before bundling.

## Data protection problems

### Sensitive data was pasted into a profile

Correction:

1. Remove identity numbers, medical file numbers, bank numbers, and addresses.
2. Replace with category-level facts.
3. Delete local copies that are not required.
4. Record only the minimum information needed for the triage purpose.

### Medical documents were added to an unsecured workflow

Correction:

- Store medical documents in a controlled document system.
- Use only summary fields in the checker.
- Limit access to authorized staff.
- Document retention and deletion rules.

## Escalation triggers

Escalate to a qualified reviewer when the case includes:

- voluntary resignation with disputed facts
- business closure
- controlling shareholder status
- cross-border residency
- separated parents or guardianship dispute
- disability appeal deadline
- vehicle or asset exception
- emergency rule or temporary directive
- suspected overpayment or debt
