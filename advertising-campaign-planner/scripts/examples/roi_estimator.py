from __future__ import annotations

import argparse
import json
import os

from advertising_campaign_planner import CampaignPlanner


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.environ.get("AD_PLANNER_ENV", "sandbox"))
    args = parser.parse_args()
    estimate = CampaignPlanner().estimate_roi(
        spend=float(os.environ.get("AD_PLANNER_ROI_SPEND", "4500")),
        clicks=int(os.environ.get("AD_PLANNER_ROI_CLICKS", "1800")),
        conversions=int(os.environ.get("AD_PLANNER_ROI_CONVERSIONS", "54")),
        avg_order_value=float(os.environ.get("AD_PLANNER_ROI_AOV", "350")),
        gross_margin=float(os.environ.get("AD_PLANNER_ROI_MARGIN", "0.48")),
    )
    payload = estimate.to_dict()
    payload["environment"] = args.env
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
