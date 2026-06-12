from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from crm_integration_agent import audit_template, write_audit_events

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CRM_ENV", "sandbox"))
parser.add_argument("--output", default=os.getenv("AUDIT_LOG", "/tmp/crm-audit.jsonl"))
args = parser.parse_args()
event = audit_template(crm_object_id=os.getenv("CRM_OBJECT_ID", "dry-run-id"), provider="hubspot")
event["environment"] = args.env
write_audit_events(Path(args.output), [event])
print(json.dumps({"written": args.output, "event": event}, ensure_ascii=False, indent=2))
