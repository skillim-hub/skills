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
    event.update({
        "event_name": "סדנת צילום מוצרים בסמארטפון",
        "format": "workshop",
        "audience": "בעלי חנויות אונליין קטנות",
        "date": os.getenv("EWP_WORKSHOP_DATE", "15-07-2026"),
        "time": os.getenv("EWP_WORKSHOP_TIME", "10:00"),
        "duration_minutes": 180,
        "price_nis": 290,
        "city": os.getenv("EWP_CITY", "חיפה"),
        "capacity": 18,
        "goal": "sales",
        "consent_status": "unknown",
    })
    plan = client.plan(event)
    print(json.dumps(plan.to_dict()["copy"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
