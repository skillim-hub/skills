# Hebrew QA log

QA date: 03/06/2026

## Goals

Ensure that Hebrew public documentation is practical for Israeli small businesses, freelancers, and consumers. Keep the tone neutral, direct, and professional.

## Changes made

| Area | Change |
|---|---|
| Voice | Rewrote guidance in imperative and neutral form |
| Localization | Standardized dates to DD/MM/YYYY in examples |
| Currency | Standardized budget and fees to ₪ notation |
| Disclosure | Used clear terms such as `גילוי מסחרי`, `פרסומת`, `בשיתוף`, `ממומן`, and `תוכן שיווקי` |
| Accounting terminology | Used `חשבונית`, `קבלה`, `מע"מ`, `תנאי תשלום`, and `ניכוי במקור` only where operationally relevant |
| Privacy terminology | Used `פרטים אישיים`, `הסכמה`, `שמירת מידע`, and `איסוף פרטים` |
| Marketing terminology | Used `יוצרי תוכן`, `משפיענים`, `תוצרים`, `קופון`, `קישור מדיד`, `לידים`, `שיעור המרה`, and `החזר על הוצאה` |
| Anglicisms | Replaced avoidable transliteration with natural Hebrew terms where a common term exists |
| Technical clarity | Kept common Israeli business terms where they are standard in daily professional use |
| Niqqud | Removed vowel marks from technical prose |
| Gender | Avoided gendered first-person phrasing and used neutral instructions |
| Legal caution | Added escalation points for privacy, tax, health, finance, minors, lotteries, and professional claims |

## Reviewed Hebrew files

| File | Result |
|---|---|
| `SKILL_HE.md` | Passed Hebrew style review |
| `README.md` | Passed localized examples review |
| `references/api-reference.md` | Passed terminology review |
| `references/workflow-guide.md` | Passed workflow terminology review |
| `references/troubleshooting.md` | Passed troubleshooting terminology review |
| `references/test-scenarios.md` | Passed scenario terminology review |
| `references/migration-checklist.md` | Passed migration terminology review |

## Final status

| Check | Status |
|---|---|
| Niqqud in technical prose | None found |
| Neutral imperative voice | Applied |
| ₪ notation | Applied |
| DD/MM/YYYY examples | Applied |
| Professional Israeli terminology | Applied |
| Disclosure terminology | Applied |

## Web-validated Hebrew terminology update for 03/06/2026

| Area | Change |
|---|---|
| מע"מ | Standardized the acronym to `מע"מ` in Hebrew prose and generated outreach text |
| גילוי מסחרי | Kept neutral wording that requires clear disclosure but does not present one fixed phrase as the only lawful phrase |
| דיוור ישיר | Kept `דיוור ישיר`, `הסכמה`, and `דבר פרסומת` as the professional terms for lead-marketing risk |
| תאריכים | Kept DD/MM/YYYY in Hebrew examples and CLI input examples |
| רגולציה | Added a verification log rather than embedding unstable thresholds in prose |
