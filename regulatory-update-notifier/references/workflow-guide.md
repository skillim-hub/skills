# Workflow Guide

## Workflow 1: Daily ecommerce check

Goal: alert an online store about Israeli consumer protection and privacy changes.

1. Create a profile with industries `ecommerce`, `retail`, and `consumers`.
2. Add keywords such as `ביטול עסקה`, `מכר מרחוק`, `משלוח`, `פרטיות`, and `מאגר מידע`.
3. Monitor Consumer Protection publications, Privacy Protection Authority publications, Reshumot, Knesset bills, and the Government Legislation Site for public consultations.
4. Run scan in sandbox first.
5. Review high and critical alerts.
6. Confirm binding status through Reshumot before changing terms.
7. Update checkout text, terms, cancellation form, and service scripts.
8. Archive the digest and source snapshot.

Command sequence:

```bash
python -m regulatory_update_notifier.cli make-config sources.json --env sandbox
CREATE_RESPONSE=$(python -m regulatory_update_notifier.cli create-profile --name "Online shop" --industry ecommerce --industry retail --keyword "ביטול עסקה" --output profile.json --env sandbox)
PROFILE_ID=$(printf '%s' "$CREATE_RESPONSE" | python -c 'import json,sys; print(json.load(sys.stdin)["id"])')
python -m regulatory_update_notifier.cli scan --config sources.json --profile profile.json --profile-id "$PROFILE_ID" --env sandbox --output updates.json
python -m regulatory_update_notifier.cli digest --input updates.json --locale he --output digest.md
```

## Workflow 2: Freelancer tax watch

Goal: detect tax changes for an Israeli independent contractor.

1. Use industries `freelancer` and `professional-services`.
2. Add keywords `חשבונית`, `עוסק מורשה`, `עוסק פטור`, `מעמ`, and `ניכוי מס במקור`.
3. Monitor Tax Authority, Reshumot, Knesset bills, and the Government Legislation Site for draft tax measures.
4. Extract dates and ₪ thresholds.
5. Route any update affecting bookkeeping, VAT, or invoices to an accountant.

Review checklist:

| Item | Question |
|---|---|
| Actor | Does it apply to an exempt dealer, authorized dealer, company, or nonprofit? |
| Date | Is the date an effective date, filing date, or public comment deadline? |
| Amount | Is the ₪ threshold annual turnover, transaction amount, fine, or exemption? |
| Source | Is final text available in Reshumot? |
| Action | Is a software, bookkeeping, or invoice change required? |

## Workflow 3: Reshumot confirmation

Goal: avoid treating drafts as final law.

1. Search for the official title in Reshumot.
2. Compare publication date, amendment number, and commencement clause.
3. If only a Knesset bill exists, keep status as `bill`.
4. If a final regulation exists, classify as `enacted`.
5. If the commencement date is future, classify as `future-effective`.
6. Preserve both the bill link and final publication link when useful.

## Workflow 4: Public consultation response

Goal: track a draft and decide whether to submit comments.

1. Classify as `draft-regulation`.
2. Extract response deadline separately from effective date.
3. Identify affected business processes and cost drivers.
4. Assign owner for comment drafting.
5. Keep the final rule watch active after submission.

## Workflow 5: Employer compliance digest

Goal: alert an employer about labor updates.

1. Use industries `employer` and `labor`.
2. Monitor Ministry of Labor, Reshumot, and enforcement notices.
3. Flag wage, leave, permit, safety, and inspection updates.
4. Escalate when fines, mandatory language, or recordkeeping duties appear.
5. Send the digest to payroll, operations, and management.

## Workflow 6: Consumer rights summary

Goal: summarize a consumer-facing update in plain Hebrew.

1. Identify the official authority.
2. Translate legal effect into plain action language.
3. Avoid promising compensation or outcome.
4. Include complaint path when the official source provides it.
5. State uncertainty when the publication is guidance or enforcement context rather than a new law.

## Workflow 7: Production deployment

1. Start with sandbox fixtures.
2. Install with `pip install -e .`.
3. Run `pytest -q` and `python -m compileall scripts/ -q`.
4. Configure official production sources.
5. Store raw source snapshots.
6. Apply rate limits.
7. Send only reviewed critical alerts.
8. Reconcile alerts against manual review weekly.


## Workflow 7: Current tax threshold recheck

1. Check the Tax Authority page for the current VAT rate and Israel Invoice allocation threshold.
2. Record the access date and the exact Hebrew sentence that contains the rate or threshold.
3. Compare against `references/verification-log.md`; if the live source differs, treat the live official source as controlling.
4. Route VAT, input-tax deduction, bookkeeping, and invoice-number allocation changes to an accountant before operational rollout.
