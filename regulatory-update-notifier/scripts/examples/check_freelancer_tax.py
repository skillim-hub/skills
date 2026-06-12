#!/usr/bin/env python3
"""Scan tax-related updates for a freelancer profile."""

from __future__ import annotations

import argparse
import json
import os

from regulatory_update_notifier import RegulatoryMonitorClient, create_profile, default_sources


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RUN_ENV", "sandbox"))
    parser.add_argument("--minimum-score", type=int, default=int(os.getenv("MINIMUM_SCORE", "20")))
    args = parser.parse_args()

    profile = create_profile(
        name=os.getenv("PROFILE_NAME", "עצמאי נותן שירותים"),
        industries=["freelancer", "professional-services"],
        keywords=["חשבונית", "עוסק מורשה", "מסים"],
        locale=os.getenv("LOCALE", "he"),
        environment=args.env,
    )
    updates = RegulatoryMonitorClient(default_sources(args.env)).collect_updates(profile=profile, minimum_score=args.minimum_score)
    print(json.dumps({"profile": profile.to_dict(), "updates": [item.to_dict() for item in updates]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
