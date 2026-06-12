from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from lead_router import LeadRouterClient

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("LEAD_ROUTER_ENV", "sandbox"))
    parser.add_argument("--config", default=os.getenv("LEAD_ROUTER_CONFIG"))
    parser.add_argument("--store", default=os.getenv("LEAD_ROUTER_STORE", ".lead-router-leads.json"))
    args = parser.parse_args()

    client = LeadRouterClient.from_json_file(args.config) if args.config else LeadRouterClient()
    lead = {
        "phone": os.getenv("LEAD_ROUTER_PHONE", "0521234567"),
        "message": os.getenv("LEAD_ROUTER_MESSAGE", "צריך הצעת מחיר להתקנה בחיפה"),
        "channel": os.getenv("LEAD_ROUTER_CHANNEL", "whatsapp"),
    }
    created = client.create_lead(lead, Path(args.store))
    routed = client.route_stored_lead(created["lead_id"], Path(args.store)).to_dict()
    print(json.dumps({"env": args.env, "created": created, "routed": routed}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
