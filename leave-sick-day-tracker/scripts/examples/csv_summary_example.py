#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from leave_sick_day_tracker import LeaveTrackerClient, write_template_csvs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("LEAVE_TRACKER_ENV", "sandbox"))
    parser.add_argument("--directory", default=os.getenv("LEAVE_TRACKER_WORKDIR", "/tmp/leave-tracker-example"))
    args = parser.parse_args()
    directory = Path(args.directory)
    employees_csv = Path(os.getenv("LEAVE_TRACKER_EMPLOYEES_CSV", "")) if os.getenv("LEAVE_TRACKER_EMPLOYEES_CSV") else None
    events_csv = Path(os.getenv("LEAVE_TRACKER_EVENTS_CSV", "")) if os.getenv("LEAVE_TRACKER_EVENTS_CSV") else None
    if employees_csv is None or events_csv is None:
        employees_csv, events_csv = write_template_csvs(directory)
    tracker = LeaveTrackerClient.from_csv(employees_csv, events_csv)
    rows = [snapshot.to_dict() for snapshot in tracker.balances(os.getenv("LEAVE_TRACKER_AS_OF", "31/12/2024"))]
    print(json.dumps({"environment": args.env, "employees_csv": str(employees_csv), "events_csv": str(events_csv), "rows": rows}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
