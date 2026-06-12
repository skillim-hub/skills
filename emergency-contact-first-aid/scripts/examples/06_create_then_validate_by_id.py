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
store_dir = os.getenv("ECFA_STORE_DIR", ".ecfa-example-store")
create_response = client.create_profile(
    os.getenv("ECFA_PROFILE_NAME", "Example Site"),
    os.getenv("ECFA_ADDRESS", "Herzl 1, entrance A"),
    os.getenv("ECFA_LOCALITY", "Ramat Gan"),
    os.getenv("ECFA_CONTACT_NAME", "Maya Levi"),
    os.getenv("ECFA_CONTACT_PHONE", "050-222-3333"),
    store_dir,
    args.env,
)
profile = client.load_profile_by_id(create_response["id"], store_dir)
dump({
    "environment": args.env,
    "create": create_response,
    "validation": client.validate_profile(profile).to_mapping()
})
