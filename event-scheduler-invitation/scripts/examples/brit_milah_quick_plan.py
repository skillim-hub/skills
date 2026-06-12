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
    birth_date = os.getenv("EVENT_SCHEDULER_BIRTH_DATE", "03/03/2026")
    result = client.create_plan(
        event_type=EventType.BRIT_MILAH,
        event_date=os.getenv("EVENT_SCHEDULER_EVENT_DATE", "10/03/2026"),
        title=os.getenv("EVENT_SCHEDULER_EVENT_TITLE", "ברית מילה"),
        city=os.getenv("EVENT_SCHEDULER_DEFAULT_CITY", "תל אביב"),
    )
    from event_scheduler_invitation import calculate_brit_milah_target_date

    print_json({
        "env": args.env,
        "contact_phone": os.getenv("EVENT_SCHEDULER_CONTACT_PHONE", ""),
        "plan": client.plan_response(result),
        "target": calculate_brit_milah_target_date(
            birth_date,
            after_sunset=os.getenv("EVENT_SCHEDULER_AFTER_SUNSET", "false").lower() == "true",
            medically_cleared=os.getenv("EVENT_SCHEDULER_MEDICALLY_CLEARED", "true").lower() == "true",
        ),
    })


if __name__ == "__main__":
    main()
