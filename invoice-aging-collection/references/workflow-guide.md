# Workflow Guide

This guide describes concrete end-to-end workflows for Israeli invoice aging and collection reminders.

## Workflow 1: First import and aging report

### Goal

Turn a bookkeeping export into an actionable aging report.

### Inputs

- CSV or JSON export of open invoices.
- Client contact details.
- Current as-of date.
- Configured blocked dates for holidays.

### Steps

1. Export open invoices from the accounting system.
2. Confirm every row contains invoice number, client, issue date, due date, amount, status, and currency.
3. Convert dates to `DD/MM/YYYY` or `YYYY-MM-DD`.
4. Import the ledger with the CLI.
5. Run the aging report.
6. Review invoices grouped by age bucket.
7. Resolve validation warnings before generating reminders.

### CLI example

```bash
python scripts/invoice-aging-collection-cli.py import-csv invoices.csv --out ledger.json
python scripts/invoice-aging-collection-cli.py age ledger.json --as-of 15/04/2026
```

### Expected output

```json
{
  "bucket_totals": {
    "current": "0.00",
    "30": "2500.00",
    "60": "2000.00",
    "90_plus": "7800.00"
  },
  "requires_human_review": 2
}
```

### Done criteria

- No missing clients.
- No negative outstanding balances.
- No reminders generated for paid invoices.
- All dates display as `DD/MM/YYYY`.
- All ILS amounts display with `₪`.

## Workflow 2: Friendly WhatsApp reminder

### Goal

Send a low-friction message for an invoice that is 30-44 days overdue.

### Preconditions

- Invoice is open.
- No unresolved dispute exists.
- WhatsApp number is verified.
- No reminder was sent today for the same invoice.
- Current date is not blocked.

### Steps

1. Generate a dry-run reminder.
2. Verify name, invoice number, amount, and due date.
3. Copy the approved message to WhatsApp or send through an approved WhatsApp Business template.
4. Save the message content and delivery timestamp.
5. Set the next check date to 7-14 days later.

### CLI example

```bash
python scripts/invoice-aging-collection-cli.py reminders ledger.json --as-of 15/04/2026 --channel whatsapp --dry-run
```

### Message example

```text
היי לקוח לדוגמה בע"מ,
רציתי לוודא שקיבלת את חשבונית INV-100 מתאריך 01/01/2026 על סך ₪2,500.00.
מועד התשלום היה 31/01/2026, ונשארה יתרה פתוחה של ₪2,000.00.
אשמח לעדכון לגבי מועד התשלום.
תודה,
סטודיו דוגמה
```

### Done criteria

- The message is respectful and short.
- The outstanding balance reflects partial payments.
- The message is stored in the evidence log.
- The next action is scheduled on a business day.

## Workflow 3: Formal email at 60 days

### Goal

Move from informal reminder to documented written demand.

### Preconditions

- Invoice is 60-74 days overdue.
- No active dispute or payment promise blocks escalation.
- Client email is verified.
- Invoice PDF is available.
- Human approval is recorded.

### Steps

1. Generate the formal email.
2. Attach the invoice PDF.
3. Add payment instructions.
4. Send from the business email domain.
5. Store sent email, headers, attachments list, and timestamp.
6. Update the invoice record with `last_stage=formal_email`.

### CLI example

```bash
python scripts/invoice-aging-collection-cli.py render ledger.json --invoice-id INV-100 --stage formal_email --as-of 15/04/2026
```

### Done criteria

- Subject contains invoice number.
- Body includes due date and open balance.
- Deadline is clear.
- Email copy is saved.
- Follow-up date is set.

## Workflow 4: Payment promise arrangement

### Goal

Avoid unnecessary escalation after a credible payment promise.

### Inputs

- Client reply.
- Promised payment date.
- Optional partial amount.

### Steps

1. Record the promise date and amount.
2. Require written confirmation for split payments.
3. Suspend reminders until the next business day after the promise date.
4. Recheck bank receipt or payment proof.
5. Resume escalation only if the promise fails.

### Example note

```json
{
  "invoice_id": "INV-100",
  "event": "payment_promise",
  "promised_date": "25/04/2026",
  "promised_amount": "2000.00",
  "source": "email reply"
}
```

### Done criteria

- The promise is not marked as payment.
- No reminder is sent before the promise date.
- Missed promise automatically returns the invoice to the appropriate bucket.

## Workflow 5: Dispute handling

### Goal

Pause pressure and handle legitimate disagreements without harming collection.

### Dispute categories

| Category | Evidence needed | Next action |
|---|---|---|
| Delivery dispute | Delivery note, project acceptance, email confirmation | Send proof and request response. |
| Quality dispute | Scope of work, acceptance criteria, correction history | Offer correction or factual rebuttal. |
| Amount dispute | Contract, quote, change order, invoice | Reconcile and issue adjustment if needed. |
| Entity dispute | Purchase order, company registration, billing instruction | Correct debtor details if required. |
| No-detail refusal | Reminder history and invoice copy | Ask for specific written reason. |

### CLI action

Use a ledger note or a custom field:

```json
{
  "invoice_id": "INV-100",
  "status": "disputed",
  "dispute_reason": "amount_mismatch",
  "escalation_paused": true
}
```

### Done criteria

- Automatic reminders are paused.
- The dispute reason is documented.
- Evidence is attached to the file.
- The next action is factual and reviewable.

## Workflow 6: Final demand and small-claims preparation

### Goal

Prepare a clean evidence file before legal escalation.

### Preconditions

- Invoice is 90+ days overdue.
- Informal and formal reminders were sent.
- Debt is not genuinely disputed or the dispute response is documented.
- Client identity and address are verified.
- Current small-claims threshold and filing fee are checked.

### Evidence checklist

- Signed agreement, quote, or order.
- Invoice copy.
- Proof of invoice delivery.
- Proof of service or product delivery.
- Payment ledger showing outstanding balance.
- Copies of WhatsApp reminders.
- Copies of email reminders with headers.
- Registered-mail receipt for final demand.
- Client replies or lack of response.
- Calculation of principal, excluding unverified interest.

### CLI example

```bash
python scripts/invoice-aging-collection-cli.py evidence ledger.json --client-id c-100 --out evidence-c-100.json
```

### Done criteria

- The claim amount matches the ledger.
- Each invoice is listed separately.
- The demand letter is dated and signed.
- Postal tracking is saved.
- Legal thresholds are verified before filing.

## Workflow 7: After payment

### Goal

Close the invoice and preserve collection history.

### Steps

1. Verify the payment in the bank account.
2. Record payment date, amount, and reference.
3. Mark invoice paid when outstanding balance reaches zero.
4. Send a short receipt acknowledgment when appropriate.
5. Keep the evidence file for retention needs.
6. Remove the invoice from active reminders.

### Done criteria

- No further reminders are generated.
- Aging report excludes the closed invoice.
- Payment record ties back to bank reference.
