# Hebrew QA Log

## Scope

Reviewed Hebrew public documentation, Hebrew message templates, sample data, and CLI examples for Israeli professional terminology, neutral imperative voice, date localization, and readability.

## Changes made

| Area | Change |
|---|---|
| Date format | Updated Hebrew-facing examples and documentation to DD/MM/YYYY. Legacy date parsing remains supported for migration. |
| Currency format | Confirmed amounts are displayed with ₪ and two decimal places. |
| Technical terminology | Used terms such as מועד פירעון, יתרה פתוחה, תשלום חלקי, מכתב דרישה, תיק ראיות, דואר רשום, תביעה קטנה, ריבית פיגורים, ומוסר תשלומים. |
| Voice | Replaced first-person and plural assistant phrasing with neutral imperative phrasing. |
| Anglicisms | Preferred דוא״ל, תשלום, יתרה, נמען, ערוץ, אסמכתה, and תבנית where applicable. |
| Nikud | Confirmed no Hebrew nikud appears in technical prose. |
| Escalation language | Kept legal escalation careful and conditional; avoided threats and unverified interest claims. |

## QA notes

- WhatsApp remains written as וואטסאפ because that is the common Israeli product name in professional service workflows.
- Email appears as דוא״ל in Hebrew prose.
- API examples may keep English field names because they are machine-readable keys.
- Dates in JSON examples use strings so spreadsheets and bookkeeping exports can preserve leading zeros.
