from __future__ import annotations

import argparse
import json
import os

from rtl_ui_design_advisor import RtlAuditClient

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RTL_ADVISOR_ENV", "sandbox"))
args = parser.parse_args()

classes = os.getenv("RTL_ADVISOR_SAMPLE_CLASSES", "flex ml-4 pl-6 text-left left-0 space-x-2")
record = RtlAuditClient().create_audit("tailwind", classes, env=args.env, save=False)
print(json.dumps(record.to_dict(), ensure_ascii=False, indent=2))
