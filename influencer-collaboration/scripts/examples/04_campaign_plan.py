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
    parser = argparse.ArgumentParser(description="Create a campaign plan.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("ICH_ENV", "sandbox"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profiles = [
        InfluencerProfile("parents_north", "ליאת", Platform.INSTAGRAM, "הורות וילדים בצפון", 31000, 14000, 900, 120, "קריות", 0.93),
        InfluencerProfile("family_deals", "אורי", Platform.FACEBOOK, "קהילות משפחה וקניות", 28000, 6000, 260, 70, "חיפה", 0.86),
        InfluencerProfile("general_il", "רוני", Platform.TIKTOK, "לייף סטייל ישראלי", 70000, 20000, 600, 50, "ישראל", 0.74),
    ]
    brief = CampaignBrief(
        business_name=os.getenv(f"ICH_{args.env.upper()}_BUSINESS_NAME", "חנות צעצועים מקומית"),
        product_or_service=os.getenv(f"ICH_{args.env.upper()}_PRODUCT", "ערכת יצירה לחופש הגדול"),
        goal=CollaborationGoal.SALES,
        target_locations=["חיפה", "קריות"],
        target_segments=[MarketSegment.PARENTING],
        budget_ils=float(os.getenv(f"ICH_{args.env.upper()}_BUDGET_ILS", "9000")),
        start_date=date(2026, 6, 15),
        end_date=date(2026, 7, 5),
        deliverables=["reel", "story"],
        coupon_code="KIDS15",
    )
    client = InfluencerCollaborationClient()
    plan = client.build_plan(profiles, brief, max_creators=2)
    print(json.dumps({"environment": args.env, "plan": plan}, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
