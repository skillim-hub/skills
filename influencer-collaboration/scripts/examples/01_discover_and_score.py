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
    parser = argparse.ArgumentParser(description="Discover and score sample creators.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("ICH_ENV", "sandbox"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    budget = float(os.getenv(f"ICH_{args.env.upper()}_BUDGET_ILS", "6500"))
    brief = CampaignBrief(
        business_name=os.getenv(f"ICH_{args.env.upper()}_BUSINESS_NAME", "קפה שכונתי"),
        product_or_service=os.getenv(f"ICH_{args.env.upper()}_PRODUCT", "תפריט בוקר חדש"),
        goal=CollaborationGoal.FOOT_TRAFFIC,
        target_locations=["חיפה"],
        target_segments=[MarketSegment.FOOD],
        budget_ils=budget,
        start_date=date(2026, 6, 10),
        end_date=date(2026, 6, 25),
        coupon_code="HAIFA10",
    )
    profiles = [
        InfluencerProfile("haifa_food", "דנה", Platform.INSTAGRAM, "אוכל בחיפה", 18000, 9000, 620, 80, "חיפה", 0.91),
        InfluencerProfile("central_style", "נועם", Platform.TIKTOK, "אופנה ולייף סטייל", 45000, 12000, 500, 35, "תל אביב", 0.62),
    ]
    client = InfluencerCollaborationClient()
    result = [asdict(item) for item in client.rank_profiles(profiles, brief)]
    print(json.dumps({"environment": args.env, "results": result}, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
