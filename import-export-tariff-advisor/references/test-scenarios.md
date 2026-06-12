# Test Scenarios

Use these concrete scenarios to validate estimates, prompts, CLI behavior, and human review routing.

| # | Scenario | Inputs | Expected behavior |
|---:|---|---|---|
| 1 | Consumer headphones | 120 USD goods, 20 USD shipping, 3.70 FX, 0% duty, 0% purchase tax, 18% VAT | VAT on CIF; wireless warning |
| 2 | Business laptop | 1,000 USD goods, 60 USD shipping, 3.70 FX, 0% duty, 18% VAT | VAT shown; input VAT note for VAT-registered business |
| 3 | Wine for resale | 12,000 ₪ CIF, 12% duty, 20% purchase tax, 18% VAT | Purchase tax included in VAT base; alcohol warning |
| 4 | Returned repair | 150 EUR repair, 40 EUR return freight, 4.00 FX | Uses repair-value treatment only if proof exists |
| 5 | Warranty replacement | Replacement value 400 USD, no charge invoice | Requests original import/warranty documents |
| 6 | Mixed shipment | T-shirts and power banks in one invoice | Splits calculation by tariff line |
| 7 | Gift | 80 USD gift from relative | Does not assume automatic exemption |
| 8 | Sample | 30 units marked sample | Flags commercial quantity and tax risk |
| 9 | Used camera | 500 USD used camera | Accepts paid value but asks for proof |
| 10 | Vehicle part | Brake pads, 200 USD | Flags transport approval/purchase tax review |
| 11 | Cosmetics | Face cream, 300 USD | Flags Ministry of Health/cosmetics requirements |
| 12 | Food supplement | Vitamins, 150 USD | Flags food/supplement import review |
| 13 | Medical device | Blood pressure monitor | Flags medical device rules |
| 14 | Wi‑Fi router | 90 USD, personal import | Flags communications approval/exemption review |
| 15 | Commercial Wi‑Fi router batch | 50 units | Strong approval warning and broker review |
| 16 | Preferential origin | EU-origin goods with supplier declaration | Calculates general and preferential scenarios |
| 17 | Missing freight | Product price only | Warns estimate is incomplete |
| 18 | Zero exchange rate | USD values, FX 0 | Validation error |
| 19 | Rate entered as 18 | VAT rate 18 | Validation error; requires 0.18 |
| 20 | Specific duty | Alcohol with liters and alcohol % missing | Requests units and manual formula |
| 21 | Courier fee dispute | Actual bill has storage fee | Separates taxes from service fees |
| 22 | Customs code changed | Supplier HS differs from customs entry | Validates Israeli tariff suffix |
| 23 | Related-party import | Supplier is affiliated company | Flags valuation review |
| 24 | Drop-shipping | Israeli customer, foreign supplier | Checks importer of record and true transaction value |
| 25 | Returned goods without documents | Repair item returns without export proof | Warns full-value taxation risk |
| 26 | Multi-currency invoice | Goods in EUR, freight in USD | Requires separate FX rates or normalized ILS amounts |
| 27 | Incoterms DDP | Seller says all taxes included | Warns to verify importer of record and Israeli VAT invoice |
| 28 | Exempt dealer import | עוסק פטור imports equipment | Notes import VAT may still be payable and recovery may not apply |
| 29 | Nonprofit import | Donation goods | Flags exemption review, not automatic |
| 30 | CLI JSON output | Valid inputs with `--json` | Emits parseable JSON with rounded amounts |

| 31 | Temporary personal-import threshold | Estimate date around 01/06/2026 | Does not hard-code temporary relief; requires live source check |
