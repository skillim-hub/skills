# Web Verification Log

Access date for every row: 04/06/2026. Quote snippets are short excerpts from live search or opened pages and are kept under 140 characters each.

| Check | Status | Pass 1 source | Pass 1 snippet | Pass 2 source | Pass 2 snippet | Package action |
|---|---|---|---|---|---|---|
| Current Israeli VAT rate | ✓✓ | https://www.gov.il/en/pages/taxes-glossary | "uniform rate of 18% starting from January 1, 2025" | https://taxsummaries.pwc.com/israel/corporate/other-taxes | "Last reviewed - 01 January 2026... current rate of VAT is 18%" | Added billing guardrail; no router calculation added. |
| VAT rate source page | ✓✓ | https://www.gov.il/en/pages/vat-rate-amount-new | "amounts and rates set out in VAT legislation and regulations" | https://main.knesset.gov.il/EN/News/PressReleases/Pages/press12324w.aspx | "effective January 1, 2025... VAT rate... increased" | Referenced as validation source. |
| Open-data API host and action endpoint | ✓✓ | https://data.gov.il/docs | "CKAN's Action API is a powerful, RPC-style API" | https://data.gov.il/api/1/util/snippet/api_info.html | "https://data.gov.il/api/3/action/datastore_search" | Added endpoint path to API reference. |
| Locality list for Israeli city normalization | ✓✓ | https://data.gov.il/he/datasets/population_authority/citiesandsettelments/5c78e9fa-c2e2-4771-93ff-7f400a12f7ba | "רשימת ישובים בישראל - מתעדכן" | https://www.cbs.gov.il/he/publications/doclib/2019/ishuvim/intro.pdf | "קובץ היישובים מכיל את היישובים בישראל" | Clarified optional normalization source. |
| Companies Registrar data | ✓✓ | https://www.gov.il/he/service/database-companies-partnership | "לעיין בקבצי מידע... החברות והשותפויות הרשומות במרשם" | https://data.gov.il/he/datasets/ministry_of_justice/ica_companies | "רשימת החברות הרשומות במרשם שמנהל רשם החברות" | Kept enrichment optional and lawful. |
| Protection of Privacy Law name and source | ✓✓ | https://www.gov.il/he/pages/privacy_law | "חוק הגנת הפרטיות, התשמ"א-1981" | https://www.gov.il/BlobFolder/legalinfo/legislation/en/ProtectionofPrivacyLaw57411981unofficialtranslatio.pdf | "No person shall infringe the privacy of another without his consent" | Kept privacy minimization guardrails. |
| Privacy data-security regulations | ✓✓ | https://www.gov.il/en/pages/data_security_eng | "establish organizational mechanisms" | https://www.gov.il/en/pages/the_board_role | "Regulations (Data Security), 5777-2017 stipulate obligations" | Added reference to review access controls and logs. |
| Privacy Amendment 13 effective date | ✓✓ | https://www.gov.il/he/pages/guide_tikon13_professional | "נכנס לתוקף ב־14 באוגוסט 2025" | https://library.mevaker.gov.il/sites/DigitalLibrary/Documents/2025/2025-12/EN/2025.12-76B-001-EN.pdf | "came into force in August 2025" | Added note to re-check Amendment 13 obligations before launch. |
| Direct marketing and spam consent | ✓✓ | https://www.gov.il/he/pages/17052018_7 | "המפרסם... יציין בו את הפרטים הבאים" | https://fs.knesset.gov.il/globaldocs/MMM/63275fbe-180e-e711-80cc-00155d0206a2/2_63275fbe-180e-e711-80cc-00155d0206a2_11_10750.pdf | "בלא קבלת הסכמה מפורשת מראש של הנמען" | Kept service/marketing separation and opt-in evidence. |
| Consumer Protection Law terminology | ✓✓ | https://www.gov.il/en/departments/consumer_protection_and_fair_trade_authority | "established by the Consumer Protection Law, 1981" | https://library.mevaker.gov.il/sites/DigitalLibrary/Documents/2022/2022.11/EN/2022.11-207-Consumer-Taktzir-EN.pdf | "principal one is the Consumer Protection Law, 1981" | Kept consumer quote/cancellation context guidance. |
| Accessibility law and fallback contact | ✓✓ | https://www.gov.il/en/pages/equal_rights_persons_disabilities_law | "A public place shall be accessible to people with disabilities" | https://www.gov.il/en/pages/website_accessibility | "aim to ensure that people with disabilities can exercise" | Kept accessible fallback guidance. |
| Telephone numbering and weak area-code inference | ✓✓ | https://www.gov.il/BlobFolder/policy/number_policy/he/Numbering-scheme-30052024.pdf | "תכנית מספור... בישראל... 30 במאי, 2024" | https://www.gov.il/he/departments/topics/numbering_telephony_services/govil-landing-page | "מספור שירותי טלפוניה" | Kept mobile prefixes as contact data, fixed-line area codes as weak hints. |
| Meta Lead Ads webhook field | ✓✓ | https://developers.facebook.com/docs/graph-api/webhooks/getting-started/webhooks-for-leadgen/ | "subscribe to the leadgen field" | https://developers.facebook.com/docs/marketing-api/guides/lead-ads/retrieving/v2.8/ | "field" => "leadgen"... "leadgen_id"" | Added external webhook field note; internal events remain local. |
| WhatsApp service and template categories | ✓✓ | https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/send-messages | "24-hour timer called a customer service window starts" | https://whatsappbusiness.com/products/platform-pricing/ | "four message categories... marketing, utility, authentication, and service" | Kept service reply vs marketing template distinction. |
| Exact public source for this package's lead-routing sentence | final ✗ | Search: "Routes incoming leads... Israel 2026" | No authoritative matching public standard found. | Search: "lead routing Hebrew Arabic Russian Israel small business" | No official standard found for the exact package behavior. | Reworded docs to state this as package capability verified by tests, not external fact. |

## Summary

| Metric | Count |
|---|---:|
| Total checks | 15 |
| Double-confirmed ✓✓ | 14 |
| Corrected in pass 2 ✗→✓ | 0 |
| Final ✗ | 1 |
