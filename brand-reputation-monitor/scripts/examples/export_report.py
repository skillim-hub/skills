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
out_dir = Path(os.environ.get("BRM_OUTPUT_DIR", str(Path(__file__).resolve().parent / "output")))
out_dir.mkdir(parents=True, exist_ok=True)
monitor = BrandReputationMonitor(config_from_env())
mentions = [
    Mention(text="הקופון לא עובד וזה מבאס", source="tiktok", engagement=15),
    Mention(text="המחיר 120 ₪ היה שווה כל שקל", source="review", engagement=2),
]
results = monitor.analyze_many(mentions)
json_path = out_dir / "analyzed.json"
report_path = out_dir / "report.md"
dump_results(results, json_path, "json")
report_path.write_text(monitor.generate_markdown_report(results), encoding="utf-8")
print(json.dumps({"env": args.env, "wrote": [str(json_path), str(report_path)]}, ensure_ascii=False, indent=2))
