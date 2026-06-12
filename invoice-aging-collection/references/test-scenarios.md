# Test Scenarios

Use these scenarios for manual QA, automated tests, and acceptance checks. All dates use DD/MM/YYYY.

## Scenario matrix

| # | Scenario | Input summary | Expected result |
|---:|---|---|---|
| 1 | Not due invoice | Due date tomorrow | Bucket `not_due`, no reminder. |
| 2 | Current invoice | Due date 10 days ago | Bucket `current`, no reminder. |
| 3 | Friendly WhatsApp | Due date 35 days ago | Stage `friendly_whatsapp`, channel WhatsApp. |
| 4 | Follow-up WhatsApp | Due date 50 days ago | Stage `followup_whatsapp`. |
| 5 | Formal email | Due date 65 days ago | Stage `formal_email`, human review required. |
| 6 | Legal warning | Due date 80 days ago | Stage `legal_warning`, 14-day deadline. |
| 7 | Final notice | Due date 120 days ago | Stage `final_notice`, evidence checklist required. |
| 8 | Paid invoice | Status `paid` and paid date exists | Excluded from reminders. |
| 9 | Cancelled invoice | Status `cancelled` | Excluded from aging totals. |
| 10 | Partial payment | Amount ₪2,500, paid ₪500 | Outstanding ₪2,000. |
| 11 | Overpayment | Amount ₪2,500, paid ₪3,000 | Validation error. |
| 12 | Missing client | Invoice references unknown client | Validation error. |
| 13 | Missing WhatsApp | WhatsApp stage but no phone | Reminder blocked for WhatsApp. |
| 14 | Missing email | Email stage but no address | Reminder blocked for email. |
| 15 | Friday reminder | Scheduled action Friday | Move to Sunday or next open day. |
| 16 | Saturday reminder | Scheduled action Saturday | Move to Sunday or next open day. |
| 17 | Holiday reminder | Date in `blocked_dates` | Move to next business day. |
| 18 | Israeli phone normalization | `050-123-4567` | `+972501234567`. |
| 19 | Invalid phone | `12345` | Validation warning or channel block. |
| 20 | DD/MM/YYYY parsing | `15/04/2026` | Parse as 15 April 2026. |
| 21 | ISO parsing | `2026-04-15` | Parse as 15 April 2026. |
| 22 | Due date before issue date | Due `01/01/2026`, issue `10/01/2026` | Validation warning. |
| 23 | Promise to pay | Promised date in future | Pause reminders until after promise date. |
| 24 | Disputed invoice | Status `disputed` | Pause escalation. |
| 25 | Multi-invoice client | Three open invoices | Client summary totals all open balances. |
| 26 | Public-sector invoice | Submitted date used | Due date uses submitted-date logic when configured. |
| 27 | Construction invoice | Longer term configured | Does not trigger early reminder. |
| 28 | Duplicate invoice ID | Same ID appears twice | Validation error. |
| 29 | Unsupported currency | Currency `USD` | Reject unless explicitly enabled. |
| 30 | Formal stage without approval | Attempt to send stage 60 | Block real send; allow dry-run only. |

## Detailed scenario: partial payment

### Input

```json
{
  "invoice_id": "INV-PARTIAL",
  "client_id": "c-100",
  "issue_date": "01/01/2026",
  "due_date": "31/01/2026",
  "amount": "2500.00",
  "currency": "ILS",
  "status": "open",
  "partial_payments": [
    {"date": "15/02/2026", "amount": "500.00"}
  ]
}
```

### Expected

```json
{
  "outstanding_amount": "2000.00",
  "message_contains": "יתרה פתוחה של ₪2,000.00"
}
```

## Detailed scenario: dispute pause

### Input

```json
{
  "invoice_id": "INV-DISPUTE",
  "client_id": "c-200",
  "issue_date": "01/01/2026",
  "due_date": "31/01/2026",
  "amount": "3000.00",
  "currency": "ILS",
  "status": "disputed",
  "dispute_reason": "amount_mismatch"
}
```

### Expected

```json
{
  "bucket": "disputed",
  "reminder_count": 0,
  "next_action": "manual_review"
}
```

## Detailed scenario: blocked date

### Input

```json
{
  "as_of": "23/04/2026",
  "blocked_dates": ["23/04/2026"],
  "invoice_age_days": 45
}
```

### Expected

```json
{
  "scheduled_send_date": "26/04/2026"
}
```

## Acceptance checklist

- At least 20 scenarios pass in automated tests.
- Every generated Hebrew message uses ₪ and DD/MM/YYYY.
- No paid, cancelled, or disputed invoice receives an automatic collection reminder.
- Human approval blocks real send for `formal_email`, `legal_warning`, and `final_notice`.
- The CLI produces valid JSON in `--json` mode.
