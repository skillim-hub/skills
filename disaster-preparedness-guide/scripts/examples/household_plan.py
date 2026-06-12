from __future__ import annotations
import argparse, json, os
from disaster_preparedness_guide import HouseholdProfile, PreparednessClient

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--env', choices=['sandbox','production'], default=os.getenv('DPG_ENV','sandbox'))
    args = p.parse_args()
    client = PreparednessClient(environment=args.env)
    payload = client.household_plan(HouseholdProfile(city=os.getenv('DPG_CITY','Haifa'), people=int(os.getenv('DPG_PEOPLE','4')), pets=os.getenv('DPG_PETS','true').lower() in {'1','true','yes'}, children=int(os.getenv('DPG_CHILDREN','2')), medications=os.getenv('DPG_MEDICATIONS','true').lower() in {'1','true','yes'})).to_dict()
    print(json.dumps(payload, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
