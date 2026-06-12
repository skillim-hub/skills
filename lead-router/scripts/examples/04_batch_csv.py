from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

from lead_router import LeadRouterClient

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("LEAD_ROUTER_ENV", "sandbox"))
    parser.add_argument("--config", default=os.getenv("LEAD_ROUTER_CONFIG"))
    parser.add_argument("--csv", default=os.getenv("LEAD_ROUTER_CSV"))
    args = parser.parse_args()

    client = LeadRouterClient.from_json_file(args.config) if args.config else LeadRouterClient()
    if args.csv:
        rows = list(csv.DictReader(Path(args.csv).open("r", encoding="utf-8-sig")))
    else:
        rows = [
            {"phone": "0521234567", "message": "צריך מחיר בחיפה"},
            {"email": "billing@example.co.il", "message": "Need invoice"},
        ]
    output = [{"env": args.env, **client.route_lead(row).to_dict()} for row in rows]
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
