# Web verification log

Access date for all sources: 03/06/2026.

Each row contains a first-pass source and a skeptical second-pass source. Snippets are kept short and are quoted only for verification.

| Check | Status | Pass 1 source | Pass 2 source | Package action |
|---|---|---|---|---|
| Current standard Israeli VAT rate | ✓✓ | Israel Tax Authority glossary, `https://www.gov.il/en/pages/taxes-glossary` — "uniform rate of 18% starting from January 1, 2025" | Gov.il 2026 accounting exam file, `https://www.gov.il/BlobFolder/dynamiccollectorresultitem/extended-practical-accounting-exam-16226/he/final-exams_extended-practical-accounting-exam-16226.pdf` — "מע\"מ מחושב לפי. 18%" | Kept `VAT_RATE = Decimal("0.18")`; updated reference text from baseline wording to current web-validated wording. |
| VAT increase effective date | ✓✓ | Prime Minister Office decision, `https://www.gov.il/he/pages/dec1270-2024` — "18% במקום 17% החל מיום 1 בינואר 2025" | Knesset press release, `https://main.knesset.gov.il/EN/News/PressReleases/Pages/press12324w.aspx` — "effective January 1, 2025" | Kept effective-date guidance in verification notes; no code change required. |
| VAT terminology and business terms | ✓✓ | Israel Tax Authority service, `https://www.gov.il/he/service/request-open-exempt-dealer-via-internet` — "פתיחת תיק עוסק פטור" | Israel Invoices topic, `https://www.gov.il/he/departments/topics/israel-invoice` — "בקשה למספר הקצאה לחשבונית מס" | Kept `עוסק פטור`, `עוסק מורשה`, `חשבונית מס`, `קבלה`, and `מע"מ`. |
| Consumer misleading claims | ✓✓ | Consumer Protection Authority, `https://www.gov.il/he/pages/cpfta_consumers_info_isur_hatayat_hatzarchan` — "מידע מלא ואמיתי לפני ואחרי ביצוע עסקה" | Supreme Court database, `https://supremedecisions.court.gov.il/Home/Download?fileName=01057120.G11&path=HebrewVerdicts%5C01%2F120%2F057%2FG11&type=4` — "מידע מלא ואמיתי" | Kept warnings against unsupported claims, hidden terms, and misleading scarcity. |
| Price presentation | ✓✓ | Consumer Protection Authority, `https://www.gov.il/he/pages/cpfta_display_of_prices` — "הצגת מחיר כולל בלבד של מוצר או של שירות" | Supreme Court database, `https://supremedecisions.court.gov.il/Home/Download?fileName=19069300.R39&path=HebrewVerdicts%2F19%2F300%2F069%2Fr39&type=4` — "להציג לפני הצרכן את מחיר המוצר הכולל" | Kept consumer-price examples with VAT-inclusive wording. |
| Cancellation timing references | ✓✓ | Consumer Protection Authority, `https://www.gov.il/he/pages/returns` — "ניתן לבטל תוך 14 ימים" | 2026 enforcement notice, `https://www.gov.il/he/pages/cpfta_electric` — "יחזיר העוסק לצרכן בתוך 14 ימים" | Package avoids a blanket cancellation rule and tells users to state actual terms. |
| Direct marketing and unsubscribe | ✓✓ | Gov.il spam FAQ, `https://www.gov.il/he/departments/faq/17052018_7` — "סעיף 30א(ה) לחוק התקשורת" | Privacy Protection Authority, `https://www.gov.il/he/pages/marketing_inquiries` — "סעיף 30א(ב) לחוק התקשורת" | Kept unsubscribe warnings for WhatsApp, SMS, and email marketing. |
| Privacy for lead forms and personal data | ✓✓ | Privacy Protection Authority, `https://www.gov.il/he/pages/privacy-protection-nice-to-meet-you` — "אוסף מידע אישי ... מחויב לפעול בהתאם" | Direct-mail guidance, `https://www.gov.il/he/pages/direct_mail_2` — "חוק הגנת הפרטיות ... דיוור ישיר" | Kept lead-form privacy microcopy and warnings. |
| Data.gov.il API host and CKAN endpoint pattern | ✓✓ | Data.gov.il docs, `https://data.gov.il/docs` — "All endpoints support POST requests" | Data.gov API snippet, `https://data.gov.il/api/1/util/snippet/api_info.html` — "https://data.gov.il/api/3/action/datastore_search" | Kept `https://data.gov.il/api/3/action/package_search` and `datastore_search`; clarified schemas vary by dataset. |
| Public government datasets | ✓✓ | Data.gov.il homepage, `https://data.gov.il/` — "מאגר הנתונים הממשלתי" | Data.gov about page, `https://data.gov.il/about` — "מאגרי מידע של משרדי ממשלה" | Kept guidance to verify live datasets before factual claims. |
| Companies registry dataset | ✓✓ | Data.gov company dataset, `https://data.gov.il/he/datasets/ministry_of_justice/ica_companies` — "רשימת החברות הרשומות במרשם" | Data.gov CKAN docs, `https://data.gov.il/docs` — "CKAN's Action API" | Kept entity lookup as data.gov package-search pattern, not as a guaranteed real-time registry. |
| Accessibility standard and service regulations | ✓✓ | Equal Rights Commission, `https://www.gov.il/he/pages/website_accessibility` — "תקנות הנגישות לשירות עוסקות בהסרת חסמים" | Knesset accessibility statement, `https://main.knesset.gov.il/About/pages/accstatement.aspx` — "התקן הישראלי (ת\"י 5568)" | Kept accessibility checklist and clear-form-error examples. |
| Hebrew UX/register guidance | ✓✓ | Government language guide, `https://harhayeda.gov.il/guides-digital-transformation/language-characterization-guide/` — "כלי עבודה לכותבים ולכותבות" | Campus IL course, `https://campus.gov.il/course/digitalil-gov-digitalil-microcopyforgovil-he/` — "בשפה שאנשים מבינים בקלות" | Kept neutral, clear, audience-aware Hebrew guidance. |
| Marketing copy for Israeli Hebrew audiences | ✓✓ | Malis Digital, `https://www.malis-cm.co.il/copywriting/` — "copywriting services in Hebrew to Israeli audiences" | Ulpan article, `https://ulpan.com/how-can-knowing-hebrew-help-you-in-marketing/` — "Using Idiomatic Expressions" | Kept the skill positioning, but treated it as market practice rather than regulation. |
| Cultural localization for Israeli marketing | ✓✓ | Digital Hype, `https://digitalhype.co.il/en/marketing_to_israelis_online/` — "Localize your content ... tone and references" | Ulpan article, `https://ulpan.com/how-can-knowing-hebrew-help-you-in-marketing/` — "Avoiding Translation Pitfalls" | Kept Hebrew-first, non-literal-copy guidance. |
| Webhook event names | ✓✓ | Package scan pass 1 — no webhook references in files | Package scan pass 2 — no webhook references in files | No webhook event names are applicable to this non-API copywriting skill. |

## Summary

| Metric | Count |
|---|---:|
| Total checks | 16 |
| ✓✓ double-confirmed | 16 |
| ✗→✓ corrected in pass 2 | 0 |
| Final ✗ not confirmed | 0 |
