from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict

from insurance_coverage_analyzer import InsuranceCoverageAnalyzer, detect_duplicates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("ICA_ENV", "sandbox"))
    parser.add_argument("--locale", default=os.getenv("ICA_LOCALE", "en-IL"))
    return parser.parse_args()



def build_payload(env: str) -> Dict[str, Any]:
    current = float(os.getenv("ICA_CURRENT_PREMIUM", "120"))
    renewal = float(os.getenv("ICA_RENEWAL_PREMIUM", "150"))
    return {
        "env": env,
        "profile": {"renewal_review": True},
        "policies": [
            {
                "policy_id": "home-current",
                "policy_type": "home",
                "premium_monthly_nis": current,
                "coverages": {
                    "structure": True,
                    "contents": True,
                    "water_damage": True,
                    "earthquake": True,
                    "third_party_liability": True,
                },
            },
            {
                "policy_id": "home-renewal",
                "policy_type": "home",
                "premium_monthly_nis": renewal,
                "coverages": {
                    "structure": True,
                    "contents": True,
                    "water_damage": True,
                    "earthquake": True,
                    "third_party_liability": True,
                },
            },
        ],
    }


def main() -> None:
    args = parse_args()
    payload = build_payload(args.env)
    result = InsuranceCoverageAnalyzer(locale=args.locale).compare(payload["policies"], profile=payload["profile"])
    print(json.dumps({"env": args.env, "result": result.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
