# Test Scenarios

Use these scenarios for manual QA, CLI validation, and automated tests.

## 1. Routine active refill

Input: 12 days remain, repeats left, valid prescription, delivery requested.

Expected: routine urgency, pharmacy verification, stock and price check.

## 2. No repeats with enough supply

Input: 8 days remain, zero repeats.

Expected: doctor renewal path and follow-up within 2 business days.

## 3. No repeats with low supply

Input: 2 days remain, zero repeats.

Expected: urgent escalation and doctor message.

## 4. Expired prescription with repeats

Input: repeats remain but validity date passed.

Expected: doctor renewal path.

## 5. Missing active prescription

Input: active_visible false.

Expected: verify profile and request renewal.

## 6. Medication appears only in history

Expected: treat as inactive.

## 7. Pharmacy cannot see prescription

Expected: check synchronization and contact support.

## 8. Wrong child profile

Expected: stop and switch profile.

## 9. Missing caregiver consent

Expected: `CONSENT_MISSING`.

## 10. Caregiver pickup with consent

Expected: pickup authorization checklist.

## 11. Employee asks for help

Expected: logistics-only support.

## 12. Travel soon

Expected: include travel date and early dispensing question.

## 13. Holiday risk

Expected: sooner follow-up and phone escalation if supply is low.

## 14. Refrigerated medicine

Expected: cold-chain checklist.

## 15. Controlled medicine

Expected: official rules only.

## 16. Price mismatch

Expected: itemized price in ₪.

## 17. Stock unavailable

Expected: nearby branches and clinician question about alternatives.

## 18. Portal login failure

Expected: no credential collection.

## 19. Duplicate request risk

Expected: reference prior confirmation.

## 20. Delivery address mismatch

Expected: verify address or switch to pickup.

## 21. Renewal completed but no fulfillment

Expected: pharmacy stock and delivery/pickup verification.

## 22. Zero supply

Expected: urgent or emergency escalation depending symptoms.

## 23. Delivery unavailable by city

Expected: pickup or licensed local pharmacy.

## 24. Lab test required

Expected: ask which test is missing.

## 25. Multiple medications

Expected: separate case per medication.

## 26. Full ID shared

Expected: redact and minimize.

## 27. Freelancer expense record

Expected: date, vendor, amount in ₪, category only.

## 28. Wrong medication submitted

Expected: stop and correct with clinic or pharmacy.

## 29. Failed cold-chain delivery

Expected: pharmacy instruction before use.

## 30. Repeated portal-pharmacy mismatch

Expected: HMO support and no duplicate requests.


## 31. Be prescription support unclear

Expected: verify the current app, branch, or pharmacist before using Be for prescription delivery.

## 32. Newpharm current support unclear

Expected: treat Newpharm as legacy/local naming and verify the licensed pharmacy before use.

## 33. VAT reference requested

Expected: state that the general Israeli VAT rate was verified as 18% in 2026, but do not calculate VAT automatically for receipts.

## 34. Public API requested

Expected: state that no public prescription-renewal API endpoints or webhook event names were confirmed; keep manual review.
