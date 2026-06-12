# Test Scenarios

Use these scenarios to validate behavior before production use. Each scenario includes input focus and expected outcome.

| Number | Scenario | Expected outcome |
| --- | --- | --- |
| 1 | Hebrew bookkeeper with חשבשבת and אקסל | Advance for accounting role requiring those tools. |
| 2 | English developer with Python and SQL | Advance for mid software role when years match. |
| 3 | Developer missing SQL | Review or decline depending on score threshold. |
| 4 | Customer-service resume with CRM and phone support | Advance for junior customer-service role. |
| 5 | Marketing resume with PPC and SEO | Normalize to marketing and match both terms. |
| 6 | Resume has no email | Add note that email was not detected. |
| 7 | Resume has no phone | Add note that Israeli phone number was not detected. |
| 8 | Resume includes Hebrew and English | Detect both languages. |
| 9 | Candidate has 1 year for senior role | Penalize seniority mismatch and route to review or decline. |
| 10 | Candidate has 8 years for senior role | Detect seniority as senior. |
| 11 | Candidate has ראש צוות | Detect seniority as lead. |
| 12 | Candidate has מנהלת תפעול | Normalize to operations or manager seniority where appropriate. |
| 13 | Job ad says צעיר | Validation fails and suggests job-related wording. |
| 14 | Job ad says אחרי צבא | Validation fails unless separately documented outside automation. |
| 15 | Job ad says מראה ייצוגי | Validation fails and suggests communication requirements. |
| 16 | Candidate includes age | Ignore age in scoring. |
| 17 | Candidate includes family status | Ignore family status in scoring. |
| 18 | Start date is Friday | First slot moves to the next default interview day unless an exception policy is passed manually. |
| 19 | Daily interview window fills up | Scheduler moves remaining candidates to the next business day. |
| 20 | Batch candidates have equal score | Rank deterministically by candidate name. |
| 21 | Role profile uses duplicate skills | Duplicate terms are normalized once. |
| 22 | Salary range is in ₪ | Preserve numeric ILS values and display as ₪ in public text. |
| 23 | Date appears in candidate-facing text | Format as DD/MM/YYYY. |
| 24 | CLI receives invalid environment | Return a validation error. |
| 25 | Empty resume text | Raise a validation error. |
| 26 | Unknown candidate identifier | Raise a validation error. |
| 27 | Mixed freelance projects | Count job-related skills and years when stated. |
| 28 | Accommodation request appears | Route to manual review outside automated decline. |

## Scenario script template

```python
from recruitment_assistant import Candidate, RecruitmentAssistantClient, RoleProfile

client = RecruitmentAssistantClient(env="sandbox")
role = RoleProfile(title="Customer Service", required_skills=["customer service", "crm"], seniority="junior")
candidate = Candidate(name="Omer", resume_text="omer@example.com CRM customer service 2 years experience")
result = client.screen_resume(candidate, role)
assert result.recommendation in {"advance", "review"}
```

## Acceptance gates

- At least twenty scenarios pass in automated or manual validation.
- Hebrew and English resumes are both represented.
- Compliance validation includes Hebrew and English disallowed terms.
- Scheduling covers conservative Friday and Saturday skip behavior and documented overrides.
- Date examples intended for candidates use DD/MM/YYYY.
- Salary examples use ₪.
