from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Mapping

from sales_chatbot import CustomerContext, SalesChatbotClient, sample_catalog, validate_catalog_data


def common_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.environ.get("SALES_CHATBOT_ENV", "sandbox"))
    parser.add_argument("--catalog", default=os.environ.get("SALES_CHATBOT_CATALOG"))
    parser.add_argument("--context", default=os.environ.get("SALES_CHATBOT_CONTEXT"))
    return parser


def build_client(args: argparse.Namespace) -> SalesChatbotClient:
    return SalesChatbotClient.from_json(args.catalog) if args.catalog else SalesChatbotClient(sample_catalog())


def _load_context(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def context_from_args(args: argparse.Namespace, defaults: Mapping[str, Any]) -> CustomerContext:
    data = dict(defaults)
    data.update(_load_context(args.context))
    data.setdefault("channel", os.environ.get("SALES_CHATBOT_CHANNEL", "whatsapp"))
    data["environment"] = args.env
    return CustomerContext.from_mapping(data)


def emit(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
