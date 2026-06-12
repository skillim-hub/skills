# Hebrew Quality Assurance Log

## Scope

Reviewed `SKILL_HE.md` and Hebrew examples in public Markdown for natural Israeli professional terminology, localization, neutral imperative voice, and technical consistency.

## Localization checks

| Area | Result |
| --- | --- |
| Currency | Uses ₪ for shekel amounts. |
| Dates | Uses `DD/MM/YYYY` in Hebrew-facing examples and accepts `DD-MM-YYYY`. |
| Terminology | Uses נדלן, שכירות, רכישה, ארנונה, ועד בית, דמי תיווך, מעמ, נסח טאבו, אישור זכויות, רישוי עסק, שימוש מותר, סיווג ארנונה, נגישות. |
| Voice | Uses neutral procedural phrasing such as `יש לבדוק`, `להגדיר`, `לשמור`, and `לאמת`. |
| Technical clarity | Keeps source names and code identifiers in English only when they are command values or site names. |
| Nikud | No Hebrew vowel marks retained in technical prose. |

## Changes made in v2

| Area | Change |
| --- | --- |
| Opening purpose | Rewrote the Hebrew guide around practical Israeli workflow terms rather than literal translation. |
| Commercial workflow | Added רישוי עסק, שימוש מותר, סיווג ארנונה, מעמ, שילוט, נגישות and דמי ניהול. |
| Purchase workflow | Added נסח טאבו, אישור זכויות, שעבודים, מידע תכנוני and עלויות רכישה. |
| Rental workflow | Added פיקדון, דמי תיווך, ארנונה, ועד בית, תיקונים, יציאה מוקדמת and אופציית הארכה. |
| Date localization | Replaced day-month examples with `15/07/2026`. |
| Currency localization | Replaced textual shekel references in user-facing examples with ₪ where amounts appear. |
| Tone | Removed first-person phrasing and kept imperative/procedural language. |
| Anglicisms | Replaced avoidable English phrasing with Hebrew terms; retained Yad2, Madlan, Komo and code values. |

## Review notes

- Site names remain in Latin characters because they are brand names and CLI source values.
- Code identifiers remain in English because they are part of the Python and CLI interface.
- Legal and tax topics are phrased as checks and references, not as legal advice.

## 1.3.0 web-validated Hebrew corrections

- תוקן ניסוח "מעמ מס" ל-"מע״מ" בעץ ההחלטה.
- הוחלף ניסוח גורף על מסנני שכונה בניסוח מדויק: מסנן שכונה כאשר אתר המקור תומך בכך, ובדיקה ידנית כאשר אין פרמטר מאומת.
- עודכנה שורת Komo כדי להבהיר שימוש בעמודי עיר ובסינון שכונה ידני.
- נשמרה כתיבה טכנית ללא ניקוד.
- נשמרו תאריכים בתצוגת DD/MM/YYYY וסכומים עם ₪.
