# API and Regulation Reference

## Scope

This skill does not depend on a public Bituach Leumi scheduling API. It creates local planning artifacts: dates, reminders, CSV, JSON, and ICS. Treat generated files as operational aids. Use official systems for identity verification, final balances, Form 102 submission, payment execution, receipts, and legal status.

## Primary official channels to verify

| Channel | Typical use | Notes |
|---|---|---|
| `https://www.btl.gov.il` | public guidance, payment pages, contribution explanations, forms | verify current rules and rates before using estimates |
| `https://ps.btl.gov.il` | personal area, balances, notices, individual payments | requires authentication |
| Bituach Leumi online payment services under `btl.gov.il` / `b2b.btl.gov.il` | card or bank payments when available | payment confirmation must be saved |
| employer reporting and Form 102 services | employer monthly reporting and payment | use payroll-system totals, not rough estimates |
| telephone service `*6050` | service routing and verification | document advice received when operationally important |

## Relevant legal and regulatory sources to cite in workpapers

Use the current official text before relying on any provision.

| Source | Hebrew name | Relevance |
|---|---|---|
| National Insurance Law, consolidated version, 5755-1995 | חוק הביטוח הלאומי [נוסח משולב], התשנ"ה-1995 | core framework for insured persons, contributions, benefits, collection, arrears |
| National Health Insurance Law, 5754-1994 | חוק ביטוח בריאות ממלכתי, התשנ"ד-1994 | health-insurance contribution component collected with National Insurance |
| National Insurance Regulations | תקנות הביטוח הלאומי | operational details, reporting, contribution and payment mechanisms |
| Collection and payment instructions published by Bituach Leumi | הוראות גבייה ותשלום של המוסד לביטוח לאומי | current payment channels, forms, and procedures |
| Employer reporting rules and Form 102 instructions | הוראות דיווח מעסיקים וטופס 102 | monthly employer reporting and payment workflow |
| Official notices on average wage, thresholds, and rates | הודעות בדבר שכר ממוצע, תקרות ושיעורים | contribution brackets and indexed values |


## Web-validated 2026 values

Access date: 02/06/2026. Use these values as bundled planning defaults only. Official Bituach Leumi systems, payroll software, payment vouchers, and accountant workpapers override the scheduler.

| Value | Verified 2026 default | Package action |
|---|---:|---|
| Self-employed standard adult reduced total rate | 7.70% | Corrected default from stale 5.97% |
| Self-employed standard adult regular total rate | 18.00% | Corrected default from stale 17.83% |
| Self-employed reduced bracket threshold | ₪7,703 | Confirmed |
| Monthly contribution ceiling | ₪51,910 | Added to guidance; estimates do not assess above-ceiling edge cases as legal calculations |
| Employer Form 102 resident-employee combined reduced rate | 8.78% | Corrected default from stale 7.35% |
| Employer Form 102 resident-employee combined regular rate | 19.77% | Corrected default from stale 19.33% |
| Consumer with no income default | ₪266 monthly | Corrected default from stale ₪203 |
| Standard VAT rate | 18% from 01/01/2025 | Documented as out of scope for scheduler calculations |

Do not use bundled employer rates for foreign residents, household workers, pension recipients, controlling shareholders, unpaid leave, training, employees above retirement-related columns, reduced work-injury branches, or other special Form 102 rows. Use payroll-system rates for those cases.

## Payment schedule convention

Default planning convention:

```json
{
  "coverage_period": "2026-01",
  "statutory_target_day": 15,
  "statutory_target_month": "following coverage month",
  "weekend_days": ["Friday", "Saturday"],
  "adjustment_policy": "next-business-day"
}
```

This convention supports common monthly planning for self-employed advances and employer reporting. Verify exceptions, special arrangements, standing orders, deferrals, strikes, emergency extensions, or official notices.

## Local client request model

### Self-employed request

```json
{
  "profile": {
    "payer_name": "Freelance Studio",
    "business_type": "self-employed",
    "monthly_income_nis": 14000
  },
  "options": {
    "start_month": "2026-01",
    "months": 12,
    "due_day": 15,
    "adjustment_policy": "next-business-day",
    "holidays": ["2026-06-15"],
    "reminder_days_before": [14, 7, 3, 1]
  }
}
```

### Employer request

```json
{
  "profile": {
    "payer_name": "Small Employer Ltd",
    "business_type": "employer",
    "monthly_payroll_nis": 65000
  },
  "options": {
    "start_month": "2026-01",
    "months": 6,
    "reminder_days_before": [10, 5, 1]
  }
}
```

