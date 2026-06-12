from __future__ import annotations

import argparse
import json
import os

from referral_program_manager import ReferralProgramManager, create_demo_manager


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a fraud-review scenario.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RPM_ENV", "sandbox"))
    return parser.parse_args()


def print_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    args = parse_args()
    gateway = os.getenv("RPM_GATEWAY", "manual")
    api_key_present = bool(os.getenv("RPM_GATEWAY_API_KEY"))
    manager = ReferralProgramManager()
    manager.create_program("clinic-75-2026", "Clinic referral", "credit", 75, "paid_visit", cooldown_days=0)
    manager.add_customer("c1", "Referrer", "ref@example.co.il", "050-7777777", metadata={"card_token": "tok_same"})
    manager.add_customer("c2", "Friend", "friend@example.co.il", "052-8888888", metadata={"card_token": "tok_same"})
    event = manager.register_referral("clinic-75-2026", "c1", "c2", "frontdesk")
    print_json({
        "environment": args.env,
        "gateway": gateway,
        "api_key_present": api_key_present,
        "scenario": "fraud_review",
        "event_id": event.event_id,
        "status": event.status.value,
        "fraud_score": event.fraud_score,
        "review_reason": event.review_reason,
    })


if __name__ == "__main__":
    main()
