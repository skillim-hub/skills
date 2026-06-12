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
texts = [
    "אמאלה איזה טעים",
    'איזה שירות "מדהים", מחכה כבר יומיים',
    "לא רע בכלל",
    "לא טוב בכלל",
]
payload = []
for text in texts:
    result = monitor.analyze_mention(Mention(text=text, source="manual"))
    payload.append({"text": text, "sentiment": result.sentiment.label, "score": result.sentiment.score})
print(json.dumps({"env": args.env, "items": payload}, ensure_ascii=False, indent=2))
