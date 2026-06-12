# Troubleshooting Guide

Use this guide when forecast results look wrong, the CLI fails, or assumptions produce unrealistic outcomes.

---

## Forecast problems

### Closing balance is positive but free cash is negative

Cause: bank balance includes money reserved for VAT, income-tax advances, or Bituach Leumi.

Fix:

1. Review `protected_reserve`.
2. Confirm reserve percentages.
3. Reduce planned spending until `free_cash` is above buffer.
4. Avoid using protected reserves for operating costs unless a documented bridge plan exists.

### Tax payments appear but reserves are zero

Cause: manual payments exist, `reserve_mode` is `none`, or receipts are not marked taxable.

Fix:

1. Set `reserve_mode` to `cash`.
2. Mark relevant receipts as taxable.
3. Confirm `vat_rate`, `income_tax_advance_rate`, and `bituach_leumi_rate`.
4. Rerun forecast.

### VAT reserve seems too high

Cause: gross revenue may be taxed twice or net/gross flags are inconsistent.

Fix:

1. Confirm whether receipts include VAT.
2. Set `gross` consistently.
3. Use one convention across each scenario.
4. Add notes for exceptions.

### VAT reserve seems too low

Cause: revenue may be non-taxable, VAT cadence disabled, or rate zero.

Fix:

1. Check `taxable`.
2. Check `vat_cadence`.
3. Check `vat_rate`.
4. Confirm exclusions deliberately.

### Negative month is surprising

Cause: a large annual payment, card debit, or authority payment lands in that month.

Fix:

1. Sort transactions by amount.
2. Identify the largest cash-out and tax payment.
3. Add reserves earlier.
4. Split payments where realistic.
5. Run stress scenario.

---

## Input errors

| Error | Meaning | Fix |
|---|---|---|
| `INVALID_DATE` | Date is not `YYYY-MM-DD` | Use ISO date in JSON/CSV |
| `INVALID_MONTH` | Month is not `YYYY-MM` | Correct `start_month` |
| `NEGATIVE_AMOUNT` | Amount below zero | Use positive amounts and correct direction |
| `UNKNOWN_CADENCE` | Invalid VAT cadence | Use `none`, `monthly`, `bimonthly`, or `manual` |
| `CSV_SCHEMA_ERROR` | Missing columns or bad direction | Include `date`, `amount`, `direction`, `description` |
| `JSON_PARSE_ERROR` | Invalid JSON | Validate syntax |

---

## CLI problems

### Command not found

Run through Python:

```bash
budget-cashflow-forecaster --help
```

### Missing dependency

```bash
python -m pip install -r requirements-dev.txt
```

### File not found

Use an absolute path or run commands from the package root.

### Empty output

Run validation first:

```bash
budget-cashflow-forecaster validate input.json
```

---

## Test problems

- Run `python -m pytest scripts` from the package root.
- Install development requirements before testing.
- Compare money rounded to two decimals.
- Keep async tests deterministic and local.

---

## Accounting assumption problems

### עוסק פטור still shows reserves

Income-tax and Bituach Leumi can still matter even when VAT is disabled. Set those rates to zero only for household-only planning.

### Withholding tax missing

Enter the net receipt as bank cash. Track withheld tax separately.

### Bituach Leumi mismatch

Use exact voucher amounts when known. Use percentages only for planning.

### Advance percentage changed

Update `income_tax_advance_rate`, add a review date, and rerun all scenarios.

---

## Recovery action ladder

1. Collect overdue invoices.
2. Request deposits.
3. Reduce owner draw.
4. Delay discretionary purchases.
5. Split supplier payments.
6. Adjust inventory timing.
7. Review advance assumptions with an accountant.
8. Prepare approved credit before the gap.
9. Rerun forecast.
10. Save the revised scenario.


---

## Web-validated 2026 assumption checks

- Confirm VAT at 18% before use.
- For Bituach Leumi, avoid treating `bituach_leumi_rate` as a final statutory calculation. Use 2026 bracketed rates, exact vouchers, or dated payments where possible.
- Treat the Bank of Israel `edge.boi.gov.il` series API as the preferred exchange-rate integration reference.
