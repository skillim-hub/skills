from __future__ import annotations

import argparse
import json
import os
from typing import Any

import followup_review_solicitor as client


def parser(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("FOLLOWUP_ENV", "sandbox"))
    return p


def env_value(name: str, default: str, *, mode: str) -> str:
    prefix = "PROD_" if mode == "production" else "SANDBOX_"
    return os.getenv(prefix + name, os.getenv(name, default))


def print_json(value: Any) -> None:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    print(json.dumps(value, ensure_ascii=False, indent=2))
