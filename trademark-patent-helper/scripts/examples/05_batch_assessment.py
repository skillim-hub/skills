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
    applicant = os.getenv("IPO_APPLICANT_NAME", "Example Applicant")
    requests = [
        {
            "kind": "trademark",
            "applicant_name": applicant,
            "mark_text": os.getenv("IPO_MARK_TEXT", "FLOWKITE"),
            "classes": [{"class_no": 42, "items": ["user interface design services"]}],
        },
        {
            "kind": "patent",
            "applicant_name": applicant,
            "title": "Encrypted database query optimizer",
            "solution": "A server receives encrypted query metadata, selects an encrypted index plan, and caches a privacy-preserving execution graph to reduce latency.",
            "novel_features": ["privacy-preserving execution graph cache"],
        },
    ]
    helper = FilingHelperClient(environment=args.env)
    print(json.dumps({
        "environment": args.env,
        "results": [{"request": item, "assessment": helper.assess(item).to_dict()} for item in requests],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
