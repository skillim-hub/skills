from __future__ import annotations

import argparse
import json
import os

from referral_program_manager import ReferralProgramManager, create_demo_manager


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a freelancer future-invoice credit scenario.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RPM_ENV", "sandbox"))
    return parser.parse_args()


def print_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    args = parse_args()
    gateway = os.getenv("RPM_GATEWAY", "manual")
    api_key_present = bool(os.getenv("RPM_GATEWAY_API_KEY"))
    manager = ReferralProgramManager()
    manager.create_program("design-150-2026", "Design client referral", "credit", 150, "paid_deposit", cooldown_days=0)
    manager.add_customer("client_a", "Yael", "yael@example.co.il", "050-5555555", True)
    manager.add_customer("client_b", "Tamar", "tamar@example.co.il", "052-6666666", True)
    event = manager.register_referral("design-150-2026", "client_a", "client_b", "proposal_form")
    manager.qualify_referral(event.event_id, {"paid_deposit": "DEP-77"})
    reward = manager.approve_reward(event.event_id, actor="freelancer", tax_treatment="future_invoice_credit")
    print_json({
        "environment": args.env,
        "gateway": gateway,
        "api_key_present": api_key_present,
        "scenario": "freelancer_credit",
        "recipient_customer_id": reward.recipient_customer_id,
        "amount_ils": str(reward.amount_ils),
    })


if __name__ == "__main__":
    main()
