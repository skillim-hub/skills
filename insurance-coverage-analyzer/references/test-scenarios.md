# Test scenarios

Use these concrete scenarios for validation.

## 1. Health lower premium lower drug limit

Input: Policy A ₪180/month drugs ₪2,000,000; Policy B ₪145/month drugs ₪1,000,000.

Expected: Cheaper policy flagged as weaker for medication.

## 2. Health same surgery higher deductible

Input: Policy A deductible ₪0; Policy B deductible ₪1,000.

Expected: Policy A better claim usability.

## 3. Health pre-existing condition

Input: Existing policy no back exclusion; new quote requires declaration.

Expected: High replacement-risk warning.

## 4. Health supplementary overlap

Input: Private surgery and supplementary surgery both present.

Expected: Duplicate flag plus practical value check.

## 5. Missing drugs outside basket

Input: Health policy lists surgery only.

Expected: Gap for drug coverage.

## 6. Serious illness duplicated

Input: Rider in health and life.

Expected: Duplicate coverage flag.

## 7. Home below mortgage requirement

Input: Bank requires ₪1,250,000; quote ₪1,100,000.

Expected: Mortgage compliance risk.

## 8. Home contents missing

Input: Structure-only policy for owner.

Expected: Contents gap.

## 9. Earthquake percentage

Input: Structure ₪1,200,000, deductible 10%.

Expected: Exposure ₪120,000.

## 10. Water restricted provider

Input: Insurer service provider only.

Expected: Usability limitation.

## 11. Domestic worker

Input: Cleaner weekly, no employer liability.

Expected: Employer liability gap.

## 12. Home office

Input: Freelancer has ₪45,000 equipment.

Expected: Business asset gap.

## 13. Valuables sublimit

Input: Jewelry ₪80,000, sublimit ₪20,000.

Expected: Underinsurance warning.

## 14. Third-party missing

Input: Client visits, no third-party liability.

Expected: Liability gap.

## 15. Mortgage life assignment

Input: Death benefit assigned to bank.

Expected: Bank-first warning.

## 16. Life stepped premium

Input: Starts ₪95/month then rises.

Expected: Multi-year cost warning.

## 17. Beneficiary ambiguity

Input: Estate vs spouse.

Expected: Clarification flag.

## 18. Smoking changed

Input: New quote assumes non-smoker but user smokes.

Expected: Underwriting risk.

## 19. Mixed policy types

Input: Health and home submitted.

Expected: No direct price ranking.

## 20. Missing premium

Input: Coverage complete but no price.

Expected: Continue with cost unknown.

## 21. Ambiguous date

Input: Renewal 01/02/26.

Expected: Request DD/MM/YYYY.

## 22. Duplicate IDs

Input: Two policies same policy_id.

Expected: Validation error.

## 23. Full Israeli ID exposed

Input: Input contains 123456789.

Expected: Sensitive identifier warning.

## 24. Brochure only

Input: No exclusions provided.

Expected: Request full wording.

## 25. First-year discount

Input: 25% discount year one.

Expected: Renewal cost warning.

## 26. CPI linkage

Input: One policy linked to CPI.

Expected: Long-term comparability warning.

## 27. Business key-person gap

Input: Business owner has loan no key-person cover.

Expected: Continuity gap.

## 28. Cancelled too early

Input: Old policy cancelled before underwriting.

Expected: Urgent gap warning.

## 29. Landlord home policy

Input: No loss-of-rent extension.

Expected: Landlord gap.

## 30. Waiting period mismatch

Input: 90 vs 180 days.

Expected: Policy with shorter waiting is more usable.
