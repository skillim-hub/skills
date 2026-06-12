"""Shared utilities for runnable examples."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import invoice_aging_collection_client as client_mod


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--env",
        choices=("sandbox", "production"),
        default=os.getenv("INVOICE_AGING_ENV", "sandbox"),
        help="Execution environment. Production only changes labels; examples stay dry-run.",
    )
    parser.add_argument(
        "--ledger",
        default=os.getenv("INVOICE_AGING_LEDGER", ""),
        help="Optional ledger JSON path. Defaults to built-in sample data.",
    )
    parser.add_argument(
        "--as-of",
        default=os.getenv("INVOICE_AGING_AS_OF", "15/04/2026"),
        help="As-of date, DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD.",
    )
    parser.add_argument(
        "--invoice-id",
        default=os.getenv("INVOICE_AGING_INVOICE_ID", "INV-100"),
        help="Invoice ID for single-invoice examples.",
    )
    parser.add_argument(
        "--client-id",
        default=os.getenv("INVOICE_AGING_CLIENT_ID", "c-100"),
        help="Client ID for client-level examples.",
    )
    return parser


def load_ledger(path: str) -> dict[str, Any]:
    if path:
        return client_mod.load_ledger(Path(path))
    return client_mod.sample_ledger()


def print_json(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
