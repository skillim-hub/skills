# Troubleshooting

## Validation errors

### `principal must be positive`

Cause: `principal` is missing, zero, negative, or formatted as text that cannot be converted to a number.

Fix: Enter a positive amount without currency symbols.

```json
{"principal": "250000"}
```

### `prime_rate is required for prime loans`

Cause: The scenario uses `rate_type: "prime"` but does not include `prime_rate`.

Fix:

```json
{
  "rate_type": "prime",
  "prime_rate": "0.06",
  "prime_margin": "0.015"
}
```

### `quarterly repayment requires term_months divisible by 3`

Cause: A quarterly schedule needs complete quarters.

Fix: Use a term such as 12, 24, 36, 48, 60, 72, or 84 months.

## Output differs from lender quote

Possible causes:

| Cause | Diagnostic check | Fix |
|---|---|---|
| Daily interest | First payment differs slightly | Ask lender for day-count basis |
| CPI timing | CPI-linked rows differ | Confirm known-index vs published-index convention |
| Fees embedded in principal | Payment higher than model | Enter net disbursement and fees separately |
| Due date shift | Month-end dates differ | Confirm lender due-date rule |
| Rate rounded differently | Payment differs by small amount | Use exact rate from disclosure |
| Full grace instead of interest-only grace | Grace payments differ | Model full deferral separately or adjust manually |
| Insurance bundled | Payment higher than model | Separate insurance from debt service |

## Final balance not zero

Check:

1. Balloon percent.
2. Extra payment larger than remaining principal.
3. Rounding in the last period.
4. Quarterly term alignment.
5. Manual modifications to CSV after export.

The helper forces the final amortizing payment to close the balance when the scenario is standard.

## Payments are too high

Possible reasons:

- Rate entered as `6.5` instead of `0.065`.
- Term entered in years instead of months.
- Balloon omitted.
- Grace period omitted.
- CPI assumption too high.
- Fees are being compared as cash cost and not as part of installment.

## Payments are too low

Possible reasons:

- Annual interest entered as monthly interest.
- Prime margin omitted.
- CPI set to zero for a CPI-linked offer.
- Balloon percent entered but the quote had no balloon.
- Grace modelled even though the lender did not offer it.
- Fees not included in effective cost.

## Hebrew date problems

Use `DD/MM/YYYY` for Israeli-style input:

```json
{"start_date": "01/07/2026"}
```

The helper also accepts ISO format:

```json
{"start_date": "2026-07-01"}
```

Avoid slashes because the parser intentionally accepts only explicit hyphenated formats.

## CLI import errors

Install dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Run commands from the package root:

```bash
python scripts/loan_amortization_planner_cli.py validate scenario.json
```

## Pytest failures

1. Confirm Python 3.10 or newer.
2. Install development dependencies.
3. Run from the package root.
4. Avoid renaming `scripts/loan_amortization_planner_client.py`; the tests import that exact path.

## Decision-quality issues

### Only one scenario was prepared

Prepare at least a base and stress case for every variable-rate or CPI-linked loan.

### CPI assumption has no source

Document whether the assumption comes from internal planning, an economist forecast, historical average, or management stress case.

### Fees were excluded

Enter origination and early-payment fees to avoid selecting an offer that looks cheap only because costs were omitted.

### No liquidity check

Compare `max_payment` with actual available cash after payroll, rent, VAT, tax advances, supplier payments, and owner draw.


## Stale public-rate assumptions

Symptom: A new prime scenario still uses `0.06` as the base prime rate.

Cause: Older example assumptions were copied into a current 2026 scenario.

Fix: As of 2026-06-02, the verified Bank of Israel rate was 3.75% and the prime rule was Bank of Israel rate plus 1.5%, giving an implied base prime of 5.25%. Enter `0.0525` before adding any lender margin, and re-check the live source before relying on the result.
