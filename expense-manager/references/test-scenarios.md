# Test Scenarios

Use these scenarios for manual QA, rule review, and regression testing.

| # | Scenario | Input summary | Entity | Expected category | Expected behavior |
|---:|---|---|---|---|---|
| 1 | Osek Patur phone bill | Partner ₪234 phone/internet | Osek Patur | `phone_internet` | 80% income-tax rate; ₪0 VAT recovery |
| 2 | Osek Murshe phone bill | Bezeq ₪117 internet | Osek Murshe | `phone_internet` | 80% income-tax rate; mixed-use VAT limitation |
| 3 | Accountant fee | CPA ₪117 retainer | Osek Murshe | `professional_services` | 100% category; VAT recovery when invoice valid |
| 4 | Domestic client coffee | Aroma ₪58 coffee with Israeli client | Osek Murshe | `domestic_hospitality` | 0% deduction and 0% VAT by default |
| 5 | Foreign guest dinner | Restaurant ₪300 foreign guest | Company | `foreign_guest_hospitality` | Flag guest details required |
| 6 | Google Ads | Google Ads ₪1,170 campaign | Osek Murshe | `marketing_advertising` | 100% business category; check invoice VAT source |
| 7 | Facebook Ads | Meta ₪800 campaign | Osek Murshe | `marketing_advertising` | 100% business category; missing receipt warning if absent |
| 8 | GitHub subscription | GitHub ₪117 private repos | Osek Murshe | `software_and_saas` | 100% business category; foreign VAT check if needed |
| 9 | AWS cloud hosting | AWS USD 50, FX 3.7 | Company | `software_and_saas` | Convert to ₪185 before tax logic |
| 10 | Home electricity | IEC ₪500 home office | Osek Murshe | `home_office` | Use configured percentage; blocker if missing |
| 11 | Arnona home office | Municipality ₪1,000 home office | Osek Patur | `home_office` | Deduct configured percentage; no VAT recovery |
| 12 | Office coworking rent | Cowork ₪1,170 office rent | Osek Murshe | `office_rent` | 100% category when dedicated workspace |
| 13 | Fuel | Paz ₪351 fuel | Osek Murshe | `vehicle` | 45% income-tax default; mixed-use VAT default |
| 14 | Parking | Pango ₪80 parking | Osek Murshe | `vehicle` | 45% income-tax default |
| 15 | Vehicle fine | Traffic ticket ₪250 | Company | `fines_penalties` | 0% deduction and 0% VAT |
| 16 | Laptop above threshold | KSP ₪5,000 laptop | Company | `capital_equipment` | No immediate deduction; depreciation suggested |
| 17 | Monitor below threshold | KSP ₪1,000 monitor | Osek Murshe | `capital_equipment` | Immediate expense allowed by helper default; info flag |
| 18 | Office paper | Kravitz ₪120 paper | Osek Murshe | `office_supplies` | 100% category |
| 19 | Client gift below cap | Gift shop ₪200 client gift | Osek Murshe | `gifts` | Deduct up to row amount; keep recipient list |
| 20 | Client gift above cap | Gift shop ₪480 client gift | Osek Murshe | `gifts` | Deduct only cap amount by helper default |
| 21 | Personal groceries | Supermarket ₪300 groceries | Osek Murshe | `personal` | 0% deduction |
| 22 | Gym subscription | Gym ₪250 | Osek Murshe | `personal` | 0% deduction |
| 23 | Business travel flight | El Al ₪2,000 flight abroad | Company | `business_travel_abroad` | Flag itinerary and receipts required |
| 24 | Hotel abroad | Hotel ₪3,000 conference abroad | Company | `business_travel_abroad` | Flag travel docs and caps review |
| 25 | Missing description | Unknown vendor ₪100 | Osek Murshe | `uncategorized_review` | Blocker flag |
| 26 | Missing receipt | Google Ads with no receipt number | Osek Murshe | `marketing_advertising` | Warning flag |
| 27 | Strict missing receipt | Same as #26 with strict mode | Osek Murshe | `marketing_advertising` | Adds strict blocker |
| 28 | Private consumer mode | Bezeq ₪117 internet | Private consumer | `phone_internet` | Tax and VAT totals forced to zero |
| 29 | Hebrew headers | `תאריך,ספק,סכום,תיאור` | Osek Murshe | Depends on text | CSV parser accepts Hebrew headers |
| 30 | Refund row | Credit-card refund for laptop | Osek Murshe | Original category after matching | Treat as reversal outside ordinary classification |

## Regression checklist

Run automated tests after each rule change:

```bash
pytest -q scripts/test_expense_manager_client.py
```

Manual acceptance:

- At least one scenario covers every major category.
- Osek Patur never shows recoverable VAT.
- Private consumer mode never shows tax or VAT recovery.
- Home-office rows require a configured percentage.
- Unknown rows stay blocked until mapped.
- UTF-8 Hebrew survives CSV round-trip.
