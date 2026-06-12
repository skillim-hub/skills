# Migration Checklist

Use this checklist when upgrading from the previous package or from informal onboarding files.

## Package migration

- [ ] Extract the old package.
- [ ] Remove any branding, visual marks, creator names, status-link artifacts, image references, and promotional callouts.
- [ ] Delete the hyphenated client script.
- [ ] Place the real client implementation in `scripts/employee_onboarding_guide_client.py`.
- [ ] Update imports to use `employee_onboarding_guide_client`.
- [ ] Keep the CLI wrapper at `scripts/employee-onboarding-guide-cli.py` for command-line convenience.
- [ ] Make modules installable through `pip install -e .`.
- [ ] Add `pytest-asyncio` to development requirements.
- [ ] Update README install instructions.
- [ ] Add local create response and follow-up checklist flow.
- [ ] Update Hebrew materials to DD/MM/YYYY.
- [ ] Add branding audit and Hebrew QA log.
- [ ] Run pytest.
- [ ] Run compileall on scripts.
- [ ] Rebuild the archive.

## Employer data migration

- [ ] Move employee records into restricted storage.
- [ ] Convert Hebrew date examples to DD/MM/YYYY.
- [ ] Keep English date examples as DD-MM-YYYY.
- [ ] Replace net salary notes with payroll-reviewed gross salary terms.
- [ ] Add pension status field.
- [ ] Add another-employer field.
- [ ] Add secure upload instructions.
- [ ] Add timekeeping owner.
- [ ] Add payroll close deadline.
- [ ] Add annual Form 101 renewal reminder.
- [ ] Add annual coordination renewal reminder for employees with multiple income sources.
- [ ] Remove unnecessary local copies of ID, bank, pension, and medical documents.
