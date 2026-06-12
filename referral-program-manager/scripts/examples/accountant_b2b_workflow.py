from __future__ import annotations

import argparse
import json
import os

from referral_program_manager import ReferralProgramManager, create_demo_manager


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a B2B accountant or consultant referral scenario.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RPM_ENV", "sandbox"))
    return parser.parse_args()


def print_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    args = parse_args()
    gateway = os.getenv("RPM_GATEWAY", "manual")
    api_key_present = bool(os.getenv("RPM_GATEWAY_API_KEY"))
    manager = ReferralProgramManager()
    manager.create_program("b2b-250-2026", "B2B referral credit", "credit", 250, "paid_first_invoice", cooldown_days=0, minimum_order_ils=1500)
    manager.add_customer("biz_ref", "Levi Consulting", "office@levi.co.il", "050-3333333", vat_or_id="000000018")
    manager.add_customer("biz_new", "Cohen Retail", "hello@cohen.co.il", "052-4444444", vat_or_id="000000026")
    event = manager.register_referral("b2b-250-2026", "biz_ref", "biz_new", "crm")
    manager.qualify_referral(event.event_id, {"invoice": "INV-2026-0100", "agreement": "signed"}, order_amount_ils=2500)
    reward = manager.approve_reward(event.event_id, actor="partner", tax_treatment="b2b_marketing_credit")
    print_json({
        "environment": args.env,
        "gateway": gateway,
        "api_key_present": api_key_present,
        "scenario": "b2b_credit",
        "reward_id": reward.reward_id,
        "amount_ils": str(reward.amount_ils),
    })


if __name__ == "__main__":
    main()
