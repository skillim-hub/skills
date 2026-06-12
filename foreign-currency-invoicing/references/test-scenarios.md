# Test Scenarios

Use these scenarios for manual QA, automated test planning, and acceptance checks.

| ID | Scenario | Input highlights | Expected result |
|---:|---|---|---|
| 1 | USD Israeli customer | USD, standard VAT, rate 3.70 | VAT calculated in ₪ at standard rate |
| 2 | EUR Israeli customer | EUR, standard VAT, rate 4.02 | NIS base equals EUR net times 4.02 |
| 3 | USD foreign-resident service | zero-rate with note | VAT equals 0 and no missing-evidence warning |
| 4 | USD zero-rate without note | zero-rate no note | Warning requests supporting evidence |
| 5 | Exempt line | exempt category | VAT equals 0 and exempt breakdown populated |
| 6 | Reverse charge | reverse_charge category | VAT equals 0 and evidence note expected |
| 7 | Outside scope | out_of_scope category | VAT equals 0 and reason note expected |
| 8 | Mixed VAT categories | standard plus zero | Only standard line contributes to VAT |
| 9 | JPY unit 100 | rate 2.40, unit 100 | Effective rate is 0.024000 ₪ per JPY |
| 10 | ILS invoice | no exchange rate | Rate defaults to 1 |
| 11 | Missing non-ILS rate | USD no exchange rate | Validation error |
| 12 | Bad currency | `US` | Validation error |
| 13 | Negative quantity | quantity -1 | Validation error |
| 14 | Discount too large | discount exceeds line gross | Validation error |
| 15 | Date with slashes | 02/06/2026 | Parsed as 2 June 2026 |
| 16 | ISO timestamp | 2026-06-02T10:00:00 | Parsed as 2 June 2026 |
| 17 | 2024 VAT | 31/12/2024 | Default VAT 17% |
| 18 | 2025 VAT | 01/01/2025 | Default VAT 18% |
| 19 | JSON Bank of Israel payload | `currentExchangeRate` | Parsed rate object |
| 20 | XML Bank of Israel payload | `CURRENCYCODE`, `RATE`, `UNIT` | Parsed rate object |
| 21 | Empty API payload | empty string | Rate lookup error |
| 22 | Weekend fallback | first day fails, previous day succeeds | Previous published rate selected |
| 23 | CLI create | valid line JSON | JSON output includes `id` |
| 24 | CLI show | id from create | Stored JSON is returned |
| 25 | Environment line input | `FCI_LINES_JSON` set | CLI uses environment lines |
| 26 | Batch example | batch JSON array | One result per job |
| 27 | Rounding per line | small fractional lines | Per-line totals match policy |
| 28 | Manual override | approved manual rate | Source retained as manual |
| 29 | Credit workflow | negative correction requested | Use credit-invoice process rather than editing original |
| 30 | Accounting export | DD/MM/YYYY, ₪ display | Israeli-facing output is localized |

## Acceptance criteria

- Every non-standard VAT line has an evidence note or a warning.
- Every non-ILS invoice has a rate source and rate date.
- Every JPY-style unit quote divides the rate by the unit before conversion.
- CLI create/show works with an extracted invoice id.
- Python import works after `pip install -e .` without path edits.

21. Parse a Bank of Israel SDMX CSV payload for `RER_USD_ILS` and verify the date and rate.
22. Build a date-specific SDMX rate URL and confirm it includes `startPeriod`, `endPeriod`, and `format=csv`.
