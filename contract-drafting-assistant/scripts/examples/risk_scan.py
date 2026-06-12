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
    terms = client.ContractTerms(
        contract_type=client.ContractType.FREELANCE_AGREEMENT,
        language="en",
        parties=[client.Party("Freelancer"), client.Party("Customer")],
        price_nis=15000,
        vat_included=None,
        description="full-time software work with fixed hours using company equipment",
        personal_data=True,
        employment_like_facts=["fixed hours", "company equipment", "exclusive"],
    )
    findings = client.scan_risks(terms)
    print_payload({
        "env": env,
        "scenario": "risk-scan",
        "risk_level": client.classify_risk_level(findings),
        "findings": [asdict(finding) for finding in findings],
    })


if __name__ == "__main__":
    main()
