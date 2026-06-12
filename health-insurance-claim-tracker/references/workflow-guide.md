# Workflow Guide

## Workflow 1: Household reimbursement through a private policy

1. Collect tax invoice or receipt, referral, medical summary, and payment proof.
2. Open a private claim with the service date and submission date.
3. Add document records using exact document types.
4. Submit the claim in the insurer portal.
5. Save the portal confirmation number in claim notes.
6. Set a follow-up date.
7. Record each reimbursement as a separate payment.
8. If the reimbursement gap remains, compare the approval letter to deductible, cap, waiting period, and exclusion clauses.
9. Appeal when the policy and medical evidence support the missing amount.
10. Close after reimbursement and bank reconciliation.

Example commands:

```bash
hict --env production create \
  --claimant-reference household-4422 \
  --policy-type private \
  --provider "Example Insurance" \
  --service-date 10/04/2026 \
  --submission-date 12/04/2026 \
  --amount 1200.00 \
  --description "Diagnostic imaging reimbursement" \
  --service-kind diagnostics \
  --follow-up-date 12/05/2026
```

```bash
CLAIM_ID="HICT-20260604-AB12CD34"
hict --env production document "$CLAIM_ID" --name receipt.pdf --document-type tax_invoice_or_receipt
hict --env production document "$CLAIM_ID" --name referral.pdf --document-type medical_referral_or_summary
hict --env production reimburse "$CLAIM_ID" --amount 900.00 --paid-date 20/05/2026 --payer "Example Insurance"
```

## Workflow 2: Supplementary health-plan claim

1. Confirm the plan level and service category.
2. Open a supplementary claim.
3. Add receipt, payment proof, member number reference, and plan level.
4. Submit through health-fund app, site, branch, or clinic.
5. Use `missing_documents` if the fund requests a revised receipt or referral.
6. Reconcile the payment and close.

Decision points:

- If the service is covered only after prior approval, add the approval document before submission.
- If the provider is outside the plan arrangement, record that fact in notes.
- If the fund pays only a fixed participation amount, keep the open gap for bookkeeping but close operationally when no further appeal is planned.

## Workflow 3: Freelancer bookkeeping handoff

1. Open the claim with a claimant reference that matches the bookkeeping file.
2. Store the supplier receipt and payment proof.
3. Record the claim as pending reimbursement.
4. Export CSV for bookkeeping at month end.
5. Reconcile reimbursements against bank deposits.
6. Redact medical details before sending to external bookkeeping unless the detail is required and legally allowed.

CSV handoff fields:

| Field | Use |
|---|---|
| `id` | Cross-reference between claim folder and bookkeeping system. |
| `amount_claimed_ils` | Gross out-of-pocket expense. |
| `total_reimbursed_ils` | Actual reimbursement received. |
| `reimbursement_gap_ils` | Remaining cost or appeal amount. |
| `status` | Operational state. |
| `tags` | Business classification such as `bookkeeping`. |

## Workflow 4: Missing documents recovery

1. Update status to `missing_documents`.
2. Copy the exact missing document language from the insurer response into notes.
3. Add a document record with `received=false` if the item has not yet arrived.
4. Request the document from the provider or clinic.
5. When received, update the document record by adding the final document as `received=true`.
6. Resubmit the claim and change status to `submitted` or `in_review`.
7. Reset the follow-up date.

## Workflow 5: Appeal after partial approval

1. Keep the original amount unchanged.
2. Record the partial reimbursement.
3. Calculate the remaining gap.
4. Read the approval letter and identify the reason for reduction.
5. Gather policy clause, medical necessity evidence, referral, approval, and provider explanation.
6. Update status to `appealed`.
7. Save appeal submission confirmation.
8. Track response date and any additional payment.
9. Close only after final operational decision.

Appeal evidence checklist:

- Approval or rejection letter.
- Policy clause or plan entitlement page.
- Medical summary and referral.
- Itemized tax invoice or receipt.
- Payment proof.
- Earlier insurer or health-fund confirmations.
- Timeline of submission and responses.

## Workflow 6: Weekly operations review

Run weekly:

```bash
hict --env production list --overdue-only
hict --env production summary
```

Review:

- Claims with follow-up dates in the past.
- Claims in `missing_documents` for more than seven days.
- Partial approvals with material gaps.
- Paid claims not yet closed.
- Claims missing tax invoice or receipt.
- Exports that must be redacted before external sharing.


## Workflow 7: VAT and Israel Invoice review for business files

1. Record the claim amount as the gross out-of-pocket amount shown on the supplier document.
2. Store the tax invoice or receipt file name in the claim documents list.
3. Add the Israel Invoice allocation number to notes or tags when the supplier document includes one.
4. Do not calculate VAT inside the claim tracker.
5. Export CSV for bookkeeping and let the accounting system or adviser classify VAT, expense recognition, and reimbursement treatment.
6. Keep medical details redacted unless the bookkeeping recipient has a lawful need to see them.
