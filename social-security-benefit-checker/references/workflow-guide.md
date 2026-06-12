# Workflow guide

Use these workflows to run consistent intake, screening, document collection, and follow-up for Israeli benefit cases.

## Workflow 1: laid-off employee seeking unemployment benefit

### Intake

Collect:

- age
- residency
- last employment status
- monthly wage
- recognized qualifying months
- termination reason
- Employment Service registration confirmation
- registration date
- children count only when household triage is also needed

### Run

```bash
social-security-benefit-checker create-profile --file unemployment-profile.json --env sandbox
social-security-benefit-checker check --profile-id "$PROFILE_ID" --benefit unemployment --env sandbox
```

### Interpret

| Result | Action |
| --- | --- |
| `likely_eligible` | Prepare claim, attach termination and wage documents, verify entitlement days |
| `possibly_eligible` | Review resignation, unpaid leave, late registration, or special pathway |
| `not_likely` | Check official exceptions before closing the case |
| `insufficient_information` | Add every field listed in `missing_info` |

### Documents

- Employment Service registration confirmation
- termination letter, dismissal letter, or end-of-contract notice
- recent payslips or employer wage report
- bank account confirmation
- explanation letter for resignation or unpaid leave when relevant

### Quality checks

- Do not use business revenue as salaried wage.
- Do not assume a resignation is justified without evidence.
- Do not skip registration-date review.

## Workflow 2: self-employed person with income drop

### Intake

Collect:

- current self-employed profit, not turnover
- spouse income
- household type
- children count
- current asset status
- vehicle status
- work-test registration or exemption
- business closure evidence when unemployment is being checked

### Run

```bash
social-security-benefit-checker check-file --file freelancer-profile.json --benefit all --env sandbox
```

### Interpret

- Treat unemployment as not likely while the business is active.
- Treat income supplement as a means-tested path.
- Request accountant confirmation for profit, advances, and closure documents.
- Retest when monthly profit changes materially.

### Output note

When the result is `insufficient_information` for income supplement, focus on `EMPLOYMENT_SERVICE_REGISTRATION_OR_EXEMPTION`, assets, and spouse income before giving any advice.

## Workflow 3: general disability intake

### Intake

Collect:

- age
- residency
- medical disability percent if already determined
- highest single impairment percent when relevant
- work-capacity loss percent
- current income
- medical documentation categories, not full records in the prompt

### Run

```bash
social-security-benefit-checker check-file --file disability-profile.json --benefit general_disability --env sandbox
```

### Interpret

| Situation | Action |
| --- | --- |
| medical percent missing | Prepare medical file and mark as missing |
| capacity loss missing | Prepare functional evidence and income evidence |
| age below 18 or at retirement age | move to another benefit workflow |
| current work income exists | flag possible reduction or capacity review |

### Documents

- specialist summaries
- diagnostic test results
- hospitalization and treatment summaries
- medication list
- occupational limitation evidence
- income documents

### Human review

Add a human review before telling a person that the disability pathway is strong or weak. Committee decisions and appeal deadlines require careful handling.

## Workflow 4: child allowance for a new or growing family

### Intake

Collect:

- parent or guardian residency
- number of children
- child birth dates in DD/MM/YYYY
- registry status
- payment account status
- custody or guardianship details when relevant

### Run

```bash
social-security-benefit-checker check-file --file child-profile.json --benefit child_allowance --env sandbox
```

### Interpret

- `likely_eligible`: confirm registry and payment account.
- `possibly_eligible`: add birth dates.
- `not_likely`: verify whether a child is under 18 or whether another guardian receives payment.

### Special cases

- separated parents
- foster-care arrangements
- guardianship orders
- child living outside the household
- child close to age 18
- delayed population registry update

## Workflow 5: income supplement household triage

### Intake

Collect:

- applicant age
- residency
- household type
- applicant income
- spouse income
- alimony or pension income
- number of children
- assets above or below the official limit
- vehicle issue
- other benefits
- Employment Service registration or exemption

### Run

```bash
social-security-benefit-checker check-file --file household-profile.json --benefit income_supplement --env sandbox
```

### Interpret

| Result | Meaning | Action |
| --- | --- | --- |
| `likely_eligible` | Rough household income and blocker checks support a path | Verify exact official threshold and documents |
| `insufficient_information` | income may fit, but a work-test or exemption fact is missing | collect registration or exemption evidence |
| `not_likely` | income, age, residency, assets, or vehicle facts block the rough path | check official exceptions |
| `possibly_eligible` | use only if local adaptation adds exception logic | send to human review |

### Accounting checks for small businesses

- Use profit after recognized expenses, not gross receipts.
- Check whether recent profit reflects a one-time month or a stable change.
- Keep tax records and bookkeeping evidence ready.
- Review National Insurance advances and income classification.

## Workflow 6: combined household triage

Use a combined check when a household asks a broad question such as "what benefits should be checked after a dismissal, birth, illness, or income drop".

### Run

```bash
social-security-benefit-checker workflow --file combined-profile.json --env sandbox
```

### Output review order

1. Resolve validation errors.
2. Review `recommended_benefits`.
3. Read warnings before amount ranges.
4. Review missing information.
5. Prepare documents.
6. Verify official sources.
7. Add human review.

### Case note template

```text
Case date: 02/06/2026
Profile source: applicant interview and documents
Benefits screened: unemployment, general disability, child allowance, income supplement
Rules verified on: DD/MM/YYYY
Missing information:
Documents requested:
Warnings:
Human reviewer:
Final advice:
```

## Workflow 7: production release

Before enabling the checker in a service desk, accounting office, or consumer support flow:

1. Run the test suite.
2. Run syntax compilation.
3. Verify official rules and amount tables.
4. Confirm Hebrew wording.
5. Confirm data retention rules.
6. Confirm no personal identifiers are stored in sample profiles.
7. Train staff on status meanings.
8. Escalate exceptions to a qualified reviewer.
9. Recheck after legislative changes or emergency directives.
10. Record source dates in case files.
