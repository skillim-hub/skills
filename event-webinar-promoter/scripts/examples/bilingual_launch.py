from __future__ import annotations

import argparse
import json
import os

from event_webinar_promoter import EventWebinarPromoterClient, sample_event


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("EWP_ENV", "sandbox"))
    return parser.parse_args()


def base_event(env: str) -> dict:
    event = sample_event()
    if env == "production":
        event["registration_url"] = os.getenv("EWP_REGISTRATION_URL", event["registration_url"])
        event["accessibility_contact"] = os.getenv("EWP_ACCESSIBILITY_CONTACT", event["accessibility_contact"])
    else:
        event["registration_url"] = os.getenv("EWP_SANDBOX_REGISTRATION_URL", "https://sandbox.example.co.il/register")
        event["accessibility_contact"] = os.getenv("EWP_SANDBOX_ACCESSIBILITY_CONTACT", "accessibility@sandbox.example.co.il")
    return event


def main() -> None:
    args = parse_args()
    client = EventWebinarPromoterClient()
    event = base_event(args.env)
    event["language"] = "bilingual"
    event["audience"] = os.getenv("EWP_AUDIENCE", "English-speaking entrepreneurs in Israel")
    plan = client.plan(event)
    payload = {
        "environment": args.env,
        "hebrew_landing_page": plan.copy["landing_page"],
        "english_summary": f"{event['event_name']} takes place on {event['date']} at {event['time']} Israel time. Register: {event['registration_url']}",
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
