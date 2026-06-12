#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from forms_certificates_downloader import FormsCertificatesClient, PortalSource, load_registry


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("FORMS_DOWNLOADER_ENV", "sandbox"))
    parser.add_argument("--download-dir", default=os.getenv("FORMS_DOWNLOADER_DOWNLOAD_DIR", "example-downloads"))
    parser.add_argument("--query", default=os.getenv("FORMS_DOWNLOADER_QUERY"))
    parser.add_argument("--limit", type=int, default=int(os.getenv("FORMS_DOWNLOADER_LIMIT", "5")))
    parser.add_argument("--registry", default=os.getenv("FORMS_DOWNLOADER_REGISTRY"))
    return parser


def make_client(args: argparse.Namespace) -> FormsCertificatesClient:
    registry = load_registry(args.registry) if args.registry else None
    return FormsCertificatesClient(download_dir=args.download_dir, registry=registry, env=args.env)


def print_json(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
