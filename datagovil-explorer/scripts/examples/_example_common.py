from __future__ import annotations

import argparse
import json
from typing import Any

from datagovil_explorer import DatagovClient, RequestConfig, base_url_for_env


def parser(description: str) -> argparse.ArgumentParser:
    item = argparse.ArgumentParser(description=description)
    item.add_argument("--env", choices=["sandbox", "production"], default="production")
    item.add_argument("--base-url", default=None)
    item.add_argument("--timeout", type=float, default=30.0)
    return item


def client_from_args(args: argparse.Namespace) -> DatagovClient:
    base_url = (args.base_url or base_url_for_env(args.env)).rstrip("/")
    return DatagovClient(RequestConfig(base_url=base_url, timeout=args.timeout))


def print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))
