# Test Scenarios

1. **Cardcom successful payment with document URL**
   - Input: `ResponseCode: 0`, `TranzactionId`, `ApprovalNumber`, `DocumentNumber`, `DocumentUrl`, gross amount ₪118.00.
   - Expected: Markdown receipt includes transaction ID, approval number, net ₪100.00, VAT ₪18.00, gross ₪118.00.

2. **Cardcom failed document creation after successful payment**
   - Input: successful transaction fields plus nested `DocumentInfo.ResponseCode: 999`.
   - Expected: payment record can be generated, but official document status stays flagged for manual follow-up.

3. **Tranzila payment request paid**
   - Input: transaction ID, confirmation code, status success, amount ₪250.00.
   - Expected: normalized receipt contains `gateway=tranzila`, original confirmation code, VAT split.

4. **Tranzila declined card**
   - Input: response status failed or declined with no transaction ID.
   - Expected: validation fails; no paid receipt output.

5. **Grow payment link created but not paid**
   - Input: payment link URL and process ID but no paid transaction status.
   - Expected: output is blocked or marked pending, not paid.

6. **Grow token charge success**
   - Input: `transactionId`, `transactionUniqueIdentifier`, status success, card suffix.
   - Expected: receipt uses masked card display and preserves idempotency reference in JSON notes.

7. **Pelecard successful debit**
   - Input: `StatusCode: "000"`, `PelecardTransactionId`, `VoucherId`, `ShvaResult: "000"`, masked card.
   - Expected: receipt includes voucher ID as approval reference.

8. **Pelecard pending authorization**
   - Input: pending endpoint response without final debit.
   - Expected: receipt generation stays pending until capture or debit confirmation.

9. **Osek Patur receipt**
   - Input: gross amount ₪400.00, exempt dealer flag.
   - Expected: VAT amount ₪0.00 and statement that VAT was not charged.

10. **B2B tax invoice above June 2026 threshold**
    - Input: net amount ₪5,500.00, VAT mode standard, no allocation number.
    - Expected: warning that allocation number is required for tax invoice handoff.

11. **Raw PAN leakage**
    - Input: payload includes `4580000000000000`.
    - Expected: validation fails with raw card number detection.

12. **Rounding edge case**
    - Input: gross amount ₪99.99 at 18% VAT.
    - Expected: net and VAT values add back to ₪99.99 after Decimal rounding.

13. **Refund record**
    - Input: original receipt plus negative amount or refund indicator.
    - Expected: direct paid receipt is rejected; operator is directed to create a credit/refund document.

14. **Unknown gateway payload**
    - Input: JSON with amount and customer only.
    - Expected: validation asks for the original gateway export or manual transaction ID mapping.
