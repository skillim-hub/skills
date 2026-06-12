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
        contract_type=client.ContractType.SUPPLY_AGREEMENT,
        language="en",
        title="Office Supplies Framework Agreement",
        date_text="02/06/2026",
        parties=[
            client.Party(
                "Office Supplier Ltd.",
                "company",
                "515000010",
                "Tel Aviv",
                role="seller",
                signatory_title="CEO",
            ),
            client.Party(
                "Small Business Ltd.",
                "company",
                "515000011",
                "Ramat Gan",
                role="buyer",
                signatory_title="COO",
            ),
        ],
        description="recurring supply of office supplies",
        deliverables=["monthly purchase orders", "delivery to buyer office", "replacement of defective items"],
        price_nis=5000,
        vat_included=False,
        payment_terms="within 30 days after invoice approval",
        liability_cap_nis=5000,
    )
    result = client.ContractDraftingClient().draft(terms)
    print_payload({
        "env": env,
        "scenario": "supply-agreement",
        "risk_level": client.classify_risk_level(result.findings),
        "contract_markdown": result.contract_markdown,
        "findings": [asdict(finding) for finding in result.findings],
    })


if __name__ == "__main__":
    main()
