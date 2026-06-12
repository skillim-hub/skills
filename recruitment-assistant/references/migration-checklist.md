# Migration Checklist

## From the previous enhanced package

1. Delete hyphenated Python client filenames from local integrations.
2. Import from the installable package:

```python
from recruitment_assistant import Candidate, RecruitmentAssistantClient, RoleProfile
```

3. Replace old script references with:
   - `scripts/recruitment_assistant_client.py`
   - `scripts/recruitment_assistant_cli.py`
   - `scripts/test_recruitment_assistant_client.py`
4. Install with:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

5. Replace quick-start snippets that created a candidate without reusing the identifier.
6. Extract `id` from `create_candidate`.
7. Retrieve or pass the candidate by that identifier in the next step.
8. Update examples to accept `--env sandbox` or `--env production`.
9. Read API keys and environment defaults from environment variables.
10. Use `json.dumps(..., ensure_ascii=False, indent=2)` for Hebrew-safe output.
11. Confirm `pytest-asyncio` appears in development requirements.
12. Run the full test suite.
13. Run compile checks for scripts.
14. Update local documentation links to the new reference files.
15. Confirm candidate-facing dates use DD/MM/YYYY.
16. Confirm salary text uses ₪.
17. Remove any external visual-asset references from local copies.
18. Remove any named organizational ownership from metadata.
19. Keep the license notice as required.
20. Save a copy of the branding audit and Hebrew QA log with the hiring project.

## From a manual spreadsheet process

1. Convert role criteria into a `RoleProfile`.
2. Separate required skills from preferred skills.
3. Remove personal or protected criteria.
4. Convert each resume to UTF-8 text.
5. Run batch screening.
6. Review every `review` result manually.
7. Export the shortlist JSON.
8. Schedule interviews only for candidates approved for contact.
9. Store decision notes in the hiring file.
10. Delete candidate data when the hiring purpose ends.

## Rollback plan

1. Keep the previous package archive until the new test suite passes.
2. Keep a copy of role profiles used in production.
3. Export screening results before changing thresholds.
4. Restore the prior package only if imports, CLI execution, or screening outputs fail acceptance tests.
5. Do not roll back compliance fixes that remove protected criteria.
