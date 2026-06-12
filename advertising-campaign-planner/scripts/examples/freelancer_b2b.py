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
    city = os.environ.get("AD_PLANNER_DEFAULT_CITY", 'Tel Aviv')
    budget = float(os.environ.get("AD_PLANNER_DEFAULT_BUDGET", '5000'))
    request = CampaignRequest(
        business='Freelance product designer',
        goal='leads',
        monthly_budget=budget,
        languages=['he', 'en'],
        cities=[city] + ['Herzliya'],
        sector='professional_services',
        audience='Startup founders and product managers',
        offer='UX audit for one product flow',
        avg_order_value=9000,
        gross_margin=0.75,
        regulated_flags=[],
        uses_remarketing=False,
        uses_direct_messages=False,
        service_languages=['he', 'en'],
        environment=args.env,
    )
    plan = CampaignPlanner().plan(request)
    print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
