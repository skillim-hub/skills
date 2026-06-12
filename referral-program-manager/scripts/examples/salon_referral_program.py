from __future__ import annotations

import argparse
import json
import os

from referral_program_manager import ReferralProgramManager, create_demo_manager


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a salon credit referral scenario.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RPM_ENV", "sandbox"))
    return parser.parse_args()


def print_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    args = parse_args()
    gateway = os.getenv("RPM_GATEWAY", "manual")
    api_key_present = bool(os.getenv("RPM_GATEWAY_API_KEY"))
    manager = create_demo_manager()
    reward = next(iter(manager.rewards.values()))
    print_json({
        "environment": args.env,
        "gateway": gateway,
        "api_key_present": api_key_present,
        "scenario": "salon_credit",
        "reward_id": reward.reward_id,
        "amount_ils": str(reward.amount_ils),
        "status": reward.status.value,
    })


if __name__ == "__main__":
    main()
