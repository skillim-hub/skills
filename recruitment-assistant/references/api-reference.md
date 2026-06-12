# API and Reference Guide

## Scope

This package runs locally. It does not require an external Israeli government API and does not call any Israeli government host or endpoint. Treat this document as an interface reference for the local Python client, the CLI, optional calendar or email connectors, and Israeli regulatory guardrails that affect hiring workflows.

## Regulatory reference matrix

| Area | Israeli reference | Practical rule |
| --- | --- | --- |
| Equal hiring opportunity | Equal Employment Opportunities Law, 5748-1988 | Do not discriminate by age, sex, sexual orientation, marital status, pregnancy, fertility treatment, parenthood, race, religion, nationality, country of origin, worldview, party affiliation, reserve duty, or similar protected grounds. |
| Job-placement and advertisements | Employment Service Law, 5719-1959 | Keep job advertisements and screening criteria related to the role. Avoid unrelated preferences. |
| Privacy and candidate records | Protection of Privacy Law, 5741-1981 | Collect only needed candidate data, limit access, and delete data when the hiring purpose ends. |
| Workplace accommodations | Equal Rights for Persons with Disabilities Law, 5758-1998 | Do not screen out candidates due to disability. Route accommodation requests to a human process. |
| Pregnancy and parenthood | Women's Employment Law, 5714-1954 | Do not score pregnancy, fertility treatment, maternity status, or parenthood. |
| Work hours and scheduling | Hours of Work and Rest Law, 5711-1951 | Plan interviews around reasonable working hours and local rest-day practices. |
| Human dignity | Basic Law: Human Dignity and Liberty | Keep processing proportionate and respectful. |

This guide is not legal advice. For sensitive roles, obtain legal review before applying criteria that may affect protected groups.

## Verified-source notes

- Standard VAT is verified as 18% from 01/01/2025, but this package does not calculate VAT or payroll taxes. Use tax and payroll tooling for those calculations.
- The scheduler uses a conservative Sunday to Thursday default. This is a product default, not a statutory statement that every Israeli workplace follows those days. Document any Friday or other non-default interview policy.
- Internal score thresholds are operational defaults. They are not legal thresholds and must be tested against representative scenarios before production use.
- No webhook event names, Israeli API hosts, or official endpoint paths are implemented in this package. Optional calendar and email payloads are local connector patterns only.

## Python interface

### Create a client

```python
from recruitment_assistant import RecruitmentAssistantClient

client = RecruitmentAssistantClient(env="sandbox")
```

Allowed environments:

| Value | Use |
| --- | --- |
| `sandbox` | Local testing, examples, training, and repeatable development. |
| `production` | Real workflows after policy, retention, and access controls are approved. |

### Candidate schema

Request:

```json
{
  "name": "Dana Levi",
  "resume_text": "dana@example.co.il 052-1234567 Python SQL 4 years experience",
  "email": null,
  "phone": null,
  "languages": [],
  "source": "manual"
}
```

Response from `create_candidate`:

```json
{
  "id": "4bbd4b7905502c58",
  "candidate": {
    "name": "Dana Levi",
    "resume_text": "dana@example.co.il 052-1234567 Python SQL 4 years experience",
    "email": "dana@example.co.il",
    "phone": "052-1234567",
    "languages": ["english"],
    "source": "manual"
  }
}
```

### Role profile schema

```json
{
  "title": "Mid Python Developer",
  "required_skills": ["python", "sql"],
  "preferred_skills": ["react", "typescript"],
  "seniority": "mid",
  "role_family": "software",
  "location": "Tel Aviv",
  "salary_min_ils": 16000,
  "salary_max_ils": 22000,
  "languages": ["hebrew", "english"],
  "must_have_terms": [],
  "disallowed_terms": []
}
```

### Screen a resume

Request:

```python
from recruitment_assistant import Candidate, RoleProfile

result = client.screen_resume(
    Candidate(name="Dana Levi", resume_text="dana@example.co.il Python SQL 4 years experience"),
    RoleProfile(title="Mid Python Developer", required_skills=["python", "sql"], seniority="mid"),
)
```

Response:

```json
{
  "candidate_id": "4bbd4b7905502c58",
  "candidate_name": "Dana Levi",
  "score": 90,
  "recommendation": "advance",
  "matched_required": ["python", "sql"],
  "missing_required": [],
  "matched_preferred": [],
  "detected_seniority": "mid",
  "role_family": "software",
  "years_experience": 4.0,
  "compliance_flags": [],
  "notes": []
}
```

