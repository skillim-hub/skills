from __future__ import annotations

import argparse
import json
import os

from event_scheduler_invitation import EventSchedulerClient, EventType, Guest, RSVPStatus, Vendor


def parse_env() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("EVENT_SCHEDULER_ENV", "sandbox"))
    return parser.parse_args()


def print_json(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def main() -> None:
    args = parse_env()
    client = EventSchedulerClient()
    plan = client.create_plan(
        event_type=EventType.BAR_MITZVAH,
        event_date=os.getenv("EVENT_SCHEDULER_EVENT_DATE", "07/11/2026"),
        title=os.getenv("EVENT_SCHEDULER_EVENT_TITLE", "בר המצווה של נועם"),
        city=os.getenv("EVENT_SCHEDULER_DEFAULT_CITY", "ירושלים"),
    )
    guests = [
        Guest("משפחת כהן", party_size_confirmed=5, status=RSVPStatus.CONFIRMED, group="משפחה"),
        Guest("משפחת לוי", party_size_confirmed=4, status=RSVPStatus.CONFIRMED, group="משפחה"),
        Guest("חברים מהכיתה", party_size_confirmed=10, status=RSVPStatus.CONFIRMED, group="חברים"),
    ]
    print_json({
        "env": args.env,
        "event_id": plan.event_id,
        "tables": client.assign_tables(guests, table_size=int(os.getenv("EVENT_SCHEDULER_TABLE_SIZE", "10"))),
    })


if __name__ == "__main__":
    main()
