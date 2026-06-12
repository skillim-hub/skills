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
    dependents = int(os.getenv("ICA_DEPENDENTS", "2"))
    return {
        "env": env,
        "profile": {"segment": "freelancer", "dependents": dependents},
        "policies": [
            {
                "policy_id": "life-stepped",
                "policy_type": "life",
                "premium_monthly_nis": 95,
                "coverages": {"death_benefit": {"covered": True, "limit_nis": 1000000}, "beneficiaries": True},
                "first_year_discount": True,
            },
            {
                "policy_id": "life-fixed",
                "policy_type": "life",
                "premium_monthly_nis": 130,
                "coverages": {"death_benefit": {"covered": True, "limit_nis": 750000}, "beneficiaries": True},
            },
            {
                "policy_id": "life-mortgage",
                "policy_type": "life",
                "premium_monthly_nis": 70,
                "coverages": {"mortgage_life": {"covered": True, "limit_nis": 600000}},
                "assigned_to_bank": True,
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
