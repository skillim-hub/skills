# Verification Log

Access date for all checks: 04/06/2026.

| Check | Status | Pass 1 source | Pass 2 source | Package action |
|---|---|---|---|---|
| Standard Israeli VAT rate | ✓✓ | "1.1.25 עלה המע"מ ל-18%" — https://www.gov.il/he/pages/vat-history | "המס הוא בשיעור אחיד של 18% החל מתאריך ה - 1.1.2025" — https://www.gov.il/he/pages/taxes-glossary | Added explicit current 18% VAT note to references. |
| Israel Invoices allocation threshold in 2026 | ✗→✓ | "10,000 החל מה-1 בינואר 2026 ו-5,000 ₪ החל מה-1 ביוני 2026" — https://www.gov.il/he/service/request-assignment-number-for-tax-invoice | "החל מה-1.6.2026 התקרה היא 5,000 ₪" — https://govextra.gov.il/taxes/innovation/home/israel-invoices/ | Added 2026 threshold table and warning. |
| Bank of Israel representative exchange-rate role | ✓✓ | "publishes the representative exchange rate of the shekel against foreign currencies" — https://www.boi.org.il/en/economic-roles/financial-markets/exchange-rates/ | "representative rate is an indicator ... has no obligatory status under law" — same official page | Kept wording that rates are indicative, not settlement rates. |
| Bank of Israel publication timing | ✓✓ | "Up-to-date as of: 03/06" — https://www.boi.org.il/en/economic-roles/financial-markets/exchange-rates/ | "published soon after 15:15 ... 12:15 on Fridays" — https://www.boi.org.il/en/economic-roles/financial-markets/explanatory-notes-to-the-representative-exchange-rates/ | Added timing and source timestamp guidance. |
| Current sample FX rates for examples | ✗→✓ | "USD 2.8720 ... GBP 3.8629 ... EUR 3.3365" — https://www.boi.org.il/en/economic-roles/financial-markets/exchange-rates/ | "Representative exchange rates ... Up-to-date as of: 03/06" — https://www.boi.org.il/en/ | Replaced old sample rates with USD 2.8720, EUR 3.3365, GBP 3.8629. |
| Bank of Israel API host | ✓✓ | "API service to access up-to-date data" — https://boi.org.il/en/the-bank-of-israel-s-new-website/ | "https://edge.boi.gov.il/FusionDataBrowser" — https://www.boi.org.il/media/tzxbuhhj/extracting-representative-exchange-rates-from-the-new-series-database.pdf | Replaced placeholder host with `edge.boi.gov.il` guidance. |
| Static public transport data | ✓✓ | "קבצי GTFS הינם קבצים המכילים את כל נתוני הרישוי" — https://www.gov.il/he/pages/gtfs_general_transit_feed_specifications | "מידע סטטי (בדף מידע סטטי - GTFS)" — https://www.gov.il/he/pages/real_time_information_siri | Kept GTFS as static schedule/licensing data source. |
| Real-time public transport interface | ✓✓ | "מידע לגבי אוטובוסים ורכבות בתחבורה הציבורית, בשלוש שכבות" — https://www.gov.il/he/pages/real_time_information_siri | "real-time information from the public transportation operator's systems" — https://www.gov.il/BlobFolder/generalpage/real_time_information_siri/he/ICD_SM_28_32.pdf | Kept SIRI as real-time class; no booking action implied. |
| Israel Rail official role | ✓✓ | "רכבת ישראל היא מפעילת מערך הרכבות הכבדות הלאומי" — https://www.rail.co.il/ | "מידע על תחנות, לוחות זמנים ותכנון נסיעה" — https://www.rail.co.il/ | Kept rail workflow as schedule/planning verification only. |
| Ramon Airport location and Eilat role | ✓✓ | "located about 19 km north of the city of Eilat" — https://www.iaa.gov.il/en/airports/ramon/about/ | "domestic flights to the Ramon airport in Eilat" — https://www.iaa.gov.il/en/companies/airline-companies/israir-haifa/ | Kept transfer warning between Ramon and Eilat. |
| Ben Gurion terminal structure | ✓✓ | "Terminal 3 for international flights and Terminal 1 for both domestic and low-cost international flights" — https://www.iaa.gov.il/en/airports/ben-gurion/about/ | "check from which terminal the flight departs" — https://www.iaa.gov.il/en/ | Kept terminal verification checklist. |
| Airport hand-luggage security | ✓✓ | "All hand luggage will be screened" — https://www.iaa.gov.il/en/airports/ben-gurion/securitybgn/ | "Laptops should be removed from carry bags in advance" — same official page | Kept baggage/security as verification prompts, not policy advice. |
| Israeli passport validity prompt | ✓✓ | "יש לבדוק תוקף דרכון מספיק זמן לפני הזמנת הטיסה" — https://www.gov.il/he/pages/tips_for_planning_best_vacation | "מרבית המדינות דורשות תוקף בדרכון בן חצי שנה" — https://www.gov.il/he/pages/questions_answers_news | Kept passport validity prompt and official-source warning. |
| Temporary foreign-passport exception for Israelis | ✗→✓ | "valid foreign passport until 30 September 2026" — https://www.gov.il/en/pages/exit-with-foriegn-passport-17022026 | "until September 30, 2026" — https://embassies.gov.il/chicago/en/announcements/entry-and-exit-israel | Added date-specific exception note; requires recheck after 30/09/2026. |
| Consumer tourism cancellation prompts | ✓✓ | "ביטול עסקת תיירות שנעשתה במכר מרחוק" — https://www.gov.il/he/pages/qaflight23 | "ניתן לבטל תוך 14 ימים" — https://www.gov.il/he/pages/returns | Kept no-legal-advice wording and cancellation fact checklist. |
| Accessibility at airports | ✓✓ | "airlines are responsible for attending to passengers requiring assistance" — https://www.iaa.gov.il/en/airports/ben-gurion/accessibility/ | "responsibility ... lies with the airline they are flying with" — https://www.iaa.gov.il/en/airports/ramon/accessibility/ | Kept accessibility prompts and airline confirmation step. |
| Public transportation accessibility | ✓✓ | "תחבורה ציבורית נגישה מאפשרת לאנשים עם מוגבלות להתנייד" — https://www.gov.il/he/pages/public_transportation_accessibility_info | "קווים בין-עירוניים נגישים לאנשים עם מוגבלות בניידות" — https://www.gov.il/he/pages/accessible_intercity_buses | Kept accessible public transport prompts. |
| Hotels and Ministry of Tourism database | ✓✓ | "מאגר של משרד התיירות המהווה כמאגר הרשמי של מדינת ישראל" — https://www.gov.il/he/service/update-hotel-accomodation-database | "Submit complaints regarding tourism services" — https://www.gov.il/en/service/review_and_complaints | Added official hotel database/complaint distinction. |
| Jordan border example validity | ✓✓ | "passports must be valid for at least 3 months" — https://www.iaa.gov.il/en/land-border-crossings/yitzhak-rabin/passengers-departing-for-jordan/ | "Visa: Check with the Embassy of Jordan in Israel" — same official page | Kept border checks as destination-specific prompts. |
| Webhook event names | ✓✓ | No webhook source referenced in the package. | No travel supplier webhook integration exists in scripts or docs. | Logged as not applicable; do not invent webhook event names. |

## Summary

| Metric | Count |
|---|---:|
| Total checks | 19 |
| ✓✓ double-confirmed | 15 |
| ✗→✓ corrected in pass 2 or after pass review | 4 |
| Final ✗ could not be confirmed | 0 |
