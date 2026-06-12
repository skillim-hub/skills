# Troubleshooting

## Fast triage

| Issue | Immediate action |
|---|---|
| payment due today and amount uncertain | check official balance before paying |
| payment portal unavailable | document attempt, retry through official alternative channel, call service if needed |
| standing order did not debit | verify bank status, account permission, and official balance |
| amount differs from calendar | use official amount, then update future reminders |
| employer payroll not closed | do not file Form 102 from an estimate |
| holiday date missing | add the holiday and regenerate the schedule |
| overdue status appears | verify official balance and penalties before creating catch-up plan |

## Generated amount differs from official amount

### Cause

The scheduler uses a simplified planning policy. Official amounts can change due to classification, minimum income, maximum income, rate updates, prior credits, debt, linkage, interest, reserve duty, maternity, business closure, or manual assessment.

### Fix

1. Use the official amount with `--amount`.
2. Regenerate the schedule.
3. Keep a note that the official amount replaced the estimate.
4. Send the difference to the accountant when material.

## Due date is wrong

### Cause

The wrong start month, due-day setting, or adjustment policy was used.

### Fix

1. Confirm whether `--start-month` is the coverage month, not the payment month.
2. Confirm due day, usually 15 for monthly planning.
3. Add holidays with `--holiday DD/MM/YYYY`.
4. Use `--adjust next-business-day` unless another policy is intentionally required.
5. Regenerate and compare the first three rows manually.

## Calendar import duplicates events

### Cause

The same ICS file was imported more than once, or an old schedule was not deleted before import.

### Fix

1. Delete old imported calendar events.
2. Re-import a single current ICS file.
3. Use a dedicated calendar for Bituach Leumi payments.
4. Store the source JSON file next to the ICS file.

## Hebrew dates are not accepted

Use one of these formats:

- `DD/MM/YYYY`, such as `15/06/2026`;
- `YYYY-MM-DD`, such as `2026-06-15`;
- `YYYY-MM`, such as `2026-06`.

Do not use slashes in CLI input.

## Reminder moved earlier than expected

Reminder dates use a previous-business-day policy by default. If a reminder falls on Friday, Saturday, or a supplied holiday, it moves earlier. This is intentional because preparation should not be delayed.

## Employer payment schedule is incomplete

Employer payment workflows require payroll closure. The scheduler can create due dates, but it cannot validate employee status, salary components, deductions, Form 102 data, or payroll exceptions.

Use this checklist:

- payroll register approved;
- employee changes checked;
- contribution totals verified;
- Form 102 prepared;
- payment method available;
- confirmation archive ready.

## Consumer debt amount keeps changing

Debt balances can change because of linkage, interest, collection costs, payments received, arrangement changes, or official corrections.

Fix:

1. Check the personal area before every payment.
2. Use `--amount` only for the current known installment.
3. Do not assume an old balance remains valid.
4. Save updated balance after payment.

## JSON validation fails

Check for these problems:

- missing `profile`;
- missing `options`;
- unsupported `business_type`;
- invalid `start_month`;
- missing income, payroll, or amount;
- negative amount;
- duplicate reminder offsets.

## CLI command cannot find files

Run commands from the skill root, or pass the full script path:

```bash
python /path/to/bituach-leumi-payment-scheduler/scripts/bituach-leumi-payment-scheduler-cli.py plan \
  --start-month 2026-01 \
  --income 10000
```

## Payment portal rejects identity details

The local schedule does not authenticate against official systems. Verify:

- correct ID or file number;
- correct payer identity;
- correct payment type;
- no closed or inactive file;
- no service restriction;
- no expired card or bank permission.

## Overdue remediation checklist

1. Check official balance.
2. Check collection status.
3. Pay official amount or set written arrangement.
4. Save confirmation.
5. Record ledger entry.
6. Add root-cause note.
7. Add earlier reminders for future cycles.
8. Confirm next cycle is scheduled.

## Escalation triggers

Escalate to a qualified professional or official support when any of these apply:

- large arrears;
- collection letter;
- garnishment or lien;
- employer reporting correction;
- employee complaint;
- classification dispute;
- maternity or reserve-duty impact on contributions;
- closure or reopening of a business;
- contradictory official notices;
- payment cannot be made through normal channels.

## Stale default rates

Symptom: the estimated amount differs from the current official voucher, payroll run, or personal-area balance.

Cause: official rates, thresholds, minimum amounts, or classification columns changed after package release.

Fix: pass `--amount` for the official amount, or update `ContributionPolicy` in code after recording two-source validation in `references/verification-log.md`. Never force a payment amount to match the scheduler when the official channel shows a different amount.
