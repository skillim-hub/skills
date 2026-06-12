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
    return {
        "env": env,
        "profile": {"review": "duplicate-coverages"},
        "policies": [
            {"policy_id": "health", "policy_type": "health", "coverages": {"serious_illness": True, "private_surgery_israel": True}},
            {
                "policy_id": "life",
                "policy_type": "life",
                "coverages": {
                    "serious_illness": True,
                    "death_benefit": {"covered": True, "limit_nis": 1000000},
                    "beneficiaries": True,
                },
            },
        ],
    }


def main() -> None:
    args = parse_args()
    payload = build_payload(args.env)
    analyzer = InsuranceCoverageAnalyzer(locale=args.locale)
    normalized = analyzer.normalize(payload["policies"])
    print(json.dumps({"env": args.env, "duplicates": detect_duplicates(normalized)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
