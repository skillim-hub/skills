from __future__ import annotations

import argparse
import json
import os
from lead_router import LeadRouterClient

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("LEAD_ROUTER_ENV", "sandbox"))
    p.add_argument("--config", default=os.getenv("LEAD_ROUTER_CONFIG"))
    return p

def client_from_args(args: argparse.Namespace) -> LeadRouterClient:
    return LeadRouterClient.from_json_file(args.config) if args.config else LeadRouterClient()

def print_json(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))

def main() -> None:
    args = parser().parse_args()
    lead = {
        "name": os.getenv("LEAD_ROUTER_NAME", "سامي"),
        "phone": os.getenv("LEAD_ROUTER_PHONE", "0523334444"),
        "city": os.getenv("LEAD_ROUTER_CITY", "נצרת"),
        "message": os.getenv("LEAD_ROUTER_MESSAGE", "مرحبا، أريد عرض سعر للخدمة"),
        "channel": os.getenv("LEAD_ROUTER_CHANNEL", "meta_lead_ad"),
    }
    result = client_from_args(args).route_lead(lead).to_dict()
    result["env"] = args.env
    print_json(result)

if __name__ == "__main__":
    main()
