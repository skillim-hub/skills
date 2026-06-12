# Test scenarios

Use these scenarios to validate rules, documentation, support flows, and user-facing messages. The expected result is preliminary and must be verified against official sources before operational advice.

| # | Scenario | Key input | Expected preliminary result |
| --- | --- | --- | --- |
| 1 | Laid-off employee, full qualifying period | age 44, resident, 16 qualifying months, registered, `laid_off` | unemployment `likely_eligible` |
| 2 | Fired employee, missing registration | age 37, 14 qualifying months, `fired`, not registered | unemployment `insufficient_information` |
| 3 | Voluntary resignation | age 35, 14 qualifying months, registered, `resigned` | unemployment `possibly_eligible` with waiting-period warning |
| 4 | Justified resignation | age 35, 14 qualifying months, registered, `resigned_justified` | unemployment `likely_eligible` if evidence exists |
| 5 | End of contract | age 29, 12 qualifying months, registered, `end_of_contract` | unemployment `likely_eligible` |
| 6 | Current freelancer | age 41, self-employed, business not closed | unemployment `not_likely` |
| 7 | Freelancer closed business | age 41, self-employed, `business_closed`, business closed | unemployment `likely_eligible` if official path applies |
| 8 | Too few qualifying months | age 28, 4 qualifying months, registered | unemployment `not_likely` |
| 9 | Under unemployment age range | age 18, registered, qualifying months entered | unemployment `not_likely` unless exception applies |
| 10 | Late Employment Service registration | age 52, registered but not within 3 months | unemployment `likely_eligible` with warning |
| 11 | Disability with complete strong data | age 49, medical 65, capacity loss 75 | general disability `likely_eligible` |
| 12 | Disability missing capacity | age 49, medical 65, capacity missing | general disability `insufficient_information` |
| 13 | Disability medical below threshold | age 49, medical 25, capacity 75 | general disability `not_likely` |
| 14 | Disability capacity below threshold | age 49, medical 70, capacity 20 | general disability `not_likely` |
| 15 | Disability at retirement boundary | age 67, medical and capacity present | general disability `not_likely` |
| 16 | Child allowance with three young children | resident parent, three birth dates under 18 | child allowance `likely_eligible` |
| 17 | Child allowance with no birth dates | resident parent, child count 2, no dates | child allowance `possibly_eligible` |
| 18 | Child over 18 only | one birth date older than 18 | child allowance `not_likely` |
| 19 | Separated parents | children under 18, custody uncertainty in notes | child allowance `likely_eligible` with routing warning |
| 20 | Newborn not yet reflected in payment | child under 1 year, registry pending in notes | child allowance `likely_eligible`, require registry verification |
| 21 | Low-income single parent | single parent, 2 children, income ₪1,500, registered | income supplement `likely_eligible` |
| 22 | Low income but no work-test evidence | unemployed, income ₪1,500, not registered | income supplement `insufficient_information` |
| 23 | Household income above threshold | couple, income ₪11,000 | income supplement `not_likely` |
| 24 | Assets above limit | income low, `assets_exceed_limit` true | income supplement `not_likely` |
| 25 | Vehicle issue | income low, vehicle flag true | income supplement `likely_eligible` or `insufficient_information` with warning |
| 26 | Other benefit received | low income and concurrent benefit | income supplement warning |
| 27 | Invalid age | age 130 | profile `insufficient_information` with validation error |
| 28 | Negative income | monthly income -1 | validation error |
| 29 | Invalid child date | date string `2020/31/12` | child allowance missing valid date |
| 30 | Combined household after job loss | laid off, children, low current income | unemployment and child allowance likely; income supplement depends on household income |
| 31 | Mixed employee and self-employed | employee plus side business | unemployment requires salaried facts; income supplement uses household income |
| 32 | Recently released young applicant | age under 20 with release date note | unemployment or income supplement requires official exception review |
| 33 | Non-resident | resident false | most supported benefits `not_likely` |
| 34 | Applicant with medical data and current work income | medical 60, capacity 65, income ₪5,000 | disability likely with work-income warning |
| 35 | Profile store chain | create profile, extract `profile_id`, check profile | create response has id; check response uses same id |

## Scenario detail: chain test

1. Create profile.
2. Read `profile_id` from create response.
3. Pass `profile_id` to the check command.
4. Confirm the check response contains the same identifier.
5. Confirm every result includes status, reasons, missing information, documents, next steps, and warnings.

## Scenario detail: Hebrew localization

Use a Hebrew support script with:

- dates such as 02/06/2026
- amounts such as ₪4,711
- benefit terms such as דמי אבטלה, קצבת נכות כללית, קצבת ילדים, הבטחת הכנסה
- neutral imperative wording
- no unnecessary English terms where a Hebrew professional term exists

## Scenario detail: data minimization

Enter only operational fields. Do not enter:

- identity number
- full medical file
- bank account number
- full address
- employer confidential records

The checker should work with category-level facts and document checklists.
