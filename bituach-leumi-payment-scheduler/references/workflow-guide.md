# Workflow Guide

## Workflow 1: self-employed monthly advance payment

### Inputs

- payer name or internal code;
- coverage month;
- official advance amount or monthly income estimate;
- year-specific Israeli non-business dates;
- reminder offsets;
- payment-channel preference;
- bookkeeping folder location.

### Steps

1. Confirm the person is classified as self-employed for the relevant period.
2. Check the official advance notice or current balance.
3. Generate the schedule with an amount override when an official amount exists.
4. Add reminders 14, 7, 3, and 1 days before the adjusted due date.
5. On the first reminder, check whether income changed materially.
6. On the second reminder, verify the official amount and payment method.
7. On the final reminder, pay or confirm standing-order execution.
8. Save the confirmation with a file name such as `2026-02-15_bituach-leumi_2026-01_confirmation.pdf`.
9. Record the payment in bookkeeping.
10. Review annual totals before the annual income-tax return and Bituach Leumi reconciliation.

### Output

- ICS calendar file for reminders;
- CSV schedule for bookkeeping;
- payment confirmation archive;
- review note for the accountant.

## Workflow 2: new freelancer onboarding

1. Open or confirm the self-employed file.
2. Record the opening date and first coverage month.
3. Confirm the official payment classification.
4. Generate a three-month starter schedule.
5. Add a first-payment reminder earlier than usual, such as 21 days before due date.
6. Add a task to verify the first official voucher.
7. Add a task to update expected income after the first invoices are issued.
8. Export CSV to the onboarding checklist.
9. After the first payment, extend the schedule to 12 months.

### Common controls

- Do not use estimated income as final liability.
- Keep registration confirmations.
- Assign a named owner to payment execution.

## Workflow 3: employer monthly Form 102 cycle

### Timeline

| Timing | Task |
|---|---|
| Month end | close payroll attendance and salary data |
| 10 days before due date | verify payroll register and deductions |
| 5 days before due date | prepare Form 102 data and payment amount |
| 1 day before due date | submit or verify payment readiness |
| Due date | submit, pay, save confirmation |
| Next business day | reconcile bank movement and ledger |

### Steps

1. Generate an employer schedule using monthly payroll estimate.
2. Replace local estimate with payroll-system totals before filing.
3. Confirm Form 102 submission status.
4. Confirm payment status.
5. Save Form 102 copy or submission reference, payment confirmation, payroll register, journal entry, and bank transaction support.
6. Escalate immediately if the payment fails.

## Workflow 4: business with owner advances and employees

1. Create one schedule for the owner's self-employed advances or owner account.
2. Create a separate employer schedule for Form 102.
3. Use separate payer names or internal codes.
4. Export separate CSV files.
5. Reconcile separately.
6. Store evidence separately.
7. Review both schedules during month-end close.

### Why split schedules

- Different legal identities can apply.
- Different source documents apply.
- Different accounting entries apply.
- Different failure modes apply.

## Workflow 5: consumer debt or installment arrangement

1. Confirm official balance in the personal area or notice.
2. Enter the exact installment amount using `--amount`.
3. Generate reminders for the arrangement period.
4. Add an early balance-check reminder.
5. Pay through the official channel.
6. Save confirmation and updated balance.
7. If a payment is missed, do not continue normal scheduling before checking the arrangement status.

## Workflow 6: standing order monitoring

1. Generate schedule with official expected amount.
2. Keep a reminder even though payment is automatic.
3. After the due date, confirm bank debit.
4. Compare debited amount to expected amount.
5. Save bank reference and Bituach Leumi confirmation.
6. Investigate missed, partial, or changed debits immediately.

## Workflow 7: yearly refresh

Complete this process every year, and after every official rate change:

1. Verify contribution thresholds.
2. Verify payer classification.
3. Verify due-date convention.
4. Refresh holiday calendar.
5. Update expected income or payroll.
6. Recreate schedule.
7. Re-export calendar files.
8. Archive the previous schedule.
9. Inform the accountant or responsible bookkeeper.
10. Test one generated event in the target calendar.

## Workflow 8: overdue payment response

1. Stop relying on the original schedule.
2. Check official balance immediately.
3. Check penalties, linkage, interest, and collection status.
4. Determine whether payment can be made online or requires service contact.
5. Create a catch-up schedule only after the official balance is known.
6. Save all communication and confirmations.
7. Add a root-cause note:
   - missing reminder;
   - failed standing order;
   - amount mismatch;
   - authentication issue;
   - unavailable approver;
   - cash-flow decision.

## Workflow 9: bookkeeping handoff

Send the following package monthly:

- CSV schedule row;
- official amount source;
- confirmation file;
- bank transaction;
- ledger code;
- notes on differences between estimate and paid amount;
- status of next due date.

## Workflow 10: calendar export

1. Generate ICS with the CLI.
2. Import it into the operational calendar.
3. Verify timezone and all-day event behavior.
4. Confirm reminders are visible to the responsible person.
5. Delete outdated versions before importing a replacement.
6. Keep a copy of the source JSON for audit.

## Workflow 8: web-validated annual rate refresh

1. Open the official Bituach Leumi rates pages for self-employed workers, salaried employees, non-workers, and employer reporting.
2. Record the access date, relevant quoted snippet, and URL in `references/verification-log.md`.
3. Update `ContributionPolicy` defaults only when two sources confirm the same operational value or an official source corrects the package.
4. Update tests for every changed default.
5. Run `pytest --color=no -q -o addopts=` and `python -m compileall scripts/ -q`.
6. Keep VAT as a documented external tax fact unless a user explicitly asks to integrate VAT scheduling.
