from __future__ import annotations
import argparse, json, os
from disaster_preparedness_guide import PreparednessClient

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--env', choices=['sandbox','production'], default=os.getenv('DPG_ENV','sandbox'))
    args = p.parse_args()
    client = PreparednessClient(environment=args.env)
    payload = {'environment': client.environment, 'items': client.go_bag(business=True, medications=True)}
    print(json.dumps(payload, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
