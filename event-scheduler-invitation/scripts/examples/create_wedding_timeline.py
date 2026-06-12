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
    city = os.getenv("EVENT_SCHEDULER_DEFAULT_CITY", "רחובות")
    event_date = os.getenv("EVENT_SCHEDULER_EVENT_DATE", "18/06/2026")
    plan = client.create_plan(
        event_type=EventType.WEDDING,
        event_date=event_date,
        title=os.getenv("EVENT_SCHEDULER_EVENT_TITLE", "חתונת מאיה ויונתן"),
        city=city,
    )
    milestones = client.generate_timeline(plan)
    print_json({
        "env": args.env,
        "plan": client.plan_response(plan),
        "milestones": [
            {"due_date": m.due_date, "title": m.title, "owner": m.owner, "urgency": m.urgency}
            for m in milestones
        ],
    })


if __name__ == "__main__":
    main()
