from __future__ import annotations

import argparse
import json
import os

from rtl_ui_design_advisor import RtlAuditClient

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RTL_ADVISOR_ENV", "sandbox"))
args = parser.parse_args()

sample = os.getenv("RTL_ADVISOR_SAMPLE_HTML", """
<html lang="he" dir="rtl">
  <form>
    <input type="text" name="customerName">
    <input type="tel" name="phone">
  </form>
</html>
""")

record = RtlAuditClient().create_audit("html", sample, env=args.env, save=False)
print(json.dumps(record.to_dict(), ensure_ascii=False, indent=2))
