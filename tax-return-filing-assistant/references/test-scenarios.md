# Test Scenarios

Use these scenarios for manual QA and automated regression tests.

## 1. Salaried refund with two employers

- Tax year: 2025.
- Facts: salary only, two Forms 106, no tax coordination, wants refund.
- Expected forms: 135.
- Expected warnings: verify limitation period and attach both Forms 106.

## 2. Salaried refund with business income

- Tax year: 2025.
- Facts: salary plus freelance income, wants refund.
- Expected forms: 1301.
- Expected warning: Form 135 is not enough when business income exists.

## 3. Freelancer below Form 6111 planning threshold

- Facts: sole proprietor, business income, turnover ₪120,000, no employees, no suppliers.
- Expected forms: 1301.
- Expected checklist: profit and loss, receipts, expense ledger, advances.

## 4. Freelancer above Form 6111 planning threshold

- Facts: sole proprietor, business income, turnover ₪420,000.
- Expected forms: 1301 and 6111.
- Expected warning: verify current 6111 requirement.

## 5. Freelancer paid reportable suppliers

- Facts: sole proprietor, business income, paid suppliers, turnover ₪250,000.
- Expected forms: 1301 and 856.

## 6. Employer with no suppliers

- Facts: business has employees, no supplier payments.
- Expected forms: 126; 1301 only if individual annual return facts are present.

## 7. Employer with suppliers

- Facts: employer paid wages and freelance designers.
- Expected forms: 126 and 856, plus 1301/6111 only when annual/business facts require them.

## 8. Consumer landlord

- Facts: individual with rental income, no salary-only refund.
- Expected forms: 1301.
- Expected field help: rental income track and documents.

## 9. Foreign broker investor

- Facts: individual with foreign dividends and capital gains.
- Expected forms: 1301.
- Expected warning: foreign income/assets and professional review.

## 10. Old refund claim

- Facts: Form 135 for tax year six years back.
- Expected: limitation-date reminder and urgency warning.

## 11. Missing tax year

- Facts: user says “help with annual return” but no year.
- Expected validation error: TAX_YEAR_MISSING.

## 12. Invalid form number

- Input: field help for Form 9999.
- Expected error: FORM_UNKNOWN.

## 13. Unknown field

- Input: Form 856 field `shoe_size`.
- Expected error: FIELD_UNKNOWN.

## 14. Online Form 1301 deadline

- Facts: tax year 2025, online, not represented.
- Expected planning due date: 30/06/2026 with official-confirmation flag.

## 15. Paper Form 1301 deadline

- Facts: tax year 2025, paper, not represented.
- Expected planning due date: 29/05/2026 with official-confirmation flag.

## 16. Represented Form 1301 deadline

- Facts: tax year 2025, represented.
- Expected planning due date: representative-extension placeholder and official-confirmation warning.

## 17. Form 126 employee mismatch

- Facts: payroll total differs from Forms 106.
- Expected troubleshooting path: employee-by-employee reconciliation.

## 18. Form 856 expired certificate

- Facts: supplier certificate valid until 30-06, payments continue after.
- Expected validation: split payments by certificate validity.

## 19. Form 6111 imbalance

- Facts: balance sheet assets do not equal liabilities plus equity.
- Expected error: reconcile trial balance before filing.

## 20. Revenue mismatch with VAT

- Facts: P&L revenue differs from VAT reports.
- Expected warning: document exempt/out-of-scope/timing differences.

## 21. Donation credit

- Facts: Form 135 includes donation receipt.
- Expected: verify Section 46 recognition and taxpayer name.

## 22. New immigrant foreign income

- Facts: foreign dividends and claimed relief.
- Expected: verify relief period and reporting obligations.

## 23. Married couple with separate businesses

- Facts: both spouses self-employed.
- Expected: review spouse allocation and shared return rules.

## 24. Business opened mid-year

- Facts: opened 01-09, business income present.
- Expected: use actual period records, do not annualize without official instruction.

## 25. Negative supplier payment

- Facts: credit notes exceed invoices for one supplier.
- Expected: flag negative annual supplier total.

## 26. Payroll correction after year-end

- Facts: corrected salary in March after Forms 106 were issued.
- Expected: update Form 126 and reissue corrected employee documents where required.

## 27. Field list command

- Input: CLI `fields 1301`.
- Expected: list all available 1301 field IDs.

## 28. CLI profile recommendation

- Input: profile JSON for freelancer with turnover ₪500,000 and suppliers.
- Expected: JSON output includes 1301, 856, 6111.

## 29. Checklist generation

- Input: Form 135 scenario.
- Expected: checklist includes Form 106, bank details, refund support, limitation check.

## 30. Privacy filter

- Facts: user pasted full ID and bank number in notes.
- Expected: PERSONAL_DATA_RISK warning and request redaction.
