from __future__ import annotations

import argparse
import json
import os

from property_tax_advisor import compare_home_office_scenarios


def main() -> None:
    parser = argparse.ArgumentParser(description="Freelancer home-office classification scenario")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PTA_ENV", "sandbox"))
    args = parser.parse_args()
    result = compare_home_office_scenarios(
        municipality=os.getenv("PTA_MUNICIPALITY", "jerusalem"),
        zone=os.getenv("PTA_ZONE", "A"),
        total_area_sqm=float(os.getenv("PTA_TOTAL_AREA_SQM", "72")),
        business_area_sqm=float(os.getenv("PTA_BUSINESS_AREA_SQM", "10")),
        business_usage=os.getenv("PTA_BUSINESS_USAGE", "office"),
    )
    print(json.dumps({"environment": args.env, "result": result.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
