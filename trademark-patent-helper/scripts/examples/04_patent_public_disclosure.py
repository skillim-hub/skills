from __future__ import annotations

import argparse
import json
import os

from trademark_patent_helper import FilingHelperClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("IPO_ENV", "sandbox"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = {'kind': 'patent', 'title': 'Bicycle lock mechanism', 'applicant_name': os.getenv("IPO_APPLICANT_NAME", "Example Applicant"), 'solution': 'A lock includes a rotating cam, spring-loaded latch, reinforced housing, and coded release module.', 'novel_features': ['cam and latch geometry'], 'public_disclosures': [{'date': '12/04/2026', 'channel': 'YouTube', 'details': 'public demo video'}]}
    result = FilingHelperClient(environment=args.env).assess(payload)
    print(json.dumps({
        "environment": args.env,
        "request": payload,
        "assessment": result.to_dict(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
