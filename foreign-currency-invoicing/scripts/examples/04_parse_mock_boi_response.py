from __future__ import annotations

import argparse
import json
import os

from foreign_currency_invoicing_client import parse_boi_rate_response

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("FCI_ENV", "sandbox"))
args = parser.parse_args()

default_payload = "TIME_PERIOD,OBS_VALUE,SERIES_CODE,BASE_CURRENCY,COUNTER_CURRENCY\n2026-06-02,3.7000,RER_USD_ILS,USD,ILS\n"
payload = os.getenv("FCI_BOI_PAYLOAD", default_payload)
rate = parse_boi_rate_response(payload, os.getenv("FCI_CURRENCY", "USD"))
print(json.dumps({"env": args.env, "rate": rate.to_dict()}, ensure_ascii=False, indent=2))
