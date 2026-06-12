# Test Scenarios

Use these concrete scenarios for manual QA, examples, and acceptance testing. Amounts are illustrative.

1. Empty household budget: opening ₪10,000, no taxes, salary and rent only; expect no tax reserve.
2. Freelancer baseline with VAT: ₪23,600 gross receipt and ₪4,000 expense; expect VAT reserve from gross.
3. Bimonthly VAT: January and February revenue; expect accumulated reserve and later payment.
4. Delayed customer payment: move March receipt to April; expect lower March free cash.
5. Negative cash: opening ₪2,000 and expense ₪8,000; expect `negative_cash`.
6. Buffer warning: closing positive but below ₪15,000 buffer; expect `buffer_warning`.
7. Protected reserve exceeds closing balance; expect negative free cash.
8. Income-tax advances only: VAT disabled and 10% income-tax rate; expect tax reserve.
9. Bituach Leumi planning only: 12% rate; expect protected reserve.
10. עוסק פטור: VAT cadence `none`; expect no VAT reserve and threshold review note.
11. Retail supplier before sales: supplier paid before card settlement; expect cash pressure.
12. Foreign-currency receipt converted manually; expect ILS handling and FX note.
13. Withholding tax: enter net receipt; expect only net cash-in.
14. Owner draw: ₪9,000 cash-out; expect reduced free cash.
15. Annual insurance: ₪6,000 in March; expect March dip.
16. Loan repayment: ₪2,500 monthly; expect full outflow.
17. Card timing: purchase in January, bank debit in February; expect February cash-out.
18. Manual tax payment: known authority payment entered; expect dated outflow.
19. High growth: revenue doubles after three months; expect higher reserves.
20. Seasonal drop: no August revenue; expect lower free cash.
21. Missing date validation: `2026/01/10`; expect `INVALID_DATE`.
22. Negative amount validation: `-500`; expect `NEGATIVE_AMOUNT`.
23. Unsupported cadence: `quarterly`; expect `UNKNOWN_CADENCE`.
24. CSV import: one income and one expense; expect loaded forecast.
25. Async parity: sync and async forecast same input; expect identical rows.
26. No buffer: expect warning.
27. Missing input file: expect `MISSING_FILE`.
28. Non-taxable gift: expect no tax reserve.
29. Gross/net mismatch: two scenarios differ by VAT calculation; expect documented difference.
30. Annual cost plus delayed receipt: expect recovery action list.

Acceptance criteria:

- Validation errors are explicit.
- Monetary outputs round to two decimals.
- Tax assumptions are visible.
- Closing balance and free cash are both shown.
- No visual marks, image references, promotional wording, or creator metadata appear.
