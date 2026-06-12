from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from event_scheduler_invitation import EventSchedulerClient


def parse_env() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("EVENT_SCHEDULER_ENV", "sandbox"))
    parser.add_argument("--csv", default=os.getenv("EVENT_SCHEDULER_GUEST_CSV", str(Path(__file__).with_name("sample_guests.csv"))))
    return parser.parse_args()


def main() -> None:
    args = parse_env()
    client = EventSchedulerClient()
    guests = client.import_guests_csv(args.csv)
    reminders = [
        client.build_rsvp_message(
            name=guest.name,
            event_title=os.getenv("EVENT_SCHEDULER_EVENT_TITLE", "אירוע משפחתי"),
            event_date=os.getenv("EVENT_SCHEDULER_EVENT_DATE", "18/06/2026"),
            deadline=os.getenv("EVENT_SCHEDULER_RSVP_DEADLINE", "01/06/2026"),
        )
        for guest in guests
        if guest.status.value == "no_response"
    ]
    print(json.dumps({
        "env": args.env,
        "summary": client.rsvp_summary(guests),
        "reminders": reminders,
    }, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
