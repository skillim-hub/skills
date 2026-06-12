from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from brand_reputation_monitor import BrandReputationMonitor, Mention, MonitorConfig, dump_results, load_mentions


def split_env(value: str | None) -> list[str]:
    return [item.strip() for item in (value or "").split(",") if item.strip()]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--env", choices=["sandbox", "production"], default=os.environ.get("BRM_ENV", "sandbox"))
    return p


def config_from_env() -> MonitorConfig:
    return MonitorConfig(
        brand_terms=split_env(os.environ.get("BRM_BRAND_TERMS")),
        exclude_terms=split_env(os.environ.get("BRM_EXCLUDE_TERMS")),
        require_brand_match=os.environ.get("BRM_REQUIRE_BRAND_MATCH", "").lower() in {"1", "true", "yes"},
    )

args = parser().parse_args()
monitor = BrandReputationMonitor(config_from_env())
mention = Mention(
    text="משרד הבריאות צריך לבדוק את המקום הזה, העוגה הייתה מקולקלת והילד הקיא",
    source="tiktok",
    engagement=88,
    url="https://example.test/video/123",
)
result = monitor.analyze_mention(mention)
print(json.dumps({"env": args.env, "result": result.to_dict()}, ensure_ascii=False, indent=2))
