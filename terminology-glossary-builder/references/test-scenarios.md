# Test scenarios

Use these scenarios to validate behavior manually or through automated tests.

| Number | Scenario | Input | Expected result |
|---|---|---|---|
| 1 | English VAT synonym | `VAT` | Resolves to `Value Added Tax (VAT)` and `מס ערך מוסף (מע"מ)`. |
| 2 | Hebrew VAT synonym | `מע"מ` | Resolves to the same VAT entry as English. |
| 3 | Duplicate normalization | `VAT, מע"מ, מס ערך מוסף` | Keeps one VAT entry. |
| 4 | Tax invoice distinction | `חשבונית מס, קבלה` | Produces separate entries and definitions. |
| 5 | Freelancer classification | `עוסק פטור, עוסק מורשה` | Cites the Tax Authority and warns that thresholds may change. |
| 6 | Withholding tax | `ניכוי מס במקור` | Explains payer deduction and Tax Authority transfer. |
| 7 | National Insurance | `דמי ביטוח לאומי` | Cites the National Insurance Institute. |
| 8 | Pension term | `הפרשות לפנסיה` | Cites labor or social insurance sources and separates obligations. |
| 9 | Consumer cancellation | `ביטול עסקה צרכנית` | Cites consumer authority and avoids unverified exact deadlines. |
| 10 | Warranty certificate | `תעודת אחריות` | Explains warranty document fields. |
| 11 | Privacy policy | `מדיניות פרטיות` | Cites the Privacy Protection Authority. |
| 12 | Database registration or notice | `רישום או הודעה על מאגר מידע` | Adds review note for applicability. |
| 13 | Accessibility statement | `הצהרת נגישות` | Cites accessibility authority. |
| 14 | Company extract | `נסח חברה` | Cites Corporations Authority and data.gov.il. |
| 15 | Import declaration | `רשימון יבוא` | Cites Tax Authority customs context. |
| 16 | Standard mark | `תו תקן` | Cites Standards Institution of Israel. |
| 17 | Restricted bank account | `חשבון מוגבל` | Cites Bank of Israel. |
| 18 | Prospectus | `תשקיף` | Cites Israel Securities Authority. |
| 19 | Unknown English term | `chargeback reserve` | Marks Hebrew translation as requiring professional review. |
| 20 | Unknown Hebrew term | `מונח פנימי` | Marks English translation as requiring professional review. |
| 21 | Sandbox environment | `--env sandbox` | Build succeeds and marks environment as sandbox. |
| 22 | Invalid environment | `--env staging` | Raises validation error. |
| 23 | Create-export chain | Use `tgb create`, extract id, then `tgb export`. | Export returns the saved glossary. |
| 24 | Store mismatch | Export id from a different store path. | Raises glossary not found. |
| 25 | Hebrew Markdown | Use `--hebrew`. | Output has Hebrew headers and DD/MM/YYYY date label. |
| 26 | JSON encoding | Export JSON. | Hebrew appears unescaped when printed by examples. |
| 27 | CSV export | Export CSV. | UTF-8 content includes source keys. |
| 28 | Empty input | Build with an empty list. | Quality check warns that no terms were provided. |
| 29 | Max terms | Use `max_terms=1`. | Only one entry appears. |
| 30 | Async build | Use `abuild_glossary`. | Result matches sync structure. |
| 31 | Registry validation | Run `tgb validate`. | No errors for the bundled registry. |
| 32 | Source listing | Run `tgb sources --json`. | JSON includes `tax_authority`, `privacy`, and `consumer_protection`. |
