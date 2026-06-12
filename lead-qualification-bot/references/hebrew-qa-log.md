# Hebrew QA Log

## Scope

Reviewed Hebrew public prose in `SKILL_HE.md`, Hebrew examples in references, README examples, scripts, and test fixtures.

## Corrections applied

| Area | Change |
|---|---|
| Technical prose | Confirmed no nikud in Hebrew technical prose. |
| Voice | Replaced first-person operational wording with neutral imperative or passive professional phrasing where appropriate. |
| Localization | Replaced DD/MM/YYYY references with DD/MM/YYYY. |
| Currency | Kept amounts in ₪ or clear "שח" examples where user input simulates informal WhatsApp text. |
| Terminology | Preserved professional terms: חשבונית מס, קבלה, חשבונית מס/קבלה, עוסק פטור, עוסק מורשה, חברה בע״מ, מע״מ, מס הכנסה, ביטוח לאומי, הסכמה, מדיניות פרטיות, הסרה. |
| Anglicisms | Kept platform/product names only where no natural Hebrew replacement exists, such as WhatsApp, CRM, webhook, API and SLA in technical integration contexts. |
| Customer-facing copy | Avoided unnecessary technical terms in user-facing Hebrew messages. |
| Gendered verbs | Used neutral or plural-friendly phrasing where possible: "אפשר להשאיר", "הפנייה תועבר", "נציג יחזור". |
| Sensitive cases | Reworded escalation text to avoid advice and avoid overpromising. |
| Dates | Updated examples such as 03/06/2026, 05/06/2026, 10/06/2026, and 01/07/2026. |

## Review notes

- Informal user inputs still include realistic WhatsApp phrasing such as "שח", "תא", and "ראשלצ" because these are test inputs, not polished technical prose.
- The term "בוט" remains because it is the common Israeli term for chatbot operation.
- The term "וואטסאפ" appears in public Hebrew documentation where the prose is Hebrew-first; `WhatsApp` remains in technical API contexts.
- Legal, medical, and tax flows use escalation language and avoid definitive professional advice.
