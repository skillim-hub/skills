from __future__ import annotations

import argparse
import json
import os

from rtl_ui_design_advisor import RtlAuditClient

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RTL_ADVISOR_ENV", "sandbox"))
args = parser.parse_args()

payload = {
    "env": args.env,
    "locale": os.getenv("RTL_ADVISOR_LOCALE", "he-IL"),
    "items": RtlAuditClient().production_checklist(),
}
print(json.dumps(payload, ensure_ascii=False, indent=2))
