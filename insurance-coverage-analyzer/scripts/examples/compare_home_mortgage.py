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
    mortgage_required = float(os.getenv("ICA_MORTGAGE_STRUCTURE_NIS", "1250000"))
    return {
        "env": env,
        "profile": {"mortgage": True, "domestic_worker": os.getenv("ICA_DOMESTIC_WORKER", "true").lower() == "true"},
        "policies": [
            {
                "policy_id": "home-current",
                "policy_type": "home",
                "premium_monthly_nis": 120,
                "coverages": {
                    "structure": {"covered": True, "limit_nis": mortgage_required},
                    "contents": {"covered": True, "limit_nis": 250000},
                    "water_damage": {"covered": True, "deductible_nis": 750},
                    "earthquake": {"covered": True, "deductible_percent": 10},
                    "third_party_liability": {"covered": True, "limit_nis": 1000000},
                },
            }
        ],
    }


def main() -> None:
    args = parse_args()
    payload = build_payload(args.env)
    result = InsuranceCoverageAnalyzer(locale=args.locale).compare(payload["policies"], profile=payload["profile"])
    print(json.dumps({"env": args.env, "result": result.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
