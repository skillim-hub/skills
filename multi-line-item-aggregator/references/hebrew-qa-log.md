# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md` and Hebrew examples for professional Israeli terminology, neutral imperative voice, no niqqud in technical prose, and DD/MM/YYYY date localization.

## Changes made

| Area | Change |
|---|---|
| Date format | Replaced DD-MM-YYYY examples with DD/MM/YYYY. |
| Voice | Standardized to neutral plural imperative forms such as `השתמשו`, `חשבו`, `שמרו`, `ודאו`, and `בדקו`. |
| Terminology | Used `מע״מ`, `חשבונית מס`, `חשבונית עסקה`, `חשבונית זיכוי`, `עוסק`, `ח.פ.`, `הנהלת חשבונות`, `בסיס חייב`, and `שיעור אפס`. |
| Anglicisms | Avoided unnecessary transliteration where a standard Hebrew accounting term exists. |
| Currency | Kept shekel amounts with `₪` and two decimal places. |
| Rounding | Clarified `עיגול לאגורות`, `אגורות חלקיות`, and `שאריות`. |
| Gross and net | Used `ברוטו` and `נטו`, which are standard professional Israeli terms. |
| Environment | Used `סביבת ייצור` for production context. |
| Niqqud | Confirmed no niqqud characters appear in technical prose. Hebrew punctuation marks such as geresh and gershayim remain where standard. |

## Review notes

- The guide uses plural imperative to avoid gendered singular instructions.
- English field names remain in code and tables because they are schema keys.
- CLI flags remain in English because they are command syntax.
- The term `שיעור אפס` is used for zero-rate examples. Exemption treatment is not asserted without external validation.
- The package does not provide legal or tax advice and directs production use to official accounting software and professional verification.


## Web-validated update

תאריך גישה: 2026-06-02. נוספו הערות רגולטוריות בעברית ללא ניקוד, עם תאריכים בפורמט DD/MM/YYYY, שימוש ב-`מספר הקצאה`, `מס תשומות`, `חשבונית מס`, `סביבת ייצור`, ו-`סביבת בדיקות`.
