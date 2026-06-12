# End-to-end workflow guide

## Workflow 1: Renewal negotiation

Goal: prepare a user to call an insurer before annual renewal.

Inputs: renewal notice, current policy schedule, new quote, claims history, and any coverage change.

Steps:
1. Redact identifiers.
2. Identify policy type.
3. Normalize current and renewal premiums to ₪ per month and ₪ per year.
4. Compare coverage changes.
5. Separate pure price increase from benefit increase.
6. Prepare negotiation points: retention discount, same coverage at lower price, deductible change, missing cover correction.
7. Request revised schedule in writing.

Output example:

```markdown
Current premium: ₪185/month, ₪2,220/year
Renewal premium: ₪215/month, ₪2,580/year
Increase: ₪360/year

Actions:
- Request written explanation for the increase.
- Ask for same coverage at last year's premium.
- Confirm no benefit was reduced.
- Request revised schedule before payment.
```

## Workflow 2: Health insurance overlap review

Goal: find duplicate or missing health coverage across private insurance and supplementary health-plan cover.

Steps:
1. Map private policy chapters: surgery, drugs outside basket, transplants, ambulatory, specialist consultations, serious illness.
2. Map supplementary tier at high level.
3. Mark overlaps.
4. Check whether the private policy adds practical value: provider choice, higher limit, faster path, overseas treatment, medication cover.
5. Flag exclusions, loadings, and waiting periods.
6. Produce keep / clarify / compare / licensed-review actions.

Stop when replacement requires new underwriting or the user has a known condition. Add a licensed-review warning.

## Workflow 3: Home insurance for mortgage borrower

Goal: verify that a cheaper or new quote still satisfies bank and household needs.

Steps:
1. Confirm owner, tenant, or landlord status.
2. Check mortgage lender clause and assignment wording.
3. Compare structure insured amount with bank requirement and realistic reconstruction value.
4. Compare contents amount and exclusions.
5. Check water damage service arrangement.
6. Check earthquake coverage and percentage deductible.
7. Check third-party liability.
8. Check employer liability for a cleaner, caregiver, babysitter, or other domestic worker.
9. Check business equipment and client visits for home-office users.
10. Create a gap list and insurer questions.

Output example:

```markdown
Do not switch until the bank clause is confirmed.
The cheaper quote has ₪150,000 lower structure cover and no contents section.
Earthquake deductible equals ₪110,000.
Confirm employer liability because a cleaner works in the home.
```

## Workflow 4: Life insurance for freelancer family protection

Goal: separate mortgage coverage from family and business needs.

Steps:
1. Classify each policy: mortgage-assigned, personal family protection, business key-person, partner buyout.
2. Compare death benefit to obligations.
3. Model premium over 10, 20, and 30 years when stepped pricing exists.
4. Confirm beneficiaries and bank assignment.
5. Check exclusions and underwriting loadings.
6. Identify underinsurance or expensive duplication.
7. Flag tax, estate, and business agreement issues for professional review.

## Workflow 5: Small-business home-office boundary

Goal: find gaps caused by a business operating from home.

Steps:
1. Check business equipment in contents.
2. Check client property.
3. Check client visits and third-party liability.
4. Check domestic worker or employee exposure.
5. Confirm whether professional liability is needed.
6. Request written insurer confirmation.

## Workflow 6: Safe replacement path

Steps:
1. Compare old and new policy side by side.
2. Confirm the new policy is accepted in writing.
3. Confirm no new exclusion or loading.
4. Confirm waiting periods.
5. Confirm beneficiary and bank assignment.
6. Confirm first premium date.
7. Keep old policy active until replacement start date is certain.
8. Cancel only after documentation is complete and professional review is satisfied.

Stop conditions:
- health or life replacement with new underwriting
- old or grandfathered policy
- known medical condition
- mortgage assignment
- beneficiary dispute
- business partner or lender reliance
