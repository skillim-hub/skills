# מסווג תנועות בנק

סווג תנועות מחשבונות בנק ישראליים והכן פלט מסודר לבקרה, הנהלת חשבונות, מעקב הוצאות, התאמות וניתוח תזרים.

המיומנות מקבלת קובצי יצוא בסגנון CSV, מנרמלת מונחים ישראליים, מזהה חובה/זכות, מסווגת תנועות, מסמנת תנועות לבדיקה, ומייצאת CSV או JSON. ההתאמה מיועדת לעסקים קטנים, עוסקים פטורים, עוסקים מורשים, חברות קטנות, עצמאים ומשקי בית.


## הערות רגולטוריות לאחר אימות ברשת

תאריך גישה: 2026-06-02.

- שיעור המע"מ הכללי בישראל הוא 18% החל מ-01/01/2025 לפי דפי רשות המסים שנבדקו. בדוק מחדש את השיעור לפני דיווח או הפקת פלט מס ללקוח.
- בנק הפועלים, בנק לאומי, בנק דיסקונט, מזרחי-טפחות, מרכנתיל, יהב, ישראכרט, MAX ו-CAL מופיעים כדוגמאות מקומיות משום שהם מופיעים בדפי הגופים המפוקחים של בנק ישראל. אין בכך אישור, שותפות, חיבור מוסמך או הבטחה לפורמט יצוא אחיד.
- החבילה מסווגת קובצי יצוא מקומיים בסגנון CSV. היא אינה מתחברת לחשבון בנק חי, אינה אוספת סיסמאות, אינה מיישמת הסכמות בנקאות פתוחה, אינה מגדירה אירועי webhook ואינה מספקת נתיבי API רשמיים של בנק ישראל.

## תחום שימוש

השתמש בקבצים שיוצאו מבנק הפועלים, לאומי, דיסקונט, מזרחי-טפחות, מרכנתיל, יהב ובנקים דומים. השתמש בפורמט ₪, בתאריכים DD-MM-YYYY, בתיאורים בעברית, ובעמודות כגון חובה, זכות, תאריך ערך, אסמכתא ויתרה.

אין להסתמך על הפלט כייעוץ חשבונאי, מס, משפטי או בנקאי. התייחס לסיווג כטיוטה מובנית שמחייבת בדיקה.

## דוגמת קלט

```csv
תאריך,תיאור,חובה,זכות,יתרה,אסמכתא
02/01/2026,מע"מ תקופתי,1200.00,,18450.20,99123
03/01/2026,העברה מלקוח - חשבונית 1042,,3500.00,21950.20,99124
04/01/2026,עמלת מסלול עסקים,29.90,,21920.30,99125
```

## התחלה מהירה

```bash
python scripts/bank-transaction-categorizer-cli.py create-sample --env sandbox --output sample.csv > create-response.json
INPUT_ID=$(python -c "import json; print(json.load(open('create-response.json', encoding='utf-8'))['id'])")
python scripts/bank-transaction-categorizer-cli.py categorize --env sandbox --input-id "$INPUT_ID" --output categorized.csv
python scripts/bank-transaction-categorizer-cli.py summary --env sandbox categorized.csv
```

## שדות פלט

כל שורה כוללת `date`, `description`, `normalized_description`, `amount`, `direction`, `category`, `subcategory`, `vat_relevant`, `tax_deductibility`, `confidence`, `rule_id`, `flags`, `currency`, `balance`, `reference`, `bank`, ו-`source_file`.

## מפת קטגוריות

| קטגוריה | דוגמאות | טיפול ברירת מחדל |
|---|---|---|
| הכנסות | העברה מלקוח, זיכוי סליקה, תשלום חשבונית, משכורת | בדיקה ואימות מקור הכסף |
| מסים ורשויות | מע״מ, מקדמות מס הכנסה, ביטוח לאומי, ארנונה | בדיקה והפרדה לפי סוג תשלום |
| עמלות וריבית בנקאית | עמלות חשבון, ריבית חובה, דמי ניהול | רלוונטי בעיקר בחשבון עסקי |
| תוכנה וענן | Google Cloud, AWS, Microsoft, Adobe, Zoom, GitHub | לרוב מוכר עם אסמכתה ושימוש עסקי |
| תקשורת | בזק, פרטנר, סלקום, פלאפון, HOT | חלקי או מוכר לפי שימוש |
| נסיעות ודלק | פז, סונול, דלק, דור אלון, חניה | חלקי/בדיקה |
| מזון ואירוח | Wolt, מסעדות, בתי קפה, תן ביס, סיבוס | בדיקה |
| שכירות ותפעול | שכירות משרד, חלל עבודה, דמי ניהול | לרוב מוכר/בדיקה |
| ביטוח | אחריות מקצועית, ביטוח עסקי, הראל, מגדל, מנורה | לרוב מוכר/בדיקה |
| שכר והטבות | שכר, פנסיה, קופת גמל, ניכויים | בדיקה |
| שירותים מקצועיים | רואה חשבון, עורך דין, יועץ | לרוב מוכר עם חשבונית |
| שיווק ופרסום | Google Ads, Meta, Taboola, Outbrain | לרוב מוכר עם חשבונית |
| ציוד ומשרד | KSP, אייבורי, מחשב, ציוד משרדי | בדיקה; ייתכן רכוש קבוע |
| העברות וארנקים | העברה בנקאית, BIT, PayBox | בדיקה |
| פרטי/בדיקה | סופרמרקט, פארם, קמעונאות ביתית | בדרך כלל לא מוכר ללא נסיבות מיוחדות |
| לא מסווג | שורות שלא נמצאה להן התאמה | בדיקה |

