from __future__ import annotations
import argparse, json, os
from disaster_preparedness_guide import PreparednessClient

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--env', choices=['sandbox','production'], default=os.getenv('DPG_ENV','sandbox'))
    args = p.parse_args()
    client = PreparednessClient(environment=args.env)
    payload = client.decide_action(os.getenv('DPG_HAZARD','missile'), {'business_open': True, 'accessibility_needs': True})
    print(json.dumps(payload, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
