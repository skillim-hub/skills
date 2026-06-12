# Troubleshooting

## Calculation issues

| Problem | Diagnostic step | Correction |
|---|---|---|
| Final balance is not zero | Inspect the last schedule row | Adjust the final principal and payment for rounding |
| Monthly payment differs from a card-provider screen | Compare fee timing and rounding policy | Align whether fees are upfront, per installment, or included in principal |
| Total fees look too high | Check both fixed and percentage fees | Remove duplicated acquirer or admin fee inputs |
| Effective annual cost is unexpectedly high | Inspect upfront fees and short terms | Show customer impact and consider reducing fees |
| Down payment does not reduce payments | Check `down_payment` and `financed_amount` | Confirm down payment is less than cash price and included in total paid |

## Date issues

| Problem | Diagnostic step | Correction |
|---|---|---|
| Date parsing fails | Check separators and day order | Use `DD/MM/YYYY`, `DD-MM-YYYY`, or `YYYY-MM-DD` |
| Payment day 31 becomes 30 or 28 | Check target month length | Treat clipping to month end as expected behavior |
| Missing schedule dates | Check `first_due_date` | Add the first date or disclose a clear date-setting rule |

## Disclosure issues

| Problem | Diagnostic step | Correction |
|---|---|---|
| Customer sees only monthly payment | Review checkout layout | Show cash price and total paid next to the plan |
| Plan says zero interest but includes fees | Inspect `finance_charge` | Replace wording with fee-inclusive cost disclosure |
| VAT status is unclear | Check `vat_included` | Use VAT-inclusive consumer pricing or mark business terms clearly |
| Refund estimate is treated as final | Review support process | Apply contract, current law, acquirer rules, and bookkeeping approval |

## CLI issues

| Problem | Cause | Correction |
|---|---|---|
| Command is not found | Package was not installed | Run `pip install -e .` |
| Import fails in examples | Virtual environment is not active | Activate the environment and install the package |
| JSON escapes Hebrew | Custom script omitted `ensure_ascii=False` | Use `json.dumps(payload, ensure_ascii=False, indent=2)` |

## Test issues

| Problem | Cause | Correction |
|---|---|---|
| Async tests fail | Missing async test plugin | Install `pytest-asyncio` from `requirements-dev.txt` |
| Snapshot differs by one agorah | Rounding policy changed | Update expected values only after accounting approval |
| Compile check creates cache files | Python writes bytecode | Delete cache folders before bundling release artifacts |

## Web-validated 2026 troubleshooting additions

| Symptom | Likely cause | Resolution |
|---|---|---|
| Israel Invoice allocation number is missing | B2B invoice workflow exceeds the 2026 threshold | Check whether the pre-VAT amount is over ₪5,000 after 01/06/2026 and route to accounting. |
| Cancellation fee appears too high | Fee was entered manually instead of capped | Use `statutory_cancellation_fee_cap`, then verify the legal cancellation context. |
| VAT split differs by one agora | Rounding order differs between systems | Round net, VAT, and gross with `ROUND_HALF_UP` and document the source amount. |
