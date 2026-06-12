from __future__ import annotations
import argparse, json, os
from disaster_preparedness_guide import HouseholdProfile, PreparednessClient

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--env', choices=['sandbox','production'], default=os.getenv('DPG_ENV','sandbox'))
    args = p.parse_args()
    client = PreparednessClient(environment=args.env)
    created = client.create_plan(HouseholdProfile(city=os.getenv('DPG_CITY','Haifa'), people=int(os.getenv('DPG_PEOPLE','4')), pets=True, accessibility_needs=True))
    output = os.getenv('DPG_OUTPUT','.generated/example-household-plan.json')
    client.export_json(created, output)
    payload = {'create': created, 'review': client.summarize_plan(created, created['id'])}
    print(json.dumps(payload, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
