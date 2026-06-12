# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md`, Hebrew examples in `SKILL.md`, Hebrew snippets in references, and Hebrew strings in the Python client.

## Changes made

| Area | Change | Reason |
|---|---|---|
| Technical prose | Removed nikud from Hebrew technical prose. | Keep professional Israeli business writing. |
| Tone | Normalized to neutral imperative wording such as "שלח", "בדוק", "הסלם", "אל תאשר". | Avoid first-person voice and keep operational clarity. |
| Accounting terms | Used "חשבונית מס", "קבלה", "חשבונית מס/קבלה", "מסמך חשבונאי", "מערכת הנהלת החשבונות", "רואה החשבון". | Use standard Israeli terminology instead of transliteration. |
| Tax wording | Used "מעמ" and "מע״מ" according to context. | Preserve recognizable Israeli usage without unsupported advice. |
| Consumer wording | Used "ביטול עסקה", "זיכוי", "מדיניות העסק", "פרטי העסקה". | Match professional service terminology. |
| Privacy wording | Used "מידע אישי", "אימות זהות", "נוהל הפרטיות". | Avoid vague privacy phrasing. |
| Payment wording | Used "אמצעי התשלום", "ארבע ספרות אחרונות", "חיוב כפול". | Prevent unsafe requests for full card details. |
| Date format | Normalized customer-facing Hebrew guidance to DD/MM/YYYY. | Match Israeli localization requested for this package. |
| Currency format | Used ₪ for shekel amounts. | Match Israeli customer-facing formatting. |
| Mixed direction | Added guidance to separate English identifiers into their own lines. | Improve RTL/LTR readability in WhatsApp, email, and CRM. |

## Review decisions

- Keep English intent identifiers such as `delivery_status` inside code and tables because they are machine-readable labels.
- Keep `DD/MM/YYYY` as a visible format token in Hebrew documentation because it is the required user-facing date format.
- Avoid transliteration when a common Hebrew professional term exists.
- Do not use slang or overly casual Israeli phrasing in production templates.
- Do not add gendered personal phrasing that could mismatch the customer. Prefer neutral service wording and infinitive or imperative forms when possible.

## Remaining human review

- Validate Arabic and Russian production templates with fluent reviewers.
- Validate legal, tax, accessibility, privacy, and consumer-protection text against current official sources before automatic sending.

## V3 web-validation Hebrew QA changes

| Area | Change | Reason |
|---|---|---|
| Language scope | Replaced ranking-style wording with "ארבע שפות בעלות כיסוי שימושי גבוה". | No official 2026 source was found that ranks the exact four-language set as the four most common languages. |
| VAT terminology | Standardized to "מע״מ", "מס תשומות", "מספר הקצאה", and "חשבונית מס". | Match Israeli professional tax/accounting terminology. |
| Date and currency | Kept ₪ and DD/MM/YYYY in customer-facing examples. | Match Israeli support localization and package requirements. |
| Chat wording | Replaced "צאט" with "שיחה" in Hebrew prose. | Avoid unnecessary Anglicism where natural Hebrew exists. |
| Format wording | Replaced "פורמט" with "תבנית" where possible in Hebrew prose. | Prefer Hebrew terminology in technical guidance. |
| Voice | Kept imperative, neutral instructions without first-person phrasing. | Match neutral operational documentation style. |
