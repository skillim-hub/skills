# Israeli regulation and API reference

This reference supports Hebrew marketing copy. It is not legal, accounting, tax, accessibility, medical, or financial advice. Verify current rates, thresholds, public datasets, platform policies, and sector rules before publication.

## Quick index

| Area | Israeli source | Copywriting relevance |
|---|---|---|
| Consumer advertising | Consumer Protection Law, 5741-1981 | Misleading claims, prices, cancellation, material terms |
| Distance sales | Consumer Protection Law and related regulations | Ecommerce, phone sales, online registration |
| Direct marketing | Communications Law (Telecommunications and Broadcasting), 5742-1982, Section 30A | Email, SMS, WhatsApp, automated messages |
| Privacy | Protection of Privacy Law, 5741-1981; Protection of Privacy Regulations | Lead forms, mailing lists, analytics, databases |
| Accessibility | Equal Rights for Persons with Disabilities Law, 5758-1998; Service Accessibility Regulations; Israeli Standard 5568 | Public digital services and readable content |
| VAT | Value Added Tax Law, 5736-1975; Israel Tax Authority publications | `כולל מע"מ`, `לא כולל מע"מ`, invoices |
| Business/tax copy | Income Tax Ordinance; bookkeeping instructions | Accountants, freelancers, deductible-expense copy |
| Public data | data.gov.il CKAN-style APIs | Locality, registry, and public dataset checks |
| Entity checks | Corporations Authority / Registrar datasets | Company/amuta trust claims |

## Citation patterns for internal notes

- `Consumer Protection Law, 5741-1981 — avoid misleading price, discount, and cancellation claims.`
- `Communications Law, Section 30A — promotional direct messages need consent/exception and unsubscribe.`
- `Protection of Privacy Law, 5741-1981 — lead form should disclose purpose and link to privacy policy.`
- `Value Added Tax Law, 5736-1975 — clarify VAT for business-facing pricing.`
- `Equal Rights for Persons with Disabilities Law and Service Accessibility Regulations — public digital text should be clear and accessible.`

## VAT and pricing

Web validation on 03/06/2026 double-confirmed the standard Israeli VAT rate as 18%. Verify the live rate again before publication or invoicing.

| Scenario | Hebrew wording |
|---|---|
| Consumer price | `₪249 כולל מע"מ` |
| Business quote | `המחיר אינו כולל מע"מ, אלא אם צוין אחרת` |
| Starting price | `החל מ-₪390, בהתאם להיקף העבודה` |
| Subscription | `₪79 לחודש, ניתן לבטל בהתאם לתנאי השירות` |
| Installments | `עד 3 תשלומים ללא ריבית, בכפוף לאישור חברת האשראי` |
| Sale condition | `בתוקף עד 30/06/2026 או עד גמר המלאי, המוקדם מביניהם` |

Avoid: `הכי זול בארץ`, `חיסכון מובטח במס`, hidden renewal terms, and discounts without material conditions.

## Direct marketing consent and unsubscribe

Promotional email, SMS, WhatsApp broadcast, or automated message generally requires consent or a recognized exception, and a clear removal method.

### Footer examples

```text
להסרה: השיבו הסר
```

```text
להסרה מהרשימה: השיבו "הסר".
```

```text
קיבלת הודעה זו כי נרשמת לקבלת עדכונים. להסרה מרשימת הדיוור לחצו כאן.
```

### Request example

```json
{
  "channel": "whatsapp",
  "audience": "לקוחות קיימים",
  "offer": "מבצע חידוש מנוי",
  "has_marketing_consent": true,
  "include_unsubscribe": true,
  "unsubscribe_method": "השיבו הסר"
}
```

### Response example

```json
{
  "copy": "היי, מנוי החידוש השנתי פתוח עד 30/06/2026 במחיר ₪390 כולל מע\"מ. להצטרפות: [קישור]. להסרה מהרשימה: השיבו \"הסר\".",
  "compliance_notes": [
    "Communications Law, Section 30A: message includes unsubscribe wording.",
    "Consumer Protection Law: promotion includes date and price."
  ]
}
```

### Error table

| Code | Meaning | Copy action |
|---|---|---|
| `CONSENT_UNKNOWN` | Consent status not provided | Add caveat and unsubscribe wording |
| `NO_UNSUBSCRIBE` | Promotional direct message lacks removal option | Add removal instruction |
| `UNCLEAR_SENDER` | Sender identity missing | Include business name |
| `FAKE_URGENCY` | Scarcity not supported | Replace with real date/quantity |
| `OVERLONG_SMS` | Message too long | Keep one offer and one הנעה לפעולה |

## Privacy and lead forms

When collecting name, phone, email, address, health, financial, or other personal information, add transparent microcopy.

```text
הפרטים ישמשו ליצירת קשר בנוגע לפנייה. ניתן לעיין במדיניות הפרטיות באתר.
```

For sensitive information:
```text
אין לשלוח מידע רפואי או פיננסי רגיש בטופס זה. נציג יחזור אליכם להמשך טיפול.
```

