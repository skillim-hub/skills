#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os

from social_media_manager_client import BlackoutPeriod, PostDraft, SocialMediaManagerClient, sample_drafts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("SOCIAL_MEDIA_MANAGER_ENV", "sandbox"))
    parser.add_argument("--start-date", default=os.getenv("SOCIAL_MEDIA_MANAGER_START_DATE", "2026-06-08"))
    parser.add_argument("--business-type", default=os.getenv("SOCIAL_MEDIA_MANAGER_BUSINESS_TYPE", "עסק מקומי"))
    return parser.parse_args()


def dump(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    args = parse_args()
    caption = os.getenv("SOCIAL_MEDIA_MANAGER_CAPTION", "מבצע ב-₪99 עד 30/06/2026. פרטים מלאים באתר.")
    client = SocialMediaManagerClient()
    draft = PostDraft(platform="instagram", format="reel", media_count=1, caption=caption, contains_price=True, offer_terms="עד 30/06/2026, בכפוף לזמינות")
    valid, issues, risk_flags = client.validate_post(draft)
    dump({"environment": args.env, "scenario": "validate_hebrew_caption", "valid": valid, "issues": [issue.to_dict() for issue in issues], "risk_flags": list(risk_flags)})


if __name__ == "__main__":
    main()
