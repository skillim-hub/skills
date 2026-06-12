# יומן בקרת איכות עברית

תאריך: 02/06/2026

## היקף

נבדקו `SKILL_HE.md` וכל קטעי העברית הציבוריים במסמכי העזר, בדוגמאות ובפקודות.

## תיקונים שבוצעו

- עודכנה לוקליזציית תאריכים לתבנית `DD/MM/YYYY`.
- הוחלפו ניסוחים שמרמזים על גוף יוצר בניסוח ניטרלי ותפעולי.
- נשמר שימוש עקבי במונחים מקצועיים: מק״ט, מע״מ, מחיר כולל מע״מ, מחיר לפני מע״מ, ספירת מלאי, תנועת מלאי, נקודת הזמנה מחדש, הנהלת חשבונות, חשבונית מס, חשבונית עסקה, קופה וספק.
- נשמר סימון מטבע `₪` בדוגמאות מחיר.
- נבדק שאין ניקוד בטקסט טכני.
- נשמרו שמות פקודות, שמות שדות וקבועי קוד באנגלית רק כאשר הם חלק מממשק טכני.
- עודכנו אזכורי קובץ הלקוח לנתיב `scripts/inventory_catalog_manager_client.py`.
- נשמרה הפרדה בין מחיר לצרכן לבין מחיר לעסק, כולל טיפול במע״מ.
- נשמר ניסוח זהיר בנושאי מס, חשבוניות ודיווח: אמת מול מקור רשמי או איש מקצוע לפני שימוש מחייב.

## החלטות מינוח

| מונח | שימוש |
|---|---|
| SKU | מק״ט כאשר מדובר בהסבר עסקי; `sku` כאשר מדובר בשם שדה טכני. |
| VAT | מע״מ בהסבר; `vat_rate` בשם שדה טכני. |
| Stock movement | תנועת מלאי. |
| Reorder point | נקודת הזמנה מחדש. |
| Point of sale | קופה. |
| Ledger or bookkeeping export | ייצוא להנהלת חשבונות. |

## תוצאה

העברית טבעית, מקצועית ומתאימה לעסק קטן בישראל. הטקסט אינו מנוקד, אינו ממותג, ואינו מייחס את החבילה ליוצר או לארגון.

## Web-validated Hebrew QA additions for 0.4.0

- Confirmed official use of `מס ערך מוסף` and common abbreviation `מע״מ`; kept both forms in Hebrew guidance.
- Confirmed `מספר הקצאה לחשבונית מס` as the official service terminology; kept `מספר הקצאה` in workflow text.
- Confirmed `ניהול ספרים`, `פנקסי חשבונות`, and `אישור ניהול ספרים` as professional terms; avoided unnecessary Anglicisms.
- Kept dates in `DD/MM/YYYY` format in public Hebrew-facing examples.
- Kept amounts with `₪` and clarified thresholds before מע״מ.
- Removed no nikud because none was found in technical prose.