## עץ החלטה

```mermaid
flowchart TD
    A[קריאת שורת תנועה] --> B{יש תאריך ותיאור תקינים?}
    B -- לא --> Z[דחיית שורה או סימון קלט שגוי]
    B -- כן --> C{קיים סכום חתום או זוג חובה/זכות?}
    C -- לא --> Z
    C -- כן --> D[נרמול טקסט עברי/אנגלי וסימן סכום]
    D --> E{נמצא כלל ישראלי בעדיפות גבוהה?}
    E -- כן --> F[הקצאת קטגוריה, תת-קטגוריה, דגל מע"מ, ניכוי ורמת ביטחון]
    E -- לא --> G{תנועת זכות?}
    G -- כן --> H{נראית כמו שכר, סליקה, תשלום לקוח, ארנק או העברה?}
    H -- כן --> I[סיווג כהכנסה או העברה וסימון לאימות]
    H -- לא --> J[הכנסה לא מסווגת, בדיקה נדרשת]
    G -- לא --> K{ספק, רשות, עמלת בנק, חיוב כרטיס או התחייבות מוכרים?}
    K -- כן --> F
    K -- לא --> L[הוצאה לא מסווגת, בדיקה נדרשת]
    F --> M{קיימת חתימת כפילות?}
    I --> M
    J --> M
    L --> M
    M -- כן --> N[הוספת possible-duplicate]
    M -- לא --> O[שמירת תנועה יחידה]
    N --> P[ייצוא שורה מסווגת]
    O --> P
```

## כללי סיווג

סווג בסדר הבא: מסים ורשויות, עמלות בנק, הלוואות, חיובי כרטיס, ספקים ספציפיים, קבוצות ספקים כלליות, העברות וארנקים, ולבסוף בדיקה ידנית. השתמש במסנן כיוון תנועה כדי למנוע התאמות שגויות. תן עדיפות לכללים ספציפיים על פני כללים כלליים.

## כללים מותאמים

```json
[
  {
    "id": "client_acme_revenue",
    "category": "Income",
    "subcategory": "Client payment",
    "patterns": ["ACME LTD", "אקמי בע\"מ"],
    "direction": "credit",
    "vat_relevant": true,
    "tax_deductibility": "review",
    "confidence": 0.98,
    "priority": 200
  }
]
```

## מקרי קצה ישראליים

### עמודות חובה וזכות

יצוא ישראלי נפוץ מפריד בין חובה לזכות. חובה הופכת לסכום שלילי וזכות לסכום חיובי.

### חיוב כרטיס אשראי מרוכז

שורה כגון `ישראכרט 02/2026` אינה פירוט העסקאות בכרטיס. בצע התאמה מול פירוט הכרטיס.

### BIT ו-PayBox

אותו תיאור יכול לציין תשלום לקוח, החזר פרטי, העברה משפחתית או משיכת בעלים. סמן לאימות.

### זיכויים וביטולים

שמור גם את שורת החיוב וגם את שורת הזיכוי. בדוק את הקיזוז מול אסמכתאות.

### משיכת מזומן

סווג כמשיכת מזומן ודרוש קבלות לפני שיוך עסקי.

### הלוואות ומימון

הפרד קרן, ריבית ועמלות לבדיקת מנהל חשבונות.

### מטבע חוץ

סווג לפי ספק כאשר אפשר, ואת עמלות ההמרה בנפרד.

### קידוד עברית

קרא UTF-8 עם BOM ו-Windows-1255; שמור מקור ונרמל רק להתאמה.


## תהליך עבודה מומלץ

1. ייצא תנועות לתקופה הנדרשת.
2. שמור עותק מקור ללא שינוי.
3. הרץ סיווג.
4. מיין לפי `confidence` מהנמוך לגבוה.
5. בדוק `needs-review`, `possible-duplicate`, `confirm-business-income`, `partial` ו-`review`.
6. התאם חיובי כרטיס מול פירוט כרטיס.
7. הוסף כללים לספקים חוזרים.
8. הרץ מחדש.
9. ייצא CSV או JSON סופי.
10. העבר לרואה החשבון או למנהל החשבונות יחד עם אסמכתאות.

## פעולות שגויות שיש להימנע מהן

- Treating output as final tax filing.
- Uploading unredacted bank statements to unapproved services.
- Assuming every positive transfer is taxable revenue.
- Assuming every debit in a business account is deductible.
- Classifying aggregate credit-card settlements as supplier expenses.
- Deleting or overwriting original bank exports.
- Hard-coding client names in public rules.
- Mixing household and business statements without review flags.
- Ignoring low-confidence rows.
- Using online-banking credentials in scripts or examples.

## רשימת בדיקות לפני שימוש שוטף

- Confirm statement period and bank account.
- Verify opening/closing balances against the bank export.
- Confirm every row has date, description, and signed amount.
- Review all low-confidence, wallet, duplicate, personal, and uncategorized rows.
- Reconcile aggregate card settlements against detailed card statements.
- Separate owner withdrawals, owner loans, personal transfers, and business income.
- Confirm VAT relevance with invoice/receipt evidence.
- Keep custom rules versioned.
- Store raw statements with access control and retention rules.
- Run pytest after code or rule-format changes.
