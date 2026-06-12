# Hebrew QA Log

Date: 04/06/2026

## Scope

Reviewed `SKILL_HE.md` and Hebrew-facing snippets in public reference material.

## Changes made

| Area | Change |
|---|---|
| Date localization | Replaced DD-MM-YYYY with DD/MM/YYYY and changed example date to 04/06/2026 |
| Currency | Kept Israeli currency examples with ₪ |
| Technical terms | Replaced avoidable Anglicisms with Hebrew terms: תשאול מחזורי, חריגת זמן, השהיה מדורגת, פענוח נתונים, תוכן תגובה |
| Imperative voice | Reworked checklist items into direct imperative wording |
| Neutral style | Removed first-person phrasing and promotional tone |
| Emergency wording | Kept action-first instructions for active alerts |
| Accessibility wording | Kept professional wording for עובדים עם מוגבלות and מרחב נגיש |
| Privacy wording | Kept direct instructions to avoid storing precise location without explicit request |
| Niqqud | Verified no Hebrew vowel marks appear in technical prose |
| Business language | Kept Israeli business terms: המשכיות עסקית, יומן אירוע, תרגול, אחראי משמרת |

## Terms approved

| Term | Approved Hebrew |
|---|---|
| protected space | מרחב מוגן |
| public shelter | מקלט ציבורי |
| residential protected room | ממ"ד |
| alert area | אזור התרעה |
| active alert | התרעה פעילה |
| polling | תשאול מחזורי |
| timeout | חריגת זמן |
| backoff | השהיה מדורגת |
| parsing | פענוח נתונים |
| response payload | תוכן תגובה |
| business continuity | המשכיות עסקית |
| incident log | יומן אירוע |

## Remaining notes

- Official safety wording should be reviewed against the current Home Front Command text before production deployment.
- Municipal shelter datasets may use inconsistent Hebrew field names; keep aliases configurable.


## Web validation additions

Date: 04/06/2026

- Confirmed official Hebrew terminology: יישומון פיקוד העורף, אמצעי התרעה אישי, מרחב מוגן, מקלט ציבורי.
- Kept DD/MM/YYYY date localization.
- Kept ₪ currency examples.
- Replaced any implication of complete nationwide shelter coverage with configured-dataset wording.
- Kept endpoint wording configurable because no official public API contract for `alerts.json` was confirmed.
