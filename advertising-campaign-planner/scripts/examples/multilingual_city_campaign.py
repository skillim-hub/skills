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
    city = os.environ.get("AD_PLANNER_DEFAULT_CITY", 'Nazareth')
    budget = float(os.environ.get("AD_PLANNER_DEFAULT_BUDGET", '4500'))
    request = CampaignRequest(
        business='Home renovation contractor',
        goal='calls',
        monthly_budget=budget,
        languages=['he', 'ar'],
        cities=[city] + ['Afula', 'Haifa'],
        sector='home_services',
        audience='Homeowners planning renovation work',
        offer='Site visit and written estimate',
        avg_order_value=12000,
        gross_margin=0.38,
        regulated_flags=[],
        uses_remarketing=False,
        uses_direct_messages=False,
        service_languages=['he', 'ar'],
        environment=args.env,
    )
    plan = CampaignPlanner().plan(request)
    print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
