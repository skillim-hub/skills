# API and Regulation Reference

This skill does not call a live Israeli government API. It provides a structured workflow, CLI, and local typed helper for classifying deposits, calculating final settlements, creating validated deposit records, and exporting reconciliation files. Production invoicing must remain inside an approved bookkeeping or invoicing system.

Verify current rules before production use. Israeli VAT rates, invoice allocation thresholds, cash restrictions, and reporting procedures can change.

## Israeli reference map

| Topic | Official source to verify | Production checks |
|---|---|---|
| VAT liability and tax invoices | Value Added Tax Law, 5736-1975; VAT Regulations; Israel Tax Authority guidance | Tax event timing, invoice deadline, taxable/exempt/zero-rated status, VAT rate |
| Bookkeeping documents | Income Tax Instructions (Bookkeeping), 5733-1973 and related circulars | Receipt numbering, cancellation, correction, retention period, audit trail |
| VAT-exempt dealer | Israel Tax Authority guidance for עוסק פטור | Annual threshold, receipt-only workflow, status-change rules |
| Israel Invoice allocation | Israel Tax Authority חשבונית ישראל / allocation number process | Current threshold, portal/API flow, allocation number storage, fallback process |
| Cash restrictions | Law for Reducing the Use of Cash, 5778-2018 | Current permitted ceilings, business/consumer distinction, exceptions |
| Consumer refunds | Consumer Protection Law, 5741-1981 and regulations | Cancellation windows, refund fees, disclosure, service-specific exceptions |
| Credit invoices | VAT Regulations and bookkeeping instructions | Required original invoice reference, reason, date, VAT-period impact |
| Electronic records | Bookkeeping and electronic document instructions | Integrity, backup, export, retention, access control |

## Local helper API

The helper lives in two forms:

- `scripts/prepayment_deposit_handler_client.py` for the required slug file.
- `scripts/prepayment_deposit_handler_client.py` for direct Python imports.

### Import example

```python
from prepayment_deposit_handler_client import (
    LineItem,
    PrepaymentDepositClient,
)

client = PrepaymentDepositClient()
result = client.settle(
    [LineItem("Consulting project", 1, "12000", "0.18")],
    deposit="3000",
    business_type="osek_murshe",
)
print(result.as_dict())
```

## Data model: Money

### Request

```json
{
  "amount": "2500.00",
  "currency": "ILS"
}
```

### Response

```json
{
  "amount": "2500.00",
  "currency": "ILS"
}
```

### Validation

| Field | Rule |
|---|---|
| `amount` | Decimal-compatible, non-negative, rounded half-up to two decimals |
| `currency` | Uppercase code, default `ILS` |

## Data model: LineItem

### Request

```json
{
  "description": "Website milestone",
  "quantity": "1",
  "unit_price_ex_vat": "10000.00",
  "vat_rate": "0.18"
}
```

### Response

```json
{
  "description": "Website milestone",
  "quantity": "1",
  "unit_price_ex_vat": "10000.00",
  "vat_rate": "0.18",
  "net": "10000.00",
  "vat": "1800.00",
  "gross": "11800.00"
}
```

## Data model: DepositRecord

### Request

```json
{
  "deposit_id": "DEP-2026-0007",
  "contract_id": "ORD-4431",
  "received_date": "15/03/2026",
  "amount": "3000.00",
  "payer_name": "Example Customer Ltd.",
  "payer_tax_id": "515000000",
  "payee_name": "Example Studio",
  "payee_tax_id": "012345678",
  "nature": "advance_for_taxable_supply",
  "payment_method": "bank_transfer",
  "currency": "ILS",
  "refundable": false,
  "applied_amount": "0.00",
  "reference": "Bank ref 883911"
}
```

### Response

