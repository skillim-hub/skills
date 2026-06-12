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
    payload = {'kind': 'patent', 'title': 'Pressure-controlled irrigation valve', 'applicant_name': os.getenv("IPO_APPLICANT_NAME", "Example Applicant"), 'inventors': ['Dana Cohen', 'Yossi Levi'], 'problem': 'Pressure spikes waste water and damage drip lines.', 'solution': 'A valve assembly includes a housing, inlet, outlet, downstream pressure sensor, controllable restrictor, and controller that adjusts the restrictor according to a selected irrigation-zone pressure threshold.', 'novel_features': ['zone-specific pressure threshold table', 'automatic downstream-pressure restrictor control'], 'public_disclosures': []}
    result = FilingHelperClient(environment=args.env).assess(payload)
    print(json.dumps({
        "environment": args.env,
        "request": payload,
        "assessment": result.to_dict(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
