from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from datetime import date


from influencer_collaboration_client import CampaignMetric, InfluencerCollaborationClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize monthly campaign performance.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("ICH_ENV", "sandbox"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    multiplier = float(os.getenv(f"ICH_{args.env.upper()}_REVENUE_MULTIPLIER", "1"))
    metrics = [
        CampaignMetric("haifa_food", 2400, 38000, 16000, 820, 95, 34, 5100 * multiplier, date(2026, 6, 30)),
        CampaignMetric("parents_north", 3600, 52000, 21000, 760, 120, 41, 6800 * multiplier, date(2026, 6, 30)),
    ]
    client = InfluencerCollaborationClient()
    summary = client.summarize_metrics(metrics)
    print(json.dumps({"environment": args.env, "summary": asdict(summary)}, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
