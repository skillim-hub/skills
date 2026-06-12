# Test Scenarios

Use these scenarios to validate output quality, CLI behavior, and edge-case handling.

1. Micro employer with 3 employees, ₪1,200 monthly budget, no existing benefits. Expected: mandatory checks first and small capped wallet.
2. Café with 8 part-time workers, shift model, ₪3,200 budget. Expected: pro-rata meal benefit and no premium package before basics.
3. Hybrid tech company with 22 employees and ₪1,200 per employee. Expected: meals, Keren Hishtalmut review, wellness, learning, quarterly review.
4. Remote team in peripheral cities. Expected: coverage warning and reimbursement fallback.
5. Employer asks for uncapped meals. Expected: reject uncapped design and add daily/monthly caps.
6. Senior-only Keren Hishtalmut. Expected: equity warning and transparent criteria.
7. Employee compares ₪600 gross salary and ₪600 meal benefit. Expected: net salary vs usable value comparison.
8. Freelancer earns ₪28,000 with 1-month buffer. Expected: emergency reserve before premium perks.
9. Freelancer earns ₪45,000 with 6-month buffer. Expected: pension, study fund, insurance, equipment reserve.
10. Consumer has ₪900 monthly subscriptions. Expected: cancel unused subscriptions before adding perks.
11. Contractor included in meal card. Expected: classification risk.
12. Wellness reimbursement requests diagnosis. Expected: privacy warning and data minimization.
13. Gym-only benefit for diverse team. Expected: flexible wellness wallet.
14. No budget supplied. Expected: three tiers and assumptions.
15. Terminated employee remains in provider file. Expected: HR-provider reconciliation and termination rule.
16. Payroll cannot code benefit. Expected: component setup and accountant/payroll review.
17. VAT invoice missing. Expected: require invoice and bookkeeping flow.
18. Employee on unpaid leave. Expected: leave rules and provider suspension.
19. Reserve duty edge case. Expected: legal/payroll review before exclusion.
20. Paid interns included. Expected: status and eligibility review.
21. New employee with active pension starts 01-07-2026. Expected: fund details and start-date compliance.
22. New employee without prior pension. Expected: note different timing and verify with payroll/legal.
23. High utilization but low satisfaction. Expected: provider quality and coverage review.
24. Provider fee increase at renewal. Expected: compare total cost and cancellation terms.
25. Bilingual policy required. Expected: Hebrew DD-MM-YYYY and ₪ formatting.
26. Owner-manager wants personal perks through company. Expected: separate owner/company analysis and accountant review.
27. Branches in Haifa, Beer Sheva, and Jerusalem. Expected: coverage by branch.
28. Home-office equipment stipend. Expected: ownership, caps, tax/payroll/accounting review.
29. Learning budget abuse. Expected: eligible categories and approval.
30. Migration from ad hoc reimbursements. Expected: inventory, freeze, policy, payroll mapping, grandfathering.


## Web-validated final-pass scenarios

## 31. VAT rate check

- Invoice date: 15/01/2026.
- Expected: use 18% VAT unless a specific exemption or zero-rate applies.

## 32. Israel Invoice allocation check

- Supplier invoice before VAT: ₪12,000 on 15/01/2026.
- Expected: require allocation-number workflow review.

## 33. Unknown webhook name

- Vendor says webhooks are available but no event list is public.
- Expected: mark webhook names as not publicly confirmed and request vendor documentation.

## 34. Self-employed pension bracket

- Freelancer asks for exact 2026 mandatory pension amount.
- Expected: apply 4.45% and 12.55% bracket logic only after verifying current average wage and exemptions.
