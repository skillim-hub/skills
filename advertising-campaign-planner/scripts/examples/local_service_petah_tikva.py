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
    city = os.environ.get("AD_PLANNER_DEFAULT_CITY", 'פתח תקווה')
    budget = float(os.environ.get("AD_PLANNER_DEFAULT_BUDGET", '6000'))
    request = CampaignRequest(
        business='רואה חשבון עצמאי',
        goal='leads',
        monthly_budget=budget,
        languages=['he', 'ru'],
        cities=[city] + ['רמת גן'],
        sector='professional_services',
        audience='עצמאים ובעלי עסקים קטנים',
        offer='שיחת ייעוץ של 20 דקות ללא התחייבות',
        avg_order_value=2400,
        gross_margin=0.7,
        regulated_flags=['tax_advice'],
        uses_remarketing=True,
        uses_direct_messages=False,
        service_languages=['he', 'ru'],
        environment=args.env,
    )
    plan = CampaignPlanner().plan(request)
    print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
