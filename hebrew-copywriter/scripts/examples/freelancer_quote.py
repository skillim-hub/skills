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
    business_name=os.getenv("HEBREW_COPYWRITER_BUSINESS_NAME", "סטודיו מצגות"),
    business_type=os.getenv("HEBREW_COPYWRITER_BUSINESS_TYPE", "עיצוב מצגות"),
    offer=os.getenv("HEBREW_COPYWRITER_OFFER", "עיצוב מצגת משקיעים"),
    audience=os.getenv("HEBREW_COPYWRITER_AUDIENCE", "מנהלי שיווק ויזמים"),
    channel=Channel.QUOTE_FOLLOWUP,
    register=Register.PROFESSIONAL,
    price=Decimal(os.getenv("HEBREW_COPYWRITER_PRICE", "3800")),
    include_vat=False,
    proof_points=["עד 20 שקפים", "סבב תיקונים אחד"],
)
emit(args.env, HebrewCopywriterClient().generate_copy(brief))
