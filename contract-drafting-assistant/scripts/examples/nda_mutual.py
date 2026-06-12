from __future__ import annotations

import argparse
import json
from dataclasses import asdict
import os

import contract_drafting_assistant_client as client


def parse_env() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env",
        choices=["sandbox", "production"],
        default=os.environ.get("CONTRACT_DRAFTING_ASSISTANT_ENV", "sandbox"),
    )
    args = parser.parse_args()
    return args.env


def print_payload(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    env = parse_env()
    terms = client.sample_terms("nda", "en")
    result = client.ContractDraftingClient().draft(terms)
    print_payload({
        "env": env,
        "scenario": "nda-mutual",
        "risk_level": client.classify_risk_level(result.findings),
        "contract_markdown": result.contract_markdown,
        "findings": [asdict(finding) for finding in result.findings],
    })


if __name__ == "__main__":
    main()
