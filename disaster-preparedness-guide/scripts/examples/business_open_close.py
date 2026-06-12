from __future__ import annotations
import argparse, json, os
from disaster_preparedness_guide import BusinessProfile, PreparednessClient

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--env', choices=['sandbox','production'], default=os.getenv('DPG_ENV','sandbox'))
    args = p.parse_args()
    client = PreparednessClient(environment=args.env)
    payload = client.business_plan(BusinessProfile(city=os.getenv('DPG_CITY','Ashdod'), business_type=os.getenv('DPG_BUSINESS_TYPE','grocery store'), employees=int(os.getenv('DPG_EMPLOYEES','3')), customers_peak=int(os.getenv('DPG_CUSTOMERS_PEAK','12')), protected_space_capacity=int(os.getenv('DPG_PROTECTED_SPACE_CAPACITY','10')), daily_revenue_nis=int(os.getenv('DPG_DAILY_REVENUE_NIS','3200')))).to_dict()
    print(json.dumps(payload, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