### Batch ranking

```python
ranked = client.rank_candidates(candidates, role)
shortlist = client.shortlist(candidates, role, minimum_score=75)
```

### Validate a job advertisement

Request:

```python
validation = client.validate_job_ad("דרוש צעיר אחרי צבא לשירות לקוחות")
```

Response:

```json
{
  "approved": false,
  "flags": ["צעיר", "אחרי צבא"],
  "suggestions": [
    "Avoid age preference. Describe required availability, workload, or experience instead.",
    "Avoid military-service criteria unless a documented legal or safety requirement applies."
  ]
}
```

### Schedule interviews

Request:

```python
slots = client.schedule_interviews(
    results=ranked,
    start_date="2026-06-07",
    interview_minutes=45,
    channel="video"
)
```

Response:

```json
[
  {
    "candidate_id": "4bbd4b7905502c58",
    "candidate_name": "Dana Levi",
    "start": "2026-06-07T09:00:00+03:00",
    "end": "2026-06-07T09:45:00+03:00",
    "timezone": "Asia/Jerusalem",
    "channel": "video"
  }
]
```

## CLI interface

### Screen

```bash
recruitment-assistant screen --resume resume.txt --role role.json --name "Dana Levi" --env sandbox
```

### Batch

```bash
recruitment-assistant batch --candidates candidates.json --role role.json --env sandbox
```

### Validate ad

```bash
recruitment-assistant validate-ad --input job-ad.txt --env sandbox
```

### Schedule

```bash
recruitment-assistant schedule --shortlist shortlist.json --start-date 2026-06-07 --env sandbox
```

## Optional connector patterns

### Calendar event payload

Use a calendar connector only after a candidate advances or a manual reviewer approves the candidate.

Request:

```json
{
  "summary": "Interview: Dana Levi",
  "start": "2026-06-07T09:00:00+03:00",
  "end": "2026-06-07T09:45:00+03:00",
  "timezone": "Asia/Jerusalem",
  "attendees": ["dana@example.co.il"],
  "description": "Interview for Mid Python Developer. Keep notes job-related."
}
```

Response:

```json
{
  "calendar_event_id": "event-123",
  "status": "created"
}
```

### Candidate email payload

Request:

```json
{
  "to": "dana@example.co.il",
  "subject": "Interview invitation",
  "body": "Hello Dana, please confirm the interview on 07/06/2026 at 09:00."
}
```

Response:

```json
{
  "message_id": "message-123",
  "status": "queued"
}
```

## Error table

| Code | Trigger | Recovery |
| --- | --- | --- |
| `INVALID_ENV` | Environment is not `sandbox` or `production`. | Pass `--env sandbox` during testing or `--env production` after approval. |
| `MISSING_RESUME` | Resume text is empty. | Add resume text before screening. |
| `UNKNOWN_CANDIDATE` | Candidate identifier does not exist in the current client instance. | Create the candidate again or load persisted records. |
| `INVALID_DATE` | Date is not `YYYY-MM-DD`. | Use ISO input for CLI and convert to DD/MM/YYYY only in candidate-facing text. |
| `INVALID_TIME_WINDOW` | Interview start time is after end time. | Set a valid working window. |
| `NO_ELIGIBLE_CANDIDATES` | Every result is declined. | Review criteria or schedule only manually approved candidates. |
| `COMPLIANCE_HOLD` | Role criteria include disallowed personal criteria. | Remove the criterion and rerun screening. |
| `CONTACT_MISSING` | Candidate lacks email or phone. | Request updated contact details before sending an invitation. |
| `DATA_RETENTION_REVIEW` | Old candidate data is being reused. | Confirm retention basis or delete records. |

## Field-level guidance

| Field | Keep | Avoid |
| --- | --- | --- |
| `required_skills` | Specific job skills such as `excel`, `sql`, `חשבשבת`. | Personality labels, age proxies, family status, appearance. |
| `preferred_skills` | Advantage skills that can improve score without excluding. | Hidden must-have requirements. |
| `languages` | Professional language proficiency needed for the work. | "Native" origin-based wording when proficiency is enough. |
| `salary_min_ils` and `salary_max_ils` | Salary range in ₪. | Salary history or personal financial status. |
| `notes` | Short job-related reason. | Medical, family, political, religious, or unrelated personal notes. |