```json
{
  "deposit_id": "DEP-2026-0007",
  "contract_id": "ORD-4431",
  "received_date": "2026-03-15",
  "amount": {"amount": "3000.00", "currency": "ILS"},
  "payer": {"name": "Example Customer Ltd.", "tax_id": "515000000", "email": null, "address": null},
  "payee": {"name": "Example Studio", "tax_id": "012345678", "email": null, "address": null},
  "nature": "advance_for_taxable_supply",
  "payment_method": "bank_transfer",
  "refundable": false,
  "applied_amount": {"amount": "0.00", "currency": "ILS"},
  "remaining": {"amount": "3000.00", "currency": "ILS"},
  "reference": "Bank ref 883911",
  "notes": null
}
```

## Classification API equivalent

### Request

```python
from prepayment_deposit_handler_client import PrepaymentDepositClient

client = PrepaymentDepositClient()
result = client.classify(
    nature="security_deposit_held_in_trust",
    business_type="osek_murshe",
    refundable=True,
)
print(result.as_dict())
```

### Response

```json
{
  "receive_documents": ["receipt"],
  "settlement_documents": ["refund_receipt", "final_tax_invoice"],
  "timing_notes": [
    "Treat as money held against an obligation until it becomes consideration for a taxable supply."
  ],
  "risk_notes": [
    "Do not recognize VAT or revenue merely because a refundable security deposit was received."
  ],
  "controls": [
    "Use a unique deposit ID and link it to the quote, order, receipt, and final invoice.",
    "Reconcile the deposit liability/advance balance at month-end.",
    "Store customer approval, refund terms, payment reference, and settlement evidence."
  ]
}
```

## Settlement API equivalent

### Request

```python
from prepayment_deposit_handler_client import LineItem, PrepaymentDepositClient

client = PrepaymentDepositClient()
result = client.settle(
    [LineItem("Consulting project", 1, "12000", "0.18")],
    deposit="3000",
    business_type="osek_murshe",
)
print(result.as_dict())
```

### Response

```json
{
  "subtotal_ex_vat": {"amount": "12000.00", "currency": "ILS"},
  "vat": {"amount": "2160.00", "currency": "ILS"},
  "total_inc_vat": {"amount": "14160.00", "currency": "ILS"},
  "deposit_applied": {"amount": "3000.00", "currency": "ILS"},
  "balance_due": {"amount": "11160.00", "currency": "ILS"},
  "overpayment": {"amount": "0.00", "currency": "ILS"},
  "recommended_documents": ["final_tax_invoice", "receipt"],
  "warnings": [
    "Confirm whether the deposit should already have been tax-invoiced under the applicable VAT timing rule."
  ],
  "journal_hint": [
    "Debit deposit liability/advance account for the applied amount.",
    "Credit customer balance or cash settlement for the balance due.",
    "Recognize VAT output according to the final tax invoice and prior tax invoices, avoiding double VAT."
  ]
}
```

## Enumerations

### Deposit natures

| Value | Meaning | Hebrew |
|---|---|---|
| `advance_for_taxable_supply` | Advance on taxable supply | מקדמה על חשבון עסקה חייבת |
| `security_deposit_held_in_trust` | Refundable security deposit | פיקדון ביטחון מוחזר |
| `refundable_booking_deposit` | Refundable booking deposit | מקדמת הזמנה מוחזרת |
| `non_refundable_booking_fee` | Non-refundable booking fee | דמי שריון שאינם מוחזרים |
| `retention_held_by_customer` | Customer retention | עיכבון אצל הלקוח |
| `gift_card_or_credit_balance` | Gift card or credit balance | שובר / יתרת זכות |

### Business types

| Value | Meaning |
|---|---|
| `osek_murshe` | VAT-registered business |
| `osek_patur` | VAT-exempt dealer |
| `amutah_or_malkar` | Non-profit/Malkar style entity; verify separately |
| `consumer` | Consumer context |

### Payment methods

