from __future__ import annotations

import argparse
import json
import os

from rtl_ui_design_advisor import RtlAuditClient

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RTL_ADVISOR_ENV", "sandbox"))
args = parser.parse_args()

css = os.getenv("RTL_ADVISOR_SAMPLE_CSS", ".invoice { padding-left: 16px; margin-right: 8px; text-align: right; right: 0; }")
client = RtlAuditClient()
payload = {
    "env": args.env,
    "before": css,
    "after": client.fix_css_logical(css),
    "audit": client.audit_css(css).to_dict(),
}
print(json.dumps(payload, ensure_ascii=False, indent=2))
