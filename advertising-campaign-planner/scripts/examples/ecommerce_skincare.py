from __future__ import annotations

import argparse
import json
import os

from advertising_campaign_planner import CampaignPlanner, CampaignRequest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.environ.get("AD_PLANNER_ENV", "sandbox"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    city = os.environ.get("AD_PLANNER_DEFAULT_CITY", 'Israel nationwide')
    budget = float(os.environ.get("AD_PLANNER_DEFAULT_BUDGET", '12000'))
    request = CampaignRequest(
        business='Online skincare store',
        goal='sales',
        monthly_budget=budget,
        languages=['he', 'ar'],
        cities=[city] + [],
        sector='cosmetics ecommerce',
        audience='Israeli consumers comparing skincare products',
        offer='Bundle discount valid 03/06/2026 to 17/06/2026',
        avg_order_value=220,
        gross_margin=0.52,
        regulated_flags=['cosmetics'],
        uses_remarketing=True,
        uses_direct_messages=False,
        service_languages=['he', 'ar'],
        environment=args.env,
    )
    plan = CampaignPlanner().plan(request)
    print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
