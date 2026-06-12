from __future__ import annotations

import argparse
import json
import os

from property_tax_advisor import calculate_arnona


def main() -> None:
    parser = argparse.ArgumentParser(description="Consumer Arnona discount scenario")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PTA_ENV", "sandbox"))
    args = parser.parse_args()
    result = calculate_arnona({
        "municipality": os.getenv("PTA_MUNICIPALITY", "tel-aviv"),
        "area_sqm": float(os.getenv("PTA_AREA_SQM", "80")),
        "zone": os.getenv("PTA_ZONE", "A"),
        "usage": os.getenv("PTA_USAGE", "residential"),
        "months": int(os.getenv("PTA_MONTHS", "2")),
        "discount": os.getenv("PTA_DISCOUNT", "senior"),
    })
    print(json.dumps({"environment": args.env, "result": result.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
