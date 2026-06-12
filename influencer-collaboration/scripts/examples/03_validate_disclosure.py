from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from datetime import date


from influencer_collaboration_client import InfluencerCollaborationClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Hebrew commercial disclosure.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("ICH_ENV", "sandbox"))
    parser.add_argument("--text", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    text = args.text or os.getenv(
        f"ICH_{args.env.upper()}_CAPTION",
        "פרסומת בשיתוף סטודיו מקומי. קוד הטבה: LOCAL10",
    )
    client = InfluencerCollaborationClient()
    valid, issues = client.validate_disclosure(text)
    print(json.dumps({"environment": args.env, "valid": valid, "issues": issues}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
