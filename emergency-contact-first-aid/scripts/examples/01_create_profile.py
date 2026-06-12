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
profile = make_starter_profile(
    os.getenv("ECFA_PROFILE_NAME", "North Workshop"),
    os.getenv("ECFA_ADDRESS", "HaTaasiya 4, entrance A"),
    os.getenv("ECFA_LOCALITY", "Haifa"),
    os.getenv("ECFA_CONTACT_NAME", "Noa Amir"),
    os.getenv("ECFA_CONTACT_PHONE", "050-111-2222"),
    args.env,
)
dump(profile.to_mapping())
