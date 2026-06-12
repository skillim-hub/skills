# Test Scenarios

Use these scenarios to validate calculations, advice wording, and edge-case handling.

| No. | Scenario | Expected handling |
| --- | --- | --- |
| 1 | Private-company options, Section 102 capital, held beyond preferred date | Capital gain treatment. |
| 2 | Same options sold before preferred date | Ordinary-income warning. |
| 3 | Missing trustee approval | Warning about trustee confirmation. |
| 4 | Unknown track | Conservative provisional result. |
| 5 | Section 102 income track with FMV at exercise | Split employment income and capital gain. |
| 6 | Section 102 income track without FMV at exercise | Validation error. |
| 7 | Public-company RSU with grant-date FMV | Employment component plus capital component. |
| 8 | Public-company RSU without grant-date FMV | Warning about missing split. |
| 9 | ESPP with purchase FMV | Discount and later appreciation split. |
| 10 | ESPP without purchase FMV | Validation error for non-102 split. |
| 11 | Section 3(i) consultant options | Ordinary-income treatment. |
| 12 | Non-employee grant | Conservative non-capital treatment. |
| 13 | Controlling shareholder | 30 percent capital gains rate warning. |
| 14 | Foreign-currency proceeds | FX conversion to ILS. |
| 15 | Negative sale price | Validation error. |
| 16 | Zero quantity | Validation error. |
| 17 | Underwater option sale | Zero taxable gain in sale model. |
| 18 | High other income above contribution cap | No additional National Insurance. |
| 19 | Capital gain crossing surtax threshold | Incremental surtax. |
| 20 | Manual preferred date | Use supplied date. |
| 21 | Trustee deposit date anchor | Add 24 months to deposit date. |
| 22 | Grant date anchor | Add 24 months to grant date. |
| 23 | Leap-day grant | Clamp month-end date correctly. |
| 24 | Batch async calculations | Return one result per input. |
| 25 | CLI JSON output | Valid UTF-8 JSON with scenario and result. |

| 25 | National Insurance 2026 employee-rate correction | Added employment income below reduced monthly bracket uses 4.27%. |
| 26 | National Insurance 2026 full-rate band | Added employment income above reduced bracket uses 12.17% until the cap. |
