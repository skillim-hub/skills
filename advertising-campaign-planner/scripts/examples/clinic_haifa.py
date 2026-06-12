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
    city = os.environ.get("AD_PLANNER_DEFAULT_CITY", 'Haifa')
    budget = float(os.environ.get("AD_PLANNER_DEFAULT_BUDGET", '15000'))
    request = CampaignRequest(
        business='Family dental clinic',
        goal='bookings',
        monthly_budget=budget,
        languages=['he', 'ar'],
        cities=[city] + ['Krayot'],
        sector='health',
        audience='Families comparing local dental care',
        offer='Initial consultation with clear treatment plan',
        avg_order_value=1800,
        gross_margin=0.62,
        regulated_flags=['health'],
        uses_remarketing=False,
        uses_direct_messages=False,
        service_languages=['he', 'ar'],
        environment=args.env,
    )
    plan = CampaignPlanner().plan(request)
    print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
