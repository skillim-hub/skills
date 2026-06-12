# Installment Calculator (Tashlumim)

Calculate Israeli installment plans for small businesses, freelancers, retailers, and consumers. Produce payment schedules in shekels, include interest and fees, compare alternatives, estimate refund exposure, and prepare disclosure-ready summaries for review.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

Run the test suite:

```bash
pytest -q
python -m compileall scripts/ -q
```

Run the CLI:

```bash
installment-calculator calculate --price 1200 --installments 6 --annual-rate 8.5 --per-installment-fee 2.90 --first-due-date 15/07/2026
```

## Quick start

```python
from installment_calculator import InstallmentRequest, calculate_plan, estimate_refund

create_response = calculate_plan(InstallmentRequest(
    cash_price="3600",
    installments=12,
    annual_interest_rate="7.5",
    upfront_fee="49",
    per_installment_fee="1.90",
    first_due_date="05/07/2026",
))

plan_id = create_response.to_dict()["label"] or "local-plan-001"
next_step = estimate_refund(create_response, installments_paid=3, cancellation_fee="0")

print(plan_id)
print(create_response.disclosure_table())
print(next_step)
```

The quick-start flow keeps the created plan object, extracts a local identifier for the next operation, then uses the same calculated plan in the refund estimate. In an application, persist the serialized plan and pass the saved plan identifier to later cancellation, service, or reconciliation steps.

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide, examples, decision trees, edge cases, checklist |
| `SKILL_HE.md` | Hebrew guide with Israeli terminology and ₪ plus DD/MM/YYYY localization |
| `references/api-reference.md` | Local API and regulation reference with schemas, examples, and error tables |
| `references/workflow-guide.md` | End-to-end workflows for checkout, quotes, invoices, refunds, and comparison |
| `references/troubleshooting.md` | Common calculation, disclosure, and implementation problems |
| `references/test-scenarios.md` | More than 20 concrete scenarios for manual and automated testing |
| `references/migration-checklist.md` | Migration checklist for existing stores, spreadsheets, and CRM flows |
| `references/branding-audit.md` | Branding, attribution, visual-link, and emoji audit report |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization QA log |
| `references/verification-log.md` | Web validation log with pass 1 and pass 2 sources |
| `installment_calculator/` | Installable Python package |
| `scripts/installment_calculator_client.py` | Underscored script-compatible client import surface |
| `scripts/installment-calculator-cli.py` | Command-line launcher |
| `scripts/test_installment_calculator_client.py` | Pytest suite with more than 20 tests |
| `scripts/examples/` | Runnable examples for common Israeli business cases |

## CLI examples

```bash
installment-calculator --env sandbox calculate --price 9800 --down-payment 2800 --installments 4 --output json
installment-calculator compare --price 3600 --installments 3 --installments 12 --annual-rate 0 --annual-rate 7.5
installment-calculator refund --price 2400 --installments 12 --paid 4 --annual-rate 6.9
```

## Web-validated regulatory baseline

Verification performed on 02/06/2026 confirmed these operational baselines for documentation and examples: Israeli VAT is 18% from 01/01/2025; consumer-facing prices generally need total-price wording that includes mandatory charges such as VAT; qualifying consumer cancellation fees are commonly capped at the lower of 5% or ₪100; Israel Invoice allocation thresholds changed in 2026. Review `references/verification-log.md` before production use.

## Legal and accounting caution

Use the package as a calculation and disclosure helper. Verify current legal, tax, card-acquirer, and bookkeeping requirements before production use, especially when changing finance charges, cancellation terms, VAT treatment, invoice allocation thresholds, or consumer-facing disclosures.
