# Recruitment Assistant

Recruitment Assistant is a local Python helper for Israeli hiring workflows. Use it to screen Hebrew and English resumes, normalize role families and seniority, validate job-ad criteria, rank candidates, and generate interview slots using a conservative Sunday to Thursday default that can be changed when the business has a documented scheduling policy.

## Install

```bash
unzip recruitment-assistant-enhanced-v3.zip
cd recruitment-assistant
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a candidate and extract the identifier from the response, then reuse it in the next step.

```python
from recruitment_assistant import Candidate, RecruitmentAssistantClient, RoleProfile

client = RecruitmentAssistantClient(env="sandbox")

create_response = client.create_candidate(
    Candidate(
        name="Dana Levi",
        resume_text="dana@example.co.il 052-1234567 Python SQL 4 years experience",
    )
)
candidate_id = create_response["id"]
candidate = client.get_candidate(candidate_id)

role = RoleProfile(
    title="Mid Python Developer",
    required_skills=["python", "sql"],
    preferred_skills=["react"],
    seniority="mid",
)

screening_result = client.screen_resume(candidate, role)
print(screening_result.to_dict())
```

## CLI quick start

```bash
recruitment-assistant screen --resume resume.txt --role role.json --name "Dana Levi" --env sandbox
recruitment-assistant validate-ad --input job-ad.txt --env sandbox
recruitment-assistant schedule --shortlist shortlist.json --start-date 2026-06-07 --env sandbox
```

## File index

| Path | Purpose |
| --- | --- |
| `SKILL.md` | English operating guide with examples, decision trees, edge cases, and checklist. |
| `SKILL_HE.md` | Hebrew operating guide localized for Israeli terminology, ₪, and DD/MM/YYYY dates. |
| `references/api-reference.md` | Local JSON interfaces, optional connector patterns, regulations, and error tables. |
| `references/workflow-guide.md` | End-to-end workflows for small businesses, freelancers, and consumers. |
| `references/troubleshooting.md` | Operational diagnostics and recovery steps. |
| `references/test-scenarios.md` | More than twenty concrete validation scenarios. |
| `references/migration-checklist.md` | Upgrade checklist from earlier packages and manual processes. |
| `references/branding-audit.md` | Neutrality audit results and remediation notes. |
| `references/hebrew-qa-log.md` | Hebrew review log and localization changes. |
| `references/verification-log.md` | Web-validated regulatory and source verification log. |
| `scripts/recruitment_assistant_client.py` | Importable helper entry file with underscored name. |
| `scripts/recruitment_assistant_cli.py` | CLI launcher for local execution. |
| `scripts/test_recruitment_assistant_client.py` | Pytest suite. |
| `scripts/examples/` | Runnable examples using environment variables and `--env`. |
| `recruitment_assistant/` | Installable Python package. |

## Development

```bash
pytest
python -m compileall scripts/ -q
```

## Data handling

Process only information that is relevant to the role. Do not use age, marital status, pregnancy, disability, religion, ethnicity, nationality, gender, family status, or military service as scoring criteria unless a specific lawful requirement has been reviewed and documented. Keep shortlists, notes, and interview invitations proportionate to the hiring purpose.
