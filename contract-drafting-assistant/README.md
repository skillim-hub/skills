# Contract Drafting Assistant

Neutral skill package for drafting practical Israeli contracts and service agreements in Hebrew or English for small businesses, freelancers, and consumers.

## What it does

- Draft service agreements, freelance agreements, consumer service terms, NDAs, sale and supply terms, and related commercial documents.
- Flag Israeli legal and operational risks: VAT ambiguity, consumer cancellation, privacy, IP ownership, limitation of liability, worker classification, and signing authority.
- Use Hebrew-first contract language with Israeli terminology.
- Provide an installable typed helper module, Typer CLI, runnable examples, and pytest coverage.

## Install

```bash
cd contract-drafting-assistant
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

Run checks:

```bash
python -m pytest scripts -q
python -m compileall scripts/ -q
```

## Quick start

Generate a built-in scenario:

```bash
contract-drafting-assistant scenario freelance-design --language he --env sandbox
```

Calculate VAT:

```bash
contract-drafting-assistant vat 12000 --rate 0.18 --env sandbox
```

Validate an Israeli ID checksum:

```bash
contract-drafting-assistant validate-id 123456782 --env sandbox
```

Generate from JSON:

```bash
contract-drafting-assistant new input.json --json --env sandbox > create-response.json
python - <<'PY'
import json
from pathlib import Path

response = json.loads(Path("create-response.json").read_text(encoding="utf-8"))
draft_id = response.get("draft_id") or "local-draft-001"
Path("draft-id.txt").write_text(draft_id, encoding="utf-8")
print(draft_id)
PY
contract-drafting-assistant check input.json --json --env sandbox > risk-response.json
```

The helper is local and does not call an external drafting API. The quick-start still keeps the common create-response pattern: extract an identifier from the first structured response, persist it, then use the same input in the next validation step. When integrating with a document system, map `draft_id` to the saved document record.

Example `input.json`:

```json
{
  "contract_type": "service_agreement",
  "language": "he",
  "title": "הסכם למתן שירותי עיצוב",
  "effective_date": "15/07/2026",
  "description": "עיצוב סימן מזהה חזותי ותבניות תפריט",
  "deliverables": ["רענון סימן מזהה חזותי", "תבנית תפריט", "5 תבניות לרשתות חברתיות"],
  "price_nis": 12000,
  "vat_included": false,
  "payment_terms": "40% מקדמה, 60% לאחר מסירה",
  "ip_ownership": "הזכויות בתוצרים הסופיים יועברו לאחר תשלום מלוא התמורה.",
  "parties": [
    {"name": "דנה כהן", "kind": "sole_proprietor", "id_number": "123456782", "address": "תל אביב", "role": "provider"},
    {"name": "רשת בתי קפה בע״מ", "kind": "company", "id_number": "515000000", "address": "רמת גן", "role": "customer"}
  ]
}
```

## Python usage

```python
from contract_drafting_assistant_client import ContractDraftingClient, sample_terms

terms = sample_terms("freelance-design", "he")
result = ContractDraftingClient().draft(terms)
print(result.contract_markdown)
```

## Examples

All examples read `CONTRACT_DRAFTING_ASSISTANT_ENV`, accept `--env sandbox|production`, and print JSON with `ensure_ascii=False` and `indent=2`.

```bash
python scripts/examples/freelance_design.py --env sandbox
python scripts/examples/risk_scan.py --env production
```

## Live verification notes

The v3 package was rechecked against live Israeli official sources on 02/06/2026. The helper keeps the standard VAT default at 18% because the Israel Tax Authority states that VAT is applied at a uniform rate of 18% from 01/01/2025. Treat tax, invoice-allocation, withholding-tax, consumer-cancellation, and privacy obligations as changeable production checks rather than immutable legal advice.

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide with decision trees, examples, edge cases, anti-patterns, checklist |
| `SKILL_HE.md` | Hebrew guide with equivalent depth and Israeli terminology |
| `references/api-reference.md` | Israeli statutes, public-data lookup patterns, validation references, error tables |
| `references/workflow-guide.md` | End-to-end workflows for service, consumer, NDA, sale/supply, website terms, negotiation |
| `references/troubleshooting.md` | Common drafting failures, red flags, replacement snippets |
| `references/test-scenarios.md` | 30 concrete scenarios and acceptance criteria |
| `references/migration-checklist.md` | Upgrade checklist from narrow or generic packages |
| `references/branding-audit.md` | Branding, visual asset, and attribution audit report |
| `references/hebrew-qa-log.md` | Hebrew quality assurance change log |
| `scripts/contract_drafting_assistant_client.py` | Typed sync/async helper module |
| `scripts/contract_drafting_assistant_cli.py` | Typer CLI |
| `scripts/test_contract_drafting_assistant_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenario scripts |
| `metadata.json` | Skill metadata |
| `CHANGELOG.md` | Keep-a-Changelog release notes |
| `LICENSE` | MIT license |
| `pyproject.toml` | Project configuration |
| `requirements-dev.txt` | Development dependencies |

## Usage guidance

Use this package for first drafts, issue spotting, negotiation alternatives, and structured checklists. Obtain legal or accounting review before signing high-value, regulated, consumer-sensitive, privacy-heavy, cross-border, real-estate, employment-adjacent, or litigation-related agreements.

## Localization conventions

- Currency: `₪12,000`
- Date: `15/07/2026`
- VAT: `מע״מ`
- Tax invoice: `חשבונית מס`
- Receipt: `קבלה`
- Withholding tax: `ניכוי מס במקור`
- Service provider: `נותן השירותים`
- Customer: `הלקוח`
- Deliverables: `תוצרים`

## Development

```bash
python -m pytest scripts -q
python -m compileall scripts/ -q
contract-drafting-assistant --help
```

The package installs top-level modules from `scripts/`, so `from contract_drafting_assistant_client import ...` works after `pip install -e .`.
