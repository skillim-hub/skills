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
    household = os.getenv("ICA_HOUSEHOLD", "family")
    return {
        "env": env,
        "profile": {"segment": household, "supplementary_health_plan": os.getenv("ICA_SHABAN", "unknown")},
        "policies": [
            {
                "policy_id": "health-family-current",
                "policy_type": "health",
                "premium_monthly_nis": 420,
                "coverages": {
                    "private_surgery_israel": {"covered": True, "limit_nis": 2000000, "deductible_nis": 0},
                    "drugs_outside_basket": {"covered": True, "limit_nis": 3000000},
                    "transplants": {"covered": True, "limit_nis": 5000000},
                    "ambulatory": {"covered": True, "limit_nis": 12000},
                },
                "waiting_period_days": 90,
            },
            {
                "policy_id": "health-family-quote",
                "policy_type": "health",
                "premium_monthly_nis": 360,
                "coverages": {
                    "private_surgery_israel": {"covered": True, "limit_nis": 1500000, "deductible_nis": 500},
                    "drugs_outside_basket": {"covered": True, "limit_nis": 1500000},
                    "ambulatory": {"covered": True, "limit_nis": 8000},
                },
                "waiting_period_days": 120,
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
