from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from datetime import date


from influencer_collaboration_client import (
    CampaignBrief,
    CollaborationGoal,
    InfluencerCollaborationClient,
    InfluencerProfile,
    MarketSegment,
    Platform,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Hebrew outreach.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("ICH_ENV", "sandbox"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    business = os.getenv(f"ICH_{args.env.upper()}_BUSINESS_NAME", "סטודיו לפילאטיס")
    profile = InfluencerProfile("pilates_tlv", "מאיה", Platform.INSTAGRAM, "כושר ופילאטיס", 22000, 10000, 710, 94, "תל אביב", 0.88)
    brief = CampaignBrief(
        business_name=business,
        product_or_service=os.getenv(f"ICH_{args.env.upper()}_PRODUCT", "חבילת היכרות ללקוחות חדשים"),
        goal=CollaborationGoal.LEADS,
        target_locations=["תל אביב", "רמת גן"],
        target_segments=[MarketSegment.FITNESS],
        budget_ils=float(os.getenv(f"ICH_{args.env.upper()}_BUDGET_ILS", "5000")),
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 15),
        deliverables=["reel", "story", "story"],
    )
    client = InfluencerCollaborationClient()
    message = client.generate_outreach(profile, brief, tone=os.getenv(f"ICH_{args.env.upper()}_TONE", "warm"))
    print(json.dumps({"environment": args.env, "message": asdict(message)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
