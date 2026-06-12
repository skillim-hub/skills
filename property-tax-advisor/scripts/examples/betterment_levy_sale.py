from __future__ import annotations

import argparse
import json
import os

from property_tax_advisor import estimate_betterment_levy


def main() -> None:
    parser = argparse.ArgumentParser(description="Betterment levy sale scenario")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PTA_ENV", "sandbox"))
    args = parser.parse_args()
    result = estimate_betterment_levy(
        planning_uplift=float(os.getenv("PTA_PLANNING_UPLIFT", "300000")),
        ownership_share=float(os.getenv("PTA_OWNERSHIP_SHARE", "1")),
        exemption=os.getenv("PTA_EXEMPTION", "false").lower() in {"1", "true", "yes"},
    )
    print(json.dumps({"environment": args.env, "result": result.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
