#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os

from leave_sick_day_tracker import EmployeeProfile, LeaveEvent, LeaveTrackerClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("LEAVE_TRACKER_ENV", "sandbox"))
    return parser.parse_args()


def emit(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    args = parse_args()
    employee_id = os.getenv("LEAVE_TRACKER_EMPLOYEE_ID", "E001")
    as_of = os.getenv("LEAVE_TRACKER_AS_OF", "31/12/2024")
    work_week_days = int(os.getenv("LEAVE_TRACKER_WORK_WEEK_DAYS", "5"))
    tracker = LeaveTrackerClient([
        EmployeeProfile(
            employee_id,
            os.getenv("LEAVE_TRACKER_EMPLOYEE_NAME", "Dana Levi"),
            os.getenv("LEAVE_TRACKER_HIRE_DATE", "01/01/2024"),
            work_week_days=work_week_days,
        )
    ])
    tracker.record_event(LeaveEvent(employee_id, "annual", os.getenv("LEAVE_TRACKER_ANNUAL_START", "18/08/2024"), os.getenv("LEAVE_TRACKER_ANNUAL_END", "22/08/2024")))
    emit({"environment": args.env, "balance": tracker.balance(employee_id, as_of).to_dict()})


if __name__ == "__main__":
    main()
