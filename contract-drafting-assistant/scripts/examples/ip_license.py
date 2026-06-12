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
        contract_type=client.ContractType.IP_LICENSE,
        language="he",
        title="הסכם רישיון לשימוש בחומרי הדרכה",
        date_text="02/06/2026",
        parties=[
            client.Party("מדריכה מקצועית", "sole_proprietor", "123456782", "ירושלים", role="licensor"),
            client.Party(
                "חברת הדרכה בע״מ",
                "company",
                "515000020",
                "תל אביב",
                role="licensee",
                signatory_title="מנכ״ל",
            ),
        ],
        description="רישיון שימוש במצגות וחומרי הדרכה",
        deliverables=["מצגת הדרכה", "דפי עבודה", "זכות שימוש פנימית לעובדי הלקוח"],
        price_nis=8000,
        vat_included=False,
        ip_ownership="ניתן ללקוח רישיון שימוש פנימי, לא בלעדי, שאינו ניתן להעברה, ללא זכות מכירה חוזרת.",
        liability_cap_nis=8000,
    )
    result = client.ContractDraftingClient().draft(terms)
    print_payload({
        "env": env,
        "scenario": "ip-license",
        "risk_level": client.classify_risk_level(result.findings),
        "contract_markdown": result.contract_markdown,
        "findings": [asdict(finding) for finding in result.findings],
    })


if __name__ == "__main__":
    main()
