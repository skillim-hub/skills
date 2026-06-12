# Annual Leave and Sick-Day Tracker

Local toolkit for tracking Israeli annual leave, sick days, reserve duty, birth and parenthood leave, and mourning days. Use it as an installable Python package, a command-line tool, or a CSV workflow helper.

## Install

```bash
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create one employee, extract the generated identifier, then use that identifier for the next event command.

```bash
EMPLOYEE_ID=$(leave-sick-day-tracker create-employee \
  --employee-id E001 \
  --name "Dana Levi" \
  --hire-date 01/01/2024 \
  | python -c 'import json,sys; print(json.load(sys.stdin)["employee"]["employee_id"])')

leave-sick-day-tracker add-event \
  --employee-id "$EMPLOYEE_ID" \
  --absence-type annual \
  --start-date 18/08/2024 \
  --end-date 22/08/2024
```

Generate CSV templates and calculate balances.

```bash
leave-sick-day-tracker template ./sample-data
leave-sick-day-tracker summary ./sample-data/employees.csv ./sample-data/events.csv --as-of 31/12/2024
```

## Python quick start

```python
from leave_sick_day_tracker import EmployeeProfile, LeaveEvent, LeaveTrackerClient

employee = EmployeeProfile("E001", "Dana Levi", "01/01/2024")
tracker = LeaveTrackerClient([employee])
tracker.record_event(LeaveEvent("E001", "annual", "18/08/2024", "22/08/2024"))
print(tracker.balance("E001", "31/12/2024").to_dict())
```

## File index

- `SKILL.md`: English operating guide.
- `SKILL_HE.md`: Hebrew operating guide for Israeli users.
- `references/api-reference.md`: regulation and data-interface reference.
- `references/workflow-guide.md`: end-to-end workflows.
- `references/troubleshooting.md`: fixes for common data and payroll issues.
- `references/test-scenarios.md`: concrete scenarios for acceptance testing.
- `references/migration-checklist.md`: migration and rollout checklist.
- `references/branding-audit.md`: neutral-content audit.
- `references/hebrew-qa-log.md`: Hebrew terminology and localization review log.
- `references/verification-log.md`: live-source validation log for the 2026 pass.
- `leave_sick_day_tracker/`: installable Python package.
- `scripts/leave_sick_day_tracker_client.py`: underscored client implementation.
- `scripts/leave_sick_day_tracker_cli.py`: underscored command-line implementation.
- `scripts/test_leave_sick_day_tracker_client.py`: pytest suite.
- `scripts/examples/`: runnable scenarios using environment variables and `--env sandbox|production`.

## Development checks

```bash
pytest
python -m compileall scripts/ -q
```

## Legal and payroll caution

Use this package as an operational tracker. Confirm final wage treatment, sector-specific extension orders, collective agreements, 2026 reserve-duty extension-order effects, and unusual cases with qualified payroll or legal advice.
