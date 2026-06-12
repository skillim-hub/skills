from __future__ import annotations

import argparse
import json
import os

from property_tax_advisor import build_appeal_packet


def main() -> None:
    parser = argparse.ArgumentParser(description="Small-business Arnona classification appeal scenario")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PTA_ENV", "sandbox"))
    args = parser.parse_args()
    issues = tuple(os.getenv("PTA_APPEAL_ISSUES", "classification,area").split(","))
    result = build_appeal_packet(
        municipality=os.getenv("PTA_MUNICIPALITY", "haifa"),
        property_number=os.getenv("PTA_PROPERTY_NUMBER", "123456"),
        issues=issues,
        facts=os.getenv("PTA_FACTS", "Workshop was billed as commerce and includes storage area."),
    )
    print(json.dumps({"environment": args.env, "result": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
