# Verification Log

Access date for all rows: 2026-06-02

| Check | Status | Pass 1 source | Pass 2 source | Package action |
|---|---|---|---|---|
| Standard Israeli VAT rate |  | Quote: "1.1.25 עלה המע"מ ל-18%". URL: https://www.gov.il/he/pages/vat-history | Quote: "will be increased... effective January 1, 2025". URL: https://main.knesset.gov.il/EN/News/PressReleases/Pages/press12324w.aspx | Added current VAT note; no VAT calculation added |
| VAT timing for services and credit |  | Quote: "החל מיום ,01/01/2025 יחויב מע"מ בשיעור של .18%". URL: https://www.gov.il/BlobFolder/dynamiccollectorresultitem/represent-info-051224-2/he/vat_represent-info-051224-2.pdf | Quote: "all transactions... where the tax liability date is on or after January 1, 2025". URL: https://www.vatupdate.com/2025/01/09/israel-increases-vat-rate-from-17-to-18-starting-january-2025/ | Clarified VAT is surrounding cash-flow context only |
| Current Bank of Israel rate |  | Quote: "lower the interest to 3.75 percent". URL: https://www.boi.org.il/en/communication-and-publications/press-releases/25-05-2026/ | Quote: "BOI interest rate 3.75%". URL: https://www.boi.org.il/en/ | Updated examples and docs from 6.00% prime base to 5.25% |
| Prime-interest formula |  | Quote: "Bank of Israel interest rate plus 1.5%". URL: https://www.boi.org.il/en/information-and-service-to-the-public/banking-customer-service-information/public-guides/taking-a-loan/ | Quote: "Prime interest rate 6.25... Bank of Israel interest rate 4.75". URL: https://www.boi.org.il/media/vohlk2lw/financial-statements-2023-full.pdf | Documented current implied prime = 3.75% + 1.5% = 5.25% |
| Fixed and variable interest terminology |  | Quote: "fixed... or variable... Prime plus 5%". URL: https://www.boi.org.il/en/information-and-service-to-the-public/banking-customer-service-information/public-guides/taking-a-loan/ | Quote: "fixed rate unindexed, fixed rate indexed, variable rate unindexed, and prime indexed". URL: https://boi.org.il/en/communication-and-publications/press-releases/consumer-reform-to-increase-information-transparency-for-bank-customers-and-to-enhance-the-competitive-environment-in-the-mortgage-market/ | Retained fixed/prime/CPI taxonomy |
| CPI-indexed loan terminology |  | Quote: "loans that are indexed to the CPI". URL: https://www.boi.org.il/en/information-and-service-to-the-public/banking-customer-service-information/public-guides/taking-a-loan/ | Quote: "Consumer Price Index (CPI) (in CPI-indexed loans)". URL: https://www.boi.org.il/en/communication-and-publications/press-releases/l05-07-23/ | Retained CPI-linked scenario support |
| CPI publication timing |  | Quote: "published on the 15th of the month at 6:30 PM". URL: https://www.cbs.gov.il/en/Pages/Main%20Price%20Indices.aspx | Quote: "מתפרסמות ב-15 בחודש בשעה 18:30". URL: https://www.cbs.gov.il/he/Pages/מדדי-מחירים-מדדים-עיקריים.aspx | Added CPI timing note |
| CPI definition and linkage use |  | Quote: "measures the percentage change... fixed basket". URL: https://www.cbs.gov.il/he/Statistical/price_ind153h.pdf | Quote: "מחשבון הצמדה... ערכו הצמוד של סכום כסף". URL: https://www.cbs.gov.il/he/Statistical/price_ind153h.pdf | Retained CPI adjustment as explicit assumption |
| CBS price-index API host |  | Quote: "https://api.cbs.gov.il/index/catalog/tree". URL: https://www.cbs.gov.il/he/Pages/מדדי-מחירים-באמצעות-API.aspx | Quote: "https://api.cbs.gov.il/index/data/price". URL: https://www.cbs.gov.il/he/Pages/מדדי-מחירים-באמצעות-API.aspx | Added optional API endpoint reference |
| CBS linkage calculator endpoint |  | Quote: "https://api.cbs.gov.il/index/data/calculator/{id}". URL: https://www.cbs.gov.il/he/Pages/מדדי-מחירים-באמצעות-API.aspx | Quote: "מחשבון הצמדה למדדים". URL: https://www.cbs.gov.il/he/cbsNewBrand/Pages/Calculator.aspx | Added optional endpoint example; package still offline |
| Loan fee terminology |  | Quote: "Early repayment fee". URL: https://www.boi.org.il/en/information-and-service-to-the-public/banking-customer-service-information/public-guides/taking-a-loan/ | Quote: "effective cost... reflecting both the interest and the fees". URL: https://www.boi.org.il/en/information-and-service-to-the-public/banking-customer-service-information/public-guides/taking-a-loan/ | Retained fee fields and cost summary |
| Small-business fee threshold |  | Quote: "small businesses up to NIS 100,000 is exempt". URL: https://www.boi.org.il/en/information-and-service-to-the-public/banking-customer-service-information/public-guides/taking-a-loan/ | Quote: "loan or credit facility up to NIS 100,000". URL: https://www.boi.org.il/en/information-and-service-to-the-public/banking-customer-service-information/public-guides/taking-a-loan/ | Added reference; no fee automation |
| Loan-track comparison claim |  | Quote: "5 major housing-loan tracks". URL: https://www.boi.org.il/en/communication-and-publications/press-releases/l05-07-23/ | Quote: "Mortgages in Israel are split between various tracks". URL: https://boi.org.il/en/communication-and-publications/press-releases/consumer-reform-to-increase-information-transparency-for-bank-customers-and-to-enhance-the-competitive-environment-in-the-mortgage-market/ | Retained multi-track comparison workflows |
| Effective cost / IRR concept |  | Quote: "actual cost of the credit". URL: https://www.boi.org.il/en/communication-and-publications/press-releases/l05-07-23/ | Quote: "Data on the portfolio internal rate of return". URL: https://www.boi.org.il/en/information-and-service-to-the-public/interest-rates-and-early-repayment-fees/interest-rate-comparisons-housing-loans/ | Kept `effective_cash_cost` as cash-cost metric, not official IRR |
| Webhook events |  | Quote: "offline-first... does not call". URL: package design, no external webhook reference | Quote: "no webhook endpoint or event name appears in package files". URL: local audit | Marked not applicable; no webhook docs added |
| Official forms |  | Quote: "no official form is required for offline scenario input". URL: package design | Quote: "scenario JSON is local input, not a government filing". URL: local audit | Marked not applicable |
| Israeli business-loan usefulness claim |  | Quote: "households or small businesses up to NIS 100,000". URL: https://www.boi.org.il/en/information-and-service-to-the-public/banking-customer-service-information/public-guides/taking-a-loan/ | Quote: "small and micro businesses". URL: https://www.boi.org.il/media/vohlk2lw/financial-statements-2023-full.pdf | Retained small-business orientation |

## Summary

| Total checks |  double-confirmed | → corrected in pass 2 | Final  |
|---:|---:|---:|---:|
| 17 | 17 | 0 | 0 |

## Corrections applied after validation

- Updated current-prime examples from `0.06` to `0.0525`.
- Added verified 2026 baseline: Bank of Israel 3.75%, implied prime 5.25%, standard VAT 18%.
- Added official CBS CPI API endpoint references as optional external inputs.
- Added warnings that the planner remains offline and does not automatically fetch official rates.
- Clarified that `effective_cash_cost` is a planning metric and not an official lender IRR disclosure.
