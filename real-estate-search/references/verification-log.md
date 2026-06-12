# Web Verification Log

Access date: 04/06/2026

This log records a two-pass web validation of public source claims, official references, paths, rates, terminology, and non-API behavior. Snippets are short excerpts from the cited pages or search result extracts.

| Check | Status | Pass 1 source and snippet | Pass 2 source and snippet | Package action |
| --- | --- | --- | --- | --- |
| Standard Israeli VAT rate is 18% from 01/01/2025 and remains the current workflow assumption in 2026. | ✓✓ | `https://www.gov.il/he/pages/vat-history` — "1.1.25 עלה המע״מ ל-18%" | `https://main.knesset.gov.il/EN/News/PressReleases/Pages/press12324w.aspx` — "effective January 1, 2025" and "VAT rate ... 18%" | Kept 18% as current assumption; added recheck warning. |
| Yad2 public real-estate rent path and neighborhood control. | ✓✓ | `https://www.yad2.co.il/realestate/rent` — "המקום המוביל לנדל"ן להשכרה בישראל" | Same page visible controls — "מחוז", "אזור", "עיר", "שכונה", "רחוב" | Kept `/realestate/rent`; documented manual confirmation. |
| Yad2 public real-estate sale path. | ✓✓ | `https://www.yad2.co.il/realestate/forsale` — "המקום המוביל לנדל"ן למכירה בישראל" | Yad2 homepage search result — "דירות למכירה ודירות להשכרה" | Kept `/realestate/forsale`. |
| Yad2 public commercial path. | ✓✓ | `https://www.yad2.co.il/realestate/commercial` — "המקום המוביל לנדל"ן מסחרי בישראל" | City commercial result — "נכסים מסחריים" and "סוג נכס" | Corrected commercial Yad2 routing to `/realestate/commercial`. |
| Madlan public listing scope includes rent, sale, and commercial. | ✓✓ | `https://www.madlan.co.il/` — "דירות להשכרה", "דירות למכירה", "נדל״ן מסחרי" | `https://www.madlan.co.il/for-rent/ישראל` — examples show rent price, rooms, area, neighborhood | Kept residential paths; documented daily/manual review. |
| Madlan commercial rent and sale paths. | ✓✓ | `https://www.madlan.co.il/commercial/for-rent/ישראל` — "משרדים וחנויות להשכרה" | `https://www.madlan.co.il/commercial/for-sale/ישראל` — "משרדים וחנויות למכירה" | Corrected Madlan commercial routing to `/commercial/for-rent` and `/commercial/for-sale`. |
| Madlan neighborhood terminology and neighborhood pages. | ✓✓ | Madlan homepage — "שכונות בתל אביב", "שכונות בירושלים" | Madlan blog links include neighborhood names such as "בת גלים" and "נווה שאנן" | Kept neighborhood-aware workflow. |
| Komo generic `/search` path for listing searches. | ✗→✓ | No reliable public evidence found for `/search` as a listing path. | Komo rent/sale pages show `/code/nadlan/apartments-for-rent.asp` and `/code/nadlan/apartments-for-sale.asp`. | Replaced `/search` with verified city page patterns. |
| Komo rental city path. | ✓✓ | `https://www.komo.co.il/code/nadlan/apartments-for-rent.asp?cityName=...&nehes=1` — "דירות להשכרה בבאר שבע" | `https://www.komo.co.il/code/rent/` — city links under "דירות להשכרה" | Updated client and docs to use `/code/nadlan/apartments-for-rent.asp`. |
| Komo sale city path. | ✓✓ | `https://www.komo.co.il/code/nadlan/apartments-for-sale.asp` — "דירות למכירה בכל רחבי הארץ" | City result — "דירות למכירה בירושלים" and `cityName=...&nehes=1` | Updated client and docs to use `/code/nadlan/apartments-for-sale.asp`. |
| Komo neighborhood filtering by Hebrew neighborhood name. | ✗→✓ | Search found no reliable public `neighborhood=` or `neighborhoodName=` query pattern. | Indexed pages show `neighborhoodNum` in some URLs and neighborhood labels in listings, but not a name parameter. | Removed assumed neighborhood-name parameter for Komo; added manual neighborhood filtering instructions. |
| Komo room query parameters. | ✓✓ | Indexed Komo URL shows `fromRooms=3` and `toRooms=3`. | City listing title says "3 - 3 חדרים" for that URL. | Added `fromRooms` and `toRooms` support for Komo. |
| Komo commercial rent helper property code for shops/commercial space. | ✓✓ | `https://www.komo.co.il/code/nadlan/apartments-for-rent.asp?nehes=28` — "חנויות/שטח מסחרי להשכרה" | City result with `cityName=חיפה&nehes=28` — "חנויות/שטח מסחרי להשכרה בחיפה" | Added `nehes=28` for commercial rent helper links. |
| Land registry extract terminology and official service. | ✓✓ | `https://www.gov.il/he/service/land_registration_extract` — "הפקת נסח טאבו מפנקסי המקרקעין" | `https://www.gov.il/he/departments/topics/registry-land` — "רישום מקרקעין (טאבו)" | Kept land registry checklist. |
| Purchase tax simulator and current-rate caution. | ✓✓ | `https://www.gov.il/he/service/real_eatate_taxsimulator` — "סימולטור - מחשבון לחישוב מס ברכישת מקרקעין" | Tax Authority department page — "מיסוי מקרקעין" and current Tax Authority services | Kept simulator reference; avoided hardcoding purchase-tax brackets. |
| Planning information source. | ✓✓ | `https://mavat.iplan.gov.il/` — "מידע על תכניות, בקשות ועררים" | `https://www.gov.il/he/service/searching-for-plans-and-applications-in-planning-database` — "איתור תוכניות, ישיבות ועררים" | Kept planning checks. |
| Arnona terminology and basis. | ✓✓ | `https://www.gov.il/he/pages/tax` — "סוג הנכס; שטחו; שימושו; האזור" | 2026 Ministry of Interior tariff table result — "טבלת התעריפים המעודכנת לשנת 2026" | Kept municipal classification and monthly charge checks. |
| Business licensing terminology. | ✓✓ | `https://www.gov.il/he/departments/legalInfo/busines-licensing-law` — "חוק רישוי עסקים, תשכ"ח-1968" | Municipal licensing and accessibility form references licensing process for businesses | Kept business licensing workflow. |
| Accessibility for small businesses. | ✓✓ | `https://mojforms.justice.gov.il/mojaempublicinquiries/Disabilityforsmallbissnness.html` — "בדיקת נגישות בעסק" | `https://www.gov.il/he/departments/topics/your-responsibility-our-right/govil-landing-page` — "לא משאירים אף אחד מחוץ לעסק" | Kept accessibility checks and small-business terminology. |
| Consumer protection authority terminology. | ✓✓ | `https://www.gov.il/he/departments/consumer_protection_and_fair_trade_authority` — "הרשות להגנת הצרכן ולסחר הוגן" | Complaint page — "הטעיה; הטעיה בפרסום; ניצול מצוקה" | Kept advertising and consumer conduct checks. |
| Privacy authority and database-notice terminology. | ✓✓ | `https://www.gov.il/he/departments/the_privacy_protection_authority` — "הרשות להגנת הפרטיות" | `https://www.gov.il/he/service/notice-obligation` — "חובת הודעה ... על מאגר מידע" | Kept data minimization and personal-data warnings. |
| Broker registry terminology. | ✓✓ | `https://www.gov.il/he/Departments/DynamicCollectors/search-real-estate-broker` — "פנקס מתווכים מורשים" | `https://data.gov.il/he/datasets/ministry_of_justice/metavhim/...` — "רשימת מתווכים מורשים" | Kept broker license verification checks. |
| Residential lease legal terminology. | ✓✓ | `https://www.gov.il/he/pages/rent_law` — "חוק השכירות והשאילה" | Knesset law page — "חוק השכירות והשאילה, התשל"א-1971" | Kept lease, deposit, repair, and guarantee checklist. |
| Government Data Portal and CKAN API host. | ✓✓ | `https://data.gov.il/` — "מאגר הנתונים הממשלתי" | `https://data.gov.il/docs` — "CKAN's Action API" and "application/json" | Added CKAN docs URL to reference index. |
| Webhook event names. | ✓✓ | No webhook feature exists in the skill. | Source docs and code expose no webhook integration. | Documented as not applicable; no webhook event names added. |

## Summary

| Total checks | ✓✓ count | ✗→✓ count | Final ✗ count |
| ---: | ---: | ---: | ---: |
| 24 | 21 | 3 | 0 |
