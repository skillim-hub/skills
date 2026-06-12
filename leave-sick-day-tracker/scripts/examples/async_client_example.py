#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os

from leave_sick_day_tracker import EmployeeProfile, LeaveTrackerClient


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("LEAVE_TRACKER_ENV", "sandbox"))
    args = parser.parse_args()
    employee_id = os.getenv("LEAVE_TRACKER_EMPLOYEE_ID", "E004")
    tracker = LeaveTrackerClient([EmployeeProfile(employee_id, "Tal Bar", os.getenv("LEAVE_TRACKER_HIRE_DATE", "01/01/2024"))])
    snapshot = await tracker.abalance(employee_id, os.getenv("LEAVE_TRACKER_AS_OF", "31/12/2024"))
    print(json.dumps({"environment": args.env, "balance": snapshot.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
