# Hebrew Quality Assurance Log

## Scope

Reviewed `SKILL_HE.md` and Hebrew-facing examples for terminology, spelling, tone, date conventions, and currency conventions.

## Changes applied

| Area | Before | After | Reason |
|---|---|---|---|
| Technical prose | Mixed date examples with dashes | DD/MM/YYYY examples, such as 15/06/2026 | Match common Israeli presentation in user-facing Hebrew |
| Currency | NIS references in prose | ₪ where an amount is displayed | Match Israeli accounting notation |
| Role terminology | Loanword for freelance workers | נותני שירותים עצמאיים where natural | Prefer Hebrew professional terminology |
| Tone | Explanatory wording mixed with guidance | Imperative operational wording | Keep neutral, task-oriented style |
| Vowels | Checked for Hebrew vowel marks | No vowel marks in technical prose | Keep standard professional Hebrew |
| Legal and accounting wording | Reviewed terms for tax and payroll context | דמי ביטוח, מקדמות, טופס 102, הנהלת חשבונות, אסמכתה, הוראת קבע | Use accepted Israeli professional terms |

## Terminology decisions

- Use `דמי ביטוח` for National Insurance contribution amounts.
- Use `מקדמות` for self-employed advance payments.
- Use `טופס 102` for employer monthly reporting.
- Use `הנהלת חשבונות` and `פקודת יומן` for bookkeeping records.
- Use `אזור אישי` for the official personal-service portal.
- Keep `CSV`, `JSON`, `ICS` and `CLI` as technical file or interface names because these are standard abbreviations in Israeli technical documentation.

## Validation checks

- No nikud or cantillation marks remain in Hebrew technical prose.
- Hebrew examples use ₪ for monetary amounts and DD/MM/YYYY for localized dates.
- Public Hebrew text avoids branding, authorship attribution, hosted visual assets, and emoji.

## v2.2.0 final Hebrew validation

| Area | Change | Result |
|---|---|---|
| מספרים ותאריכים | הוחלפו תאריכים ל-DD/MM/YYYY ונשמר סימון ₪ לפני סכומים | עומד בלוקליזציה ישראלית |
| מונחי תשלום | הועדפו דמי ביטוח, דמי ביטוח בריאות, מקדמות, טופס 102, הוראת קבע, מדרגת גבייה מופחתת | מונחים מקצועיים מקובלים בישראל |
| קול ניטרלי | נשמר ניסוח ציווי מקצועי ללא גוף ראשון | מתאים לשימוש תפעולי |
| שיעורי 2026 | נוספו ברירות מחדל מאומתות: 7.70%, 18.00%, 8.78%, 19.77%, ₪266 | תוקן מול המקורות הרשמיים והמשניים |
| ניקוד | לא נוסף ניקוד לטקסט טכני | עומד בדרישה |
