#!/usr/bin/env python3
"""Monitor ecommerce and consumer protection updates."""

from __future__ import annotations

import argparse
import json
import os

from regulatory_update_notifier import RegulatoryMonitorClient, create_profile, default_sources


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RUN_ENV", "sandbox"))
    parser.add_argument("--keyword", action="append", default=None)
    args = parser.parse_args()

    keywords = args.keyword or os.getenv("KEYWORDS", "ביטול עסקה,cancellation").split(",")
    profile = create_profile(
        name=os.getenv("PROFILE_NAME", "חנות מקוונת"),
        industries=["ecommerce", "retail", "consumers"],
        keywords=keywords,
        locale=os.getenv("LOCALE", "he"),
        environment=args.env,
    )
    updates = RegulatoryMonitorClient(default_sources(args.env)).collect_updates(profile=profile, minimum_score=20)
    print(json.dumps({"profile": profile.to_dict(), "updates": [item.to_dict() for item in updates]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
