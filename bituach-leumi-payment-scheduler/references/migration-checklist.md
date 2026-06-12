# Migration Checklist

Use this checklist when moving from a manual spreadsheet, calendar reminders, or a prior general Bituach Leumi reference package to the payment scheduler.

## Inventory current process

- [ ] List every payer identity.
- [ ] Identify self-employed advances.
- [ ] Identify employer Form 102 obligations.
- [ ] Identify consumer debts or installment arrangements.
- [ ] Identify standing orders.
- [ ] Identify manual reminders.
- [ ] Identify current confirmation archive.
- [ ] Identify responsible person for each obligation.

## Clean source data

- [ ] Remove full Israeli ID numbers from exported schedules unless essential.
- [ ] Replace sensitive IDs with short internal codes.
- [ ] Confirm current official amount for each payer.
- [ ] Confirm current status of each file or account.
- [ ] Remove obsolete reminders.
- [ ] Remove duplicate calendar series.
- [ ] Archive old spreadsheets as read-only.

## Configure the new scheduler

- [ ] Choose `self-employed`, `employer`, `small-business`, or `consumer`.
- [ ] Set first coverage month.
- [ ] Set planning horizon.
- [ ] Set official amount override where available.
- [ ] Add income or payroll estimate only when official amount is unavailable.
- [ ] Add Israeli non-business dates.
- [ ] Set reminder offsets.
- [ ] Select output format.

## Validate first output

- [ ] Check first period.
- [ ] Check first adjusted due date.
- [ ] Check first amount.
- [ ] Check reminder dates.
- [ ] Check action list.
- [ ] Check file names.
- [ ] Check calendar import behavior.
- [ ] Check CSV columns required by bookkeeping.
- [ ] Check JSON format if automation consumes it.

## Replace old process

- [ ] Import ICS to the operational calendar.
- [ ] Save CSV in the bookkeeping folder.
- [ ] Save JSON as generation evidence.
- [ ] Mark old spreadsheet as superseded.
- [ ] Delete duplicate reminder series.
- [ ] Notify responsible persons.
- [ ] Run one cycle with parallel manual review.
- [ ] Disable old process after successful cycle.

## Migration from a benefits-focused package

A benefits-focused Bituach Leumi reference may contain eligibility, claims, and forms content. Keep it separate from payment operations.

- [ ] Do not reuse benefit-claim forms as payment evidence.
- [ ] Do not use benefit rate tables for contribution scheduling.
- [ ] Remove unrelated benefit workflows from payment checklists.
- [ ] Keep payment references focused on contributions, balances, Form 102, arrears, and confirmations.
- [ ] Review all metadata and remove unrelated benefit tags.
- [ ] Confirm the payment scheduler name and description match payment use cases.

## Rollback plan

- [ ] Keep the previous calendar or spreadsheet for one cycle.
- [ ] Export the new schedule to a test calendar first.
- [ ] Keep official payment confirmations outside the tool.
- [ ] If errors are found, delete imported ICS events, correct inputs, regenerate, and re-import.
- [ ] Document the issue and correction.

## Post-migration review

After 30 to 45 days:

- [ ] Confirm no due date was missed.
- [ ] Confirm confirmations were archived.
- [ ] Confirm the accountant received the CSV.
- [ ] Confirm standing orders were monitored.
- [ ] Confirm income or payroll estimates still make sense.
- [ ] Confirm holidays are complete for the rest of the year.

## Migrating from v2.1.0 to v2.2.0

- [ ] Replace stale self-employed default rates with 7.70% and 18.00%.
- [ ] Replace stale employer combined default rates with 8.78% and 19.77%.
- [ ] Replace stale consumer no-income default with ₪266.
- [ ] Recreate cached estimates produced before 02/06/2026.
- [ ] Continue using official vouchers, payroll totals, and personal-area balances as payment authority.
