# Credit-Card Receipt Generator

Generate reconciliation-grade receipt drafts for Israeli card payments from Cardcom, Tranzila, Grow/Meshulam, and Pelecard payloads.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a Markdown receipt from a gateway JSON export:

```bash
python scripts/credit_card_receipt_generator_cli.py from-json payment.json \
  --gateway cardcom \
  --business-name "Kinneret Studio" \
  --business-tax-id 515123453 \
  --format markdown \
  --output receipt.md
```

Generate a sample receipt:

```bash
python scripts/credit_card_receipt_generator_cli.py sample --gateway grow
```

Show an endpoint reference:

```bash
python scripts/credit_card_receipt_generator_cli.py endpoint pelecard add_receipt
```

Run tests:

```bash
pytest -q
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide, examples, decision tree, troubleshooting, anti-patterns |
| `SKILL_HE.md` | Hebrew operating guide with Israeli terminology and date/currency conventions |
| `references/api-reference.md` | Web-validated Israeli API and regulation reference with endpoint paths and error tables |
| `references/troubleshooting.md` | Debugging guide by gateway, VAT mode, and security issue |
| `references/test-scenarios.md` | Concrete test scenarios for gateway and VAT behavior |
| `scripts/credit_card_receipt_generator_client.py` | Typed sync/async receipt generator and gateway normalizer |
| `scripts/credit_card_receipt_generator_cli.py` | Click CLI for JSON input, samples, validation, and endpoint lookup |
| `scripts/test_credit_card_receipt_generator_client.py` | Pytest suite with validation, formatting, CLI, and async coverage |
| `metadata.json` | Skill metadata without attribution fields |
| `CHANGELOG.md` | Keep a Changelog history |
| `LICENSE` | MIT license |
| `pyproject.toml` | Package metadata and pytest config |
| `requirements-dev.txt` | Test and CLI development dependencies |

## Safety boundary

Use this package only for legitimate payment records. Do not fabricate receipts, alter gateway identifiers, or store full card numbers. Treat generated output as a draft unless a certified accounting system or gateway document module issued the official accounting document.
