# Test Scenarios

Use these concrete scenarios for QA and regression testing.

1. Local plumber in Rishon LeZion, calls, ₪3,000, Hebrew, no website.
2. Independent accountant in Petah Tikva, leads, ₪6,000, Hebrew and Russian, tax advice.
3. Dental clinic in Haifa, bookings, ₪15,000, Hebrew and Arabic, health flag.
4. Ecommerce skincare store, sales, ₪12,000, Hebrew and Arabic, cosmetics flag.
5. Boutique bakery in Jerusalem, store visits, ₪4,000, Hebrew and English.
6. Freelance designer B2B, leads, ₪5,000, Hebrew and English.
7. Real estate broker in Netanya, leads, ₪9,000, real estate flag.
8. Online course for teens, sales, ₪8,000, minors flag.
9. Insurance agency, leads, ₪10,000, Hebrew and Russian, finance flag.
10. Physiotherapy clinic, bookings, ₪7,500, health flag.
11. Arabic-speaking renovation contractor in the Galilee, calls, ₪4,500, Arabic and Hebrew.
12. Tel Aviv restaurant launch, store visits, ₪6,500, Hebrew and English.
13. Small jewelry ecommerce, sales, ₪2,500, low AOV.
14. Tourist day-trip provider, bookings, ₪8,000, English and Hebrew.
15. Career coach, leads, ₪3,500, Hebrew.
16. Environmental product with green claims, sales, ₪9,000, environmental flag.
17. Alcohol delivery promotion, sales, ₪10,000, alcohol flag.
18. Prize giveaway, awareness, ₪5,000, lottery flag.
19. WhatsApp-only lead campaign, ₪2,000, direct-message consent risk.
20. Remarketing-heavy ecommerce with customer lists, ₪20,000, privacy risk.
21. Very small budget local tutor, ₪700, Hebrew.
22. Locksmith campaign without AOV, calls, ₪2,500.
23. Ecommerce with invalid gross margin 1.4.
24. Consultant campaign with unsupported language code fr.
25. Russian ads but no Russian-speaking service staff.
26. Arabic landing page with Hebrew-only sales team.
27. Search campaign attracting students and job seekers.
28. Health ad using “guaranteed cure”.
29. Discount offer without end date or material conditions.
30. Landing page with inaccessible form and no privacy notice.

## Expected checks

- Flag regulated sectors and unsupported claims.
- Warn on tiny budgets and channel fragmentation.
- Require privacy review for remarketing and direct messages.
- Detect unsupported language codes and service-language mismatches.
- Avoid profitability claims without AOV and gross margin.
- Require accessibility review for landing pages and forms.

## CLI smoke tests

```bash
python scripts/advertising-campaign-planner-cli.py plan --business "מנעולן" --goal calls --monthly-budget 2500 --language he --city "חולון"
python scripts/advertising-campaign-planner-cli.py estimate-roi --spend 4500 --clicks 900 --conversions 30 --avg-order-value 600 --gross-margin 0.45
python scripts/advertising-campaign-planner-cli.py validate --business "Clinic" --goal bookings --monthly-budget 10000 --language he --regulated-flag health --offer "Guaranteed cure"
python scripts/advertising-campaign-planner-cli.py template --language he
```
