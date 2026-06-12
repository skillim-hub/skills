# Migration Checklist

Use this checklist when upgrading from a spreadsheet, earlier reminder workflow, or older package.

## 1. Inventory existing assets

- [ ] Export all open invoices.
- [ ] Export all unpaid client balances.
- [ ] Export client contact details.
- [ ] Export reminder history.
- [ ] Export partial payment records.
- [ ] Export dispute notes.
- [ ] Export promised payment dates.
- [ ] Export invoice PDFs and contracts.
- [ ] Export postal receipts and tracking numbers.

## 2. Clean source data

- [ ] Remove duplicate invoice rows.
- [ ] Normalize invoice numbers.
- [ ] Normalize client IDs.
- [ ] Convert dates to `DD/MM/YYYY` or `YYYY-MM-DD`.
- [ ] Convert amounts to decimal strings.
- [ ] Set currency to `ILS` unless foreign currency handling is enabled.
- [ ] Mark paid invoices as `paid`.
- [ ] Mark cancelled invoices as `cancelled`.
- [ ] Mark disputed invoices as `disputed`.
- [ ] Add missing due dates from contracts or invoices.

## 3. Map fields

| Legacy field | New field | Notes |
|---|---|---|
| `Customer` | `client.name` | Use legal name where available. |
| `Customer No.` | `client.client_id` | Must be stable and unique. |
| `Invoice` | `invoice.invoice_id` | Must be unique. |
| `Invoice Date` | `invoice.issue_date` | Display as DD/MM/YYYY. |
| `Payment Due` | `invoice.due_date` | Preferred aging baseline. |
| `Total` | `invoice.amount` | Principal before partial payments. |
| `Paid` | `partial_payments` | Store payment date and amount. |
| `Balance` | Calculated | Do not import as source of truth unless reconciled. |
| `Phone` | `client.whatsapp` | Normalize to E.164. |
| `Email` | `client.email` | Verify before sending. |

## 4. Validate migrated ledger

Run:

```bash
python scripts/invoice-aging-collection-cli.py validate ledger.json
python scripts/invoice-aging-collection-cli.py age ledger.json --as-of 15/04/2026
```

Resolve:

- Missing clients.
- Duplicate invoice IDs.
- Negative balances.
- Unsupported currencies.
- Bad dates.
- Paid/open status conflicts.
- Missing channel details.

## 5. Migrate reminder history

For each prior message, preserve:

```json
{
  "invoice_id": "INV-100",
  "stage": "friendly_whatsapp",
  "channel": "whatsapp",
  "recipient": "+972501234567",
  "sent_at": "2026-03-01T10:30:00+02:00",
  "content": "היי...",
  "delivery_status": "sent"
}
```

Do not restart reminder sequences from day 30 when formal reminders were already sent. Set `last_stage` based on history.

## 6. Set operational controls

- [ ] Add blocked Israeli holidays.
- [ ] Configure business name and payment instructions.
- [ ] Configure WhatsApp template names.
- [ ] Configure email sender identity.
- [ ] Enable dry-run mode by default.
- [ ] Require approval for formal and legal stages.
- [ ] Define retention and backup rules.
- [ ] Create a review role for disputes.
- [ ] Create a manual override process.

## 7. Run parallel validation

For one billing cycle:

1. Keep the old spreadsheet read-only.
2. Run the new report from the migrated ledger.
3. Compare totals per client.
4. Compare oldest invoice per client.
5. Compare reminders due this week.
6. Resolve differences before enabling live sending.

## 8. Cutover

- [ ] Freeze old workflow.
- [ ] Export final source data.
- [ ] Re-import and validate.
- [ ] Run all automated tests.
- [ ] Generate dry-run reminders.
- [ ] Approve templates.
- [ ] Start live workflow.
- [ ] Monitor bounce/rejection logs daily for the first week.

## 9. Rollback

Keep a rollback package:

- Last known-good ledger.
- Old spreadsheet.
- Template backups.
- Reminder history export.
- Contact export.
- Runbook for disabling sends.

Rollback steps:

1. Disable automated delivery.
2. Restore old workflow.
3. Reconcile any messages sent after cutover.
4. Correct ledger and templates.
5. Retry cutover only after validation passes.
