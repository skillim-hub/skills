from __future__ import annotations

import argparse
import json
import os

from referral_program_manager import ReferralProgramManager, create_demo_manager


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an ecommerce coupon referral scenario.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RPM_ENV", "sandbox"))
    return parser.parse_args()


def print_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    args = parse_args()
    gateway = os.getenv("RPM_GATEWAY", "manual")
    api_key_present = bool(os.getenv("RPM_GATEWAY_API_KEY"))
    manager = ReferralProgramManager()
    manager.create_program("shop-40-2026", "Shop ₪40 Coupon", "coupon", 40, "paid_order_not_returned", cooldown_days=0, minimum_order_ils=199)
    manager.add_customer("ref_1", "Amit", "amit@example.co.il", "050-1111111", True)
    manager.add_customer("new_1", "Maya", "maya@example.co.il", "052-2222222", True)
    event = manager.register_referral("shop-40-2026", "ref_1", "new_1", "checkout")
    manager.qualify_referral(event.event_id, {"order": "ORDER-1001"}, order_amount_ils=240)
    reward = manager.approve_reward(event.event_id, actor="ecommerce-owner", tax_treatment="coupon")
    payload = manager.build_reward_gateway_payload(reward.reward_id, gateway)
    print_json({
        "environment": args.env,
        "gateway": gateway,
        "api_key_present": api_key_present,
        "scenario": "ecommerce_coupon",
        "gateway_payload": payload,
    })


if __name__ == "__main__":
    main()
