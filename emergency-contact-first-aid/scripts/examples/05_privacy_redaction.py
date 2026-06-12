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
profile_path = os.getenv("ECFA_PROFILE_PATH", "templates/emergency-profile.example.json")
profile = client.load_profile(profile_path)
dump({
    "environment": args.env,
    "public_profile": client.redact_profile(profile)
})
