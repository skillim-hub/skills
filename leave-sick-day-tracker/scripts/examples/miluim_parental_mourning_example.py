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
    employee_id = os.getenv("LEAVE_TRACKER_EMPLOYEE_ID", "E003")
    tracker = LeaveTrackerClient([EmployeeProfile(employee_id, "Noa Israel", os.getenv("LEAVE_TRACKER_HIRE_DATE", "01/01/2022"))])
    tracker.record_event(LeaveEvent(employee_id, "miluim", os.getenv("LEAVE_TRACKER_MILUIM_START", "03/03/2024"), os.getenv("LEAVE_TRACKER_MILUIM_END", "14/03/2024")))
    tracker.record_event(LeaveEvent(employee_id, "parental", os.getenv("LEAVE_TRACKER_PARENTAL_START", "01/05/2024"), os.getenv("LEAVE_TRACKER_PARENTAL_END", "31/05/2024"), days=0))
    tracker.record_event(LeaveEvent(employee_id, "mourning", os.getenv("LEAVE_TRACKER_MOURNING_START", "01/10/2024"), os.getenv("LEAVE_TRACKER_MOURNING_END", "08/10/2024"), days=8))
    emit({"environment": args.env, "balance": tracker.balance(employee_id, os.getenv("LEAVE_TRACKER_AS_OF", "31/12/2024")).to_dict()})


if __name__ == "__main__":
    main()
