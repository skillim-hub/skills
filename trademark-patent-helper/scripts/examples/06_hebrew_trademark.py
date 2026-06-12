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
    payload = {'kind': 'trademark', 'applicant_name': os.getenv("IPO_APPLICANT_NAME_HE", "דנה לוי"), 'mark_text': 'החזרי מס מהירים', 'mark_type': 'word', 'classes': [{'class_no': 35, 'items': ['סיוע בהחזרי מס לשכירים']}], 'meaning': 'הסימן מתאר שירות מהיר להחזרי מס'}
    result = FilingHelperClient(environment=args.env).assess(payload)
    print(json.dumps({
        "environment": args.env,
        "request": payload,
        "assessment": result.to_dict(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