| Value | Meaning |
|---|---|
| `cash` | Cash |
| `credit_card` | Credit card |
| `bank_transfer` | Bank transfer |
| `check` | Check |
| `digital_wallet` | Bit, PayBox, or similar wallet |
| `other` | Other |

## CLI request/response examples

### Classify a refundable security deposit

```bash
python scripts/prepayment-deposit-handler-cli.py classify \
  --nature security_deposit_held_in_trust \
  --business-type osek_murshe \
  --refundable
```

Expected output includes:

```json
{
  "receive_documents": ["receipt"],
  "settlement_documents": ["refund_receipt", "final_tax_invoice"]
}
```

### Calculate a final settlement

```bash
python scripts/prepayment-deposit-handler-cli.py settle \
  --line "Consulting:1:12000:0.18" \
  --deposit 3000 \
  --business-type osek_murshe
```

Expected balance due: `11160.00`.

### Create a deposit record and CSV

```bash
python scripts/prepayment-deposit-handler-cli.py record \
  --deposit-id DEP-2026-0007 \
  --contract-id ORD-4431 \
  --received-date 15/03/2026 \
  --amount 3000 \
  --payer-name "Example Customer Ltd." \
  --payee-name "Example Studio" \
  --nature advance_for_taxable_supply \
  --payment-method bank_transfer \
  --output-csv deposits.csv
```

## Error table

| Error text | Cause | Corrective action |
|---|---|---|
| `Money amount cannot be negative` | Negative amount passed where positive money is required | Enter a positive amount and model refunds through refund workflow |
| `VAT rate must be between 0 and 1` | VAT entered as `18` instead of `0.18` | Use decimal rate format |
| `Line item quantity must be positive` | Quantity is zero or negative | Correct quantity |
| `Line item price cannot be negative` | Negative price used as discount | Represent discount as its own documented workflow or reduce price before calculation |
| `At least one line item is required` | Settlement has no invoice lines | Add supplied goods/services |
| `Applied amount cannot exceed deposit amount` | Deposit record over-applied | Correct the application or split records |
| `Currency mismatch` | Combined ILS with another currency | Convert and document exchange rate first |
| `Date must be YYYY-MM-DD, DD/MM/YYYY, or DD/MM/YYYY` | Unsupported date format | Use `2026-03-15` or `15/03/2026` |
| `Line item must be description:quantity:unit_price_ex_vat[:vat_rate]` | CLI line syntax invalid | Use colon-delimited line syntax |

## Production integration controls

- Keep official invoice and receipt numbering inside the bookkeeping system.
- Treat helper output as a classification, calculation, and checklist layer.
- Persist helper output with timestamp, user ID, source document IDs, and hash where possible.
- Require human approval before tax invoice issuance.
- Store Israel Invoice allocation number, request ID, response time, and error evidence where applicable.
- Re-run settlement after every price change, cancellation, refund, credit note, or partial delivery.



## Verified 2026 values

| Parameter | Verified value | Implementation note |
|---|---:|---|
| Standard VAT rate | 18% | Default helper rate remains `0.18`; keep configurable |
| Israel Invoice threshold, 2025 | ₪20,000 before VAT | Allocation number required as condition for input VAT deduction above threshold |
| Israel Invoice threshold, 01/01/2026 to 31/05/2026 | ₪10,000 before VAT | Applies to qualifying tax invoices |
| Israel Invoice threshold, from 01/06/2026 | ₪5,000 before VAT | Applies to qualifying tax invoices |
| VAT-exempt dealer ceiling, 2026 | ₪122,833 annual turnover | Verify yearly |
| Consumer cancellation fee | 5% or ₪100, lower of the two | Applies only where the statutory cancellation framework applies |
| Cash-law review trigger | Business transaction above ₪6,000 | Use official simulator and current guidance |

## Webhook events

No official webhook event names were confirmed for this non-integrating helper. The official materials reviewed describe allocation-number services and API documentation for software providers, not a webhook contract for this skill.
