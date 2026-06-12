from __future__ import annotations

import argparse
import json
import os

from emergency_contact_first_aid import EmergencyInfoClient, make_starter_profile


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("ECFA_ENV", "sandbox"))
    return result


def dump(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))

args = parser().parse_args()
client = EmergencyInfoClient()
scenario = os.getenv("ECFA_SCENARIO", "choking")
age_group = os.getenv("ECFA_AGE_GROUP", "adult")
dump({
    "environment": args.env,
    "triage": client.triage(scenario, age_group=age_group).to_mapping()
})