### Request example

```json
{
  "asset": "landing_page",
  "collects_personal_data": ["name", "phone", "email"],
  "privacy_policy_url": "https://example.co.il/privacy"
}
```

### Response example

```json
{
  "microcopy": "השאירו פרטים ונחזור אליכם לתיאום. הפרטים ישמשו ליצירת קשר בלבד, בהתאם למדיניות הפרטיות באתר.",
  "notes": ["Protection of Privacy Law: disclose purpose of collection and reference privacy policy."]
}
```

## Accessibility copy checks

- Use clear link labels: `לתיאום שיחה`, not only `לחצו כאן`.
- Use short paragraphs and informative headings.
- Do not rely only on color or emoji to convey meaning.
- Write specific form errors: `יש להזין מספר טלפון תקין בן 9 או 10 ספרות.`
- Keep הנעה לפעולה buttons understandable without surrounding text.

## data.gov.il API patterns

Many Israeli public datasets are exposed through CKAN-style endpoints. Dataset names and resource schemas vary.

### Package search

```http
GET https://data.gov.il/api/3/action/package_search?q=רשויות%20מקומיות
Accept: application/json
```

### Typical response

```json
{
  "success": true,
  "result": {
    "count": 12,
    "results": [
      {
        "id": "example-package-id",
        "title": "רשויות מקומיות",
        "resources": [
          {
            "id": "example-resource-id",
            "format": "CSV",
            "url": "https://data.gov.il/dataset/example/resource/example/download/file.csv"
          }
        ]
      }
    ]
  }
}
```

### Datastore search

```http
GET https://data.gov.il/api/3/action/datastore_search?resource_id=RESOURCE_ID&limit=5&q=חיפה
Accept: application/json
```

### Typical response

```json
{
  "success": true,
  "result": {
    "records": [
      {"_id": 1, "שם_ישוב": "חיפה", "סמל_ישוב": 4000}
    ],
    "total": 1
  }
}
```

### API error table

| Status | Cause | Handling |
|---|---|---|
| `success=false` | Invalid action/resource/query | Report dataset not verified |
| `404` | Endpoint/resource missing | Retry package search |
| `429` | Rate limit | Back off and cache |
| `5xx` | Public service unavailable | Do not invent facts |
| Empty records | No match | Remove factual claim or cite another source |

## Tax and accounting terminology

| Hebrew term | Use |
|---|---|
| `עוסק פטור` | Business exempt from VAT collection, subject to turnover threshold |
| `עוסק מורשה` | VAT-registered business |
| `חשבונית מס` | Tax invoice |
| `קבלה` | Receipt |
| `חשבונית מס/קבלה` | Combined tax invoice/receipt |
| `הוצאה מוכרת` | Deductible expense, subject to rules |
| `דוח שנתי` | Annual report |
| `הצהרת הון` | Capital declaration |
| `מקדמות מס הכנסה` | Income tax advances |
| `דיווח למע"מ` | VAT reporting |

Safe:
```text
ליווי מסודר לעוסקים פטורים ומורשים: קליטת מסמכים, תזכורות לדיווחים, והסבר ברור על הוצאות מוכרות בהתאם לדין.
```

Risky:
```text
נחסוך לך אלפי שקלים במס בוודאות.
```

## Entity lookup pattern

When copy references a registered company or amuta, verify the entity before using trust claims.

```http
GET https://data.gov.il/api/3/action/package_search?q=רשם%20החברות
Accept: application/json
```

Prefer:
```text
חברה ישראלית רשומה המספקת שירותי התקנה ותמיכה לעסקים קטנים.
```

Avoid:
```text
החברה המובילה בישראל.
```

## Sector-specific safer wording

| Sector | Risk | Safer wording |
|---|---|---|
| Health clinic | Cure guarantee | `אבחון מקצועי ותוכנית טיפול מותאמת` |
| Fitness | Body transformation promise | `תוכנית אימונים הדרגתית עם מעקב` |
| Accountant | Guaranteed tax saving | `בדיקת זכאויות והוצאות מוכרות בהתאם לדין` |
| Lawyer | Guaranteed outcome | `בחינת המקרה וגיבוש דרך פעולה` |
| Real estate | Unverified scarcity | `נכון ל-03/06/2026, קיימות דירות זמינות בפרויקט` |
| Finance | Return guarantee | `היכרות עם אפשרויות השקעה ורמות סיכון` |
| Education | Guaranteed acceptance | `הכנה ממוקדת לתהליך הקבלה` |
| Beauty | Medical result | `מראה מטופח יותר, בהתאם לסוג העור` |


## Web validation status

See `references/verification-log.md` for the two-pass source table, snippets, access date, and package actions. The log confirms the VAT rate, VAT effective date, direct-marketing references, privacy references, accessibility references, data.gov.il endpoint patterns, and entity-dataset guidance as of 03/06/2026.

## Webhook applicability

This is a non-API copywriting skill. No webhook event names are referenced or required.
