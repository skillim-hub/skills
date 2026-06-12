from __future__ import annotations

import argparse
import json
import os
from decimal import Decimal

from hebrew_copywriter import Channel, CopyBrief, HebrewCopywriterClient, Register


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("HEBREW_COPYWRITER_ENV", "sandbox"))
    return p


def emit(env: str, result: dict) -> None:
    payload = {"env": env, "result": result}
    print(json.dumps(payload, ensure_ascii=False, indent=2))

args = parser().parse_args()
brief = CopyBrief(
    business_name=os.getenv("HEBREW_COPYWRITER_BUSINESS_NAME", "ילקוטי העיר"),
    business_type=os.getenv("HEBREW_COPYWRITER_BUSINESS_TYPE", "חנות מקוונת"),
    offer=os.getenv("HEBREW_COPYWRITER_OFFER", "ילקוט 28 ליטר עם רצועות מרופדות"),
    audience=os.getenv("HEBREW_COPYWRITER_AUDIENCE", "הורים לילדי בית ספר"),
    channel=Channel.PRODUCT_PAGE,
    price=Decimal(os.getenv("HEBREW_COPYWRITER_PRICE", "179")),
    include_vat=True,
    proof_points=["תא למחשב", "גב מרופד", "משלוח עד 3 ימי עסקים"],
)
emit(args.env, HebrewCopywriterClient().generate_copy(brief))
