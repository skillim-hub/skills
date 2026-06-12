from __future__ import annotations

import argparse
import json
import os

from property_tax_advisor import assess_mas_rechush


def main() -> None:
    parser = argparse.ArgumentParser(description="Mas Rechush compensation routing scenario")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PTA_ENV", "sandbox"))
    args = parser.parse_args()
    result = assess_mas_rechush(
        property_kind=os.getenv("PTA_PROPERTY_KIND", "apartment"),
        damage_type=os.getenv("PTA_DAMAGE_TYPE", "war_direct"),
        incident_date=os.getenv("PTA_INCIDENT_DATE", "15/03/2026"),
    )
    print(json.dumps({"environment": args.env, "result": result.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
