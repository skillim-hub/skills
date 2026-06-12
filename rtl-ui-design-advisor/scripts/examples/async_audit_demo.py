from __future__ import annotations

import argparse
import asyncio
import json
import os

from rtl_ui_design_advisor import RtlAuditClient

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RTL_ADVISOR_ENV", "sandbox"))
args = parser.parse_args()

async def main() -> None:
    css = os.getenv("RTL_ADVISOR_SAMPLE_CSS", ".drawer { left: 0; transform: translateX(100%); }")
    record = await RtlAuditClient().create_audit_async("css", css, env=args.env, save=False)
    print(json.dumps(record.to_dict(), ensure_ascii=False, indent=2))

asyncio.run(main())
