# Troubleshooting

## Tone problems

### Too cold

Add context and a courteous request.

```text
רציתי לוודא שהחשבונית התקבלה ושהכול תקין מבחינתכם.
אשמח לקבל עדכון לגבי מועד התשלום הצפוי.
```

### Too weak

Replace vague timing with a concrete date.

```text
נא לעדכן עד 06/06/2026 אם נדרש מסמך נוסף לצורך השלמת התשלום.
```

### Too aggressive

Replace threats with factual status.

```text
התשלום טרם התקבל במערכת. נא לעדכן עד 06/06/2026 לגבי מועד התשלום הצפוי.
```

## Hebrew grammar problems

### Wrong gender

Use neutral forms when gender is unknown.

| Risky | Better |
|---|---|
| `אשמח אם תוכל/י לאשר` | `אשמח לקבל אישור` |
| `תעדכן אותי` | `נא לעדכן אותי` |
| `שלחי לי` | `אפשר לשלוח אליי` |

### Awkward slash forms

Avoid slash-heavy text in polished emails.

```text
לא מומלץ: אשמח אם תוכל/י לשלוח/י ולעדכן/י.
מומלץ: אשמח לקבל את המסמך ועדכון לאחר השליחה.
```

### Literal English structure

| Literal | Natural Hebrew |
|---|---|
| `רציתי להגיע החוצה` | `רציתי לפנות אליך` |
| `לעשות מעקב` | `לוודא שהנושא התקדם` |
| `אני מעריך את הזמן שלך` | `תודה על הזמן וההתייחסות` |

## Localization problems

### Amount lacks context

Always include currency and VAT status when quoting a price.

```text
עלות: 4,800 ₪ בתוספת מע"מ כדין
```

When VAT status is unknown:

```text
עלות: 4,800 ₪ [בדיקה נדרשת: סטטוס מע"מ לא נמסר.]
```

### Date format is inconsistent

Convert every complete date to `DD/MM/YYYY`.

| Input | Output |
|---|---|
| `2026-06-03` | `03/06/2026` |
| `3-6-26` | `03/06/2026` |
| `June 3` | `[נדרש תאריך מלא]` |

### Attachment wording is wrong

| Situation | Correct wording |
|---|---|
| One invoice attached | `מצורפת חשבונית` |
| One quote attached | `מצורפת הצעת מחיר` |
| Multiple documents attached | `מצורפים המסמכים` |
| Attachment not confirmed | Do not claim that a file is attached |

## Accounting and tax wording

### Missing VAT status

Do not invent. Add a review note.

```text
[בדיקה נדרשת: סטטוס מע"מ לא נמסר.]
```

### Wrong document type

Do not turn a payment request into `חשבונית מס` unless supplied. Use generic wording:

```text
מסמך התשלום
דרישת התשלום
המסמך המצורף
```

### Business identifier missing

Do not fabricate `עוסק מורשה` or `ח.פ.`. Omit the line or use a placeholder only when requested.

## Privacy and sensitivity

Remove unnecessary identification numbers, home addresses, medical details, and payment-card details unless they are essential to the request.

Safer phrasing:

```text
מספר הזמנה: [מספר]
פרטי התקשרות: [טלפון/מייל]
```

## Consumer complaints

Use structured facts when the complaint is unfocused.

```text
פרטי הפנייה:
- מספר הזמנה או לקוח:
- תאריך רכישה:
- סכום העסקה:
- תיאור הבעיה:
- פתרון מבוקש:
```

Replace legal conclusions with review language.

| Overclaim | Safer |
|---|---|
| `על פי חוק אתם חייבים להחזיר לי כסף` | `אבקש לבדוק את זכאותי להחזר ולעדכן בכתב` |
| `זו הטעיה אסורה` | `אבקש לבדוק את הפער בין המידע שנמסר לבין השירות שסופק` |

## Final review checklist

- Purpose visible in subject.
- First sentence gives context.
- Facts are complete and not invented.
- Tone fits relationship.
- Gender is correct or neutral.
- Dates use `DD/MM/YYYY`.
- Amounts use `₪`.
- VAT status is explicit for prices.
- Call to action is concrete.
- Signature is appropriate.
- Review notes flag assumptions.


## Israel Invoices review note

When a business email discusses a B2B tax invoice above 5,000 ₪ before VAT as of 03/06/2026, add a review note instead of giving tax instructions.

```text
[בדיקה נדרשת: ייתכן שנדרש מספר הקצאה לפי כללי חשבוניות ישראל. יש לבדוק במערכת הרשמית.]
```
