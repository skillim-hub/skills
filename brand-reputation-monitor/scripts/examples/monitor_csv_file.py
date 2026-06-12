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
input_path = Path(os.environ.get("BRM_INPUT_PATH", str(Path(__file__).resolve().parent / "sample_mentions.csv")))
if not input_path.exists():
    input_path.write_text(
        "date,source,text,engagement\n"
        "24/06/2026,facebook,שירות מצוין,3\n"
        "24/06/2026,facebook,\"הטלפון שלי 050-1234567, לא קיבלתי קבלה\",6\n",
        encoding="utf-8",
    )
monitor = BrandReputationMonitor(config_from_env())
mentions = load_mentions(input_path)
results = monitor.analyze_many(mentions)
print(json.dumps({"env": args.env, "input": str(input_path), "items": [r.to_dict() for r in results]}, ensure_ascii=False, indent=2))
