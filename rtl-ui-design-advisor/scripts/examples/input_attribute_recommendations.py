from __future__ import annotations

import argparse
import json
import os

from rtl_ui_design_advisor import recommend_input_attributes

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RTL_ADVISOR_ENV", "sandbox"))
args = parser.parse_args()

fields = [
    ("text", "customerName"),
    ("email", "email"),
    ("tel", "phone"),
    ("text", "businessId"),
    ("text", "amount"),
]
payload = {
    "env": args.env,
    "recommendations": [
        {"type": field_type, "name": name, "attributes": recommend_input_attributes(field_type, name)}
        for field_type, name in fields
    ],
}
print(json.dumps(payload, ensure_ascii=False, indent=2))
