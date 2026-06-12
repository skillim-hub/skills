# Troubleshooting guide

## Triage table

| Problem | Diagnostic question | Likely cause | Resolution |
|---|---|---|---|
| Cheaper policy appears better | Are limits, deductibles, exclusions, waiting periods, and providers identical? | Price-only comparison | Rebuild matrix |
| Missing annual premium | Is only a monthly price shown? | Cadence omitted | Multiply by 12 and mark estimate |
| Monthly premium is unstable | Is pricing stepped by age? | Age-based premium | Model multiple years |
| Unknown policy type | What are the main chapters? | Ambiguous product name | Classify by coverage |
| Health replacement attractive | Does underwriting apply? | New exclusions may appear | Add replacement warning |
| Home quote excludes contents | Is only structure listed? | Mortgage-focused quote | Add contents gap |
| Earthquake appears included | What is deductible percent? | Large percentage deductible | Convert to ₪ exposure |
| Life duplicates mortgage | Who receives proceeds first? | Bank assignment | Separate bank and family needs |
| Domestic worker absent | Is a cleaner or caregiver employed? | Employer liability omitted | Request written confirmation |
| Home office not covered | Is property used for income? | Business exclusion | Confirm extension |
| Summary conflicts with policy | Which document is binding? | Marketing summary | Prefer policy and endorsements |
| Date ambiguous | Is `05-06-2026` day-month? | Locale mismatch | Use DD/MM/YYYY |
| Full ID exposed | Does input contain 9 digits? | Unredacted source | Redact |
| Medical detail excessive | Is it needed for coverage? | Overcollection | Summarize coverage impact |
| Renewal price jumps | Did discount expire? | First-year discount | Compare year 2 |
| No page references | Was text pasted? | Weak evidence | Mark unverified |
| Multiple same product names | Are issue dates different? | Product generations | Compare by date |
| Deductible basis unclear | Per claim or per year? | Different bases | Preserve wording |
| Supplementary overlap unclear | What does private policy add? | Different systems | Compare practical value |

## Replacement-risk checklist

Flag high risk when any answer is yes:

- Existing health or life policy is old.
- User has a known medical condition.
- New policy requires health declaration.
- New waiting period applies.
- Mortgage bank is assigned.
- Business lender or partner relies on coverage.
- Beneficiary wording changes.
- Current cancellation is irreversible.

## Missing-information prompts

- "Upload or paste the policy schedule, including premium, insured amount, deductibles, exclusions, and renewal date."
- "Confirm whether the premium is monthly or annual."
- "Confirm whether the life policy is assigned to a mortgage bank."
- "Confirm whether the home policy includes contents, third-party liability, and employer liability."
- "Confirm whether the health policy has medical exclusions or waiting periods."

## Anti-pattern diagnostics

| Anti-pattern | Warning sign | Correction |
|---|---|---|
| Premium-only ranking | Cheapest policy selected immediately | Add coverage and deductible comparison |
| Overconfident cancellation | Output says to cancel | Replace with licensed-review warning |
| Ignoring product generation | Old and new health policies treated as identical | Compare issue dates and terms |
| Business/private mixing | Home-office facts ignored | Add business-equipment checks |
| Weak evidence | No source clauses | Add unknown markers |