### Consumer request with known amount

```json
{
  "profile": {
    "payer_name": "Household Account",
    "business_type": "consumer",
    "amount_override_nis": 350
  },
  "options": {
    "start_month": "2026-01",
    "months": 8
  }
}
```

## Local client response model

```json
{
  "generated_at": "2026-06-02T00:00:00+00:00",
  "profile": {
    "payer_name": "Freelance Studio",
    "business_type": "self-employed",
    "monthly_income_nis": 14000,
    "monthly_payroll_nis": null,
    "amount_override_nis": null
  },
  "options": {
    "start_month": "2026-01-01",
    "months": 12,
    "due_day": 15,
    "adjustment_policy": "next-business-day",
    "weekend_days": [4, 5],
    "holidays": ["2026-06-15"],
    "reminder_days_before": [14, 7, 3, 1],
    "reminder_adjustment_policy": "previous-business-day"
  },
  "obligations": [
    {
      "obligation_id": "BL-self-employed-2026-01",
      "payer_name": "Freelance Studio",
      "business_type": "self-employed",
      "period_start": "2026-01-01",
      "period_end": "2026-01-31",
      "statutory_due_date": "2026-02-15",
      "adjusted_due_date": "2026-02-15",
      "amount_nis": 1581.23,
      "currency": "ILS",
      "status": "upcoming",
      "reminders": [
        {
          "date": "2026-02-01",
          "days_before_due": 14,
          "channel_hint": "calendar",
          "note": "Prepare documents, verify amount, and pay before the adjusted due date."
        }
      ],
      "actions": [
        "Check the current advance assessment and payment voucher.",
        "Compare the estimate with actual profit and accountant guidance."
      ],
      "source_note": "Planning estimate. Verify classification, amount, due date, and payment channel in official Bituach Leumi systems before payment."
    }
  ]
}
```

## CLI examples

### Generate text output

```bash
python scripts/bituach-leumi-payment-scheduler-cli.py plan \
  --start-month 2026-01 \
  --months 3 \
  --payer-type self-employed \
  --income 10000
```

### Generate JSON output

```bash
python scripts/bituach-leumi-payment-scheduler-cli.py plan \
  --start-month 2026-01 \
  --months 3 \
  --payer-type self-employed \
  --income 10000 \
  --format json
```

### Generate ICS file

```bash
python scripts/bituach-leumi-payment-scheduler-cli.py plan \
  --start-month 2026-01 \
  --months 12 \
  --payer-type self-employed \
  --amount 1200 \
  --format ics \
  --output bituach-leumi-2026.ics
```

## Error reference

| Error | Meaning | Fix |
|---|---|---|
| `date must be YYYY-MM-DD, DD/MM/YYYY, or YYYY-MM` | date parser rejected the input | use `2026-01`, `2026-01-31`, or `31/01/2026` |
| `unsupported business type` | payer type not recognized | use `self-employed`, `employer`, `small-business`, or `consumer` |
| `unsupported adjustment policy` | adjustment mode not recognized | use `next-business-day`, `previous-business-day`, or `keep-date` |
| `months must be between 1 and 60` | generated range too short or too long | choose an operational planning range |
| `due_day must be between 1 and 28` | invalid monthly day | use a stable day that exists in every month |
| `monthly_income_nis or amount_override_nis is required` | self-employed estimate lacks amount basis | enter income estimate or official amount |
| `monthly_payroll_nis or amount_override_nis is required` | employer estimate lacks payroll basis | enter payroll estimate or official amount |
| `amount_override_nis cannot be negative` | negative payments are not supported | model refunds or credits outside this scheduler |
| `rates must be between 0 and 1` | custom policy has invalid rate | correct configuration |
| payment portal rejects payment | official system state differs from local plan | verify identity, balance, payment method, and due date in official channel |

## Security and privacy notes

- Avoid storing full Israeli ID numbers in exported calendar files.
- Use a short hint such as last four digits or internal payer code when needed.
- Do not put passwords, payment-card details, or one-time codes into JSON, CSV, ICS, or examples.
- Store payment confirmations in the business record system, not only in calendar events.
- Limit file access because schedules can reveal income, payroll, and debt information.

## Known limitations

- No official public scheduling API is invoked.
- Holiday dates are caller-supplied.
- Contribution estimates are simplified planning aids.
- Final amounts can change due to classification, minimum income, maximum income, credits, arrears, linkage, interest, collection costs, reserve duty, maternity leave, closure, or official updates.
- Employer payroll calculations must come from a payroll system or professional workpaper before submission.
