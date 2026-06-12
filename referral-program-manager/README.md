# Referral Program Manager

Neutral documentation and Python tooling for setting up and tracking Israeli customer referral programs with payment-gateway, payout, fraud-review, and accounting workflows.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

The CLI prints JSON so the identifiers from one step can be used in the next step.

```bash
python scripts/referral-program-manager-cli.py init-state --state demo.json

PROGRAM_ID="$(
  python scripts/referral-program-manager-cli.py create-program \
    --state demo.json \
    --program-id salon-50-2026 \
    --name "Salon ₪50 Referral" \
    --reward-type credit \
    --reward-amount 50 \
    --qualifying-action paid_completed_appointment \
    --cooldown-days 0 \
    --max-rewards 10 \
  | python -c 'import json,sys; print(json.load(sys.stdin)["program_id"])'
)"

python scripts/referral-program-manager-cli.py add-customer \
  --state demo.json \
  --customer-id cust_1001 \
  --name "Dana Levi" \
  --email dana@example.co.il \
  --phone 050-1234567 \
  --marketing-consent

python scripts/referral-program-manager-cli.py add-customer \
  --state demo.json \
  --customer-id cust_2002 \
  --name "Noa Cohen" \
  --email noa@example.co.il \
  --phone 052-7654321 \
  --marketing-consent

EVENT_ID="$(
  python scripts/referral-program-manager-cli.py register \
    --state demo.json \
    --program-id "$PROGRAM_ID" \
    --referrer-id cust_1001 \
    --referred-customer-id cust_2002 \
    --source booking_form \
  | python -c 'import json,sys; print(json.load(sys.stdin)["event_id"])'
)"

python scripts/referral-program-manager-cli.py qualify \
  --state demo.json \
  --event-id "$EVENT_ID" \
  --invoice INV-2026-0042 \
  --order-amount 200

REWARD_ID="$(
  python scripts/referral-program-manager-cli.py approve \
    --state demo.json \
    --event-id "$EVENT_ID" \
    --actor owner \
    --tax-treatment customer_credit \
  | python -c 'import json,sys; print(json.load(sys.stdin)["reward_id"])'
)"

echo "Approved reward: $REWARD_ID"
```

## Python import

After installation, import the package directly:

```python
from referral_program_manager import ReferralProgramManager

manager = ReferralProgramManager()
manager.create_program(
    program_id="salon-50-2026",
    name="Salon ₪50 Referral",
    reward_type="credit",
    reward_amount_ils=50,
    qualifying_action="paid_completed_appointment",
    cooldown_days=3,
)
```

## Run tests

```bash
python -m pytest scripts -q
python -m compileall scripts/ -q
```

## Run examples

Examples read environment variables and accept `--env sandbox|production`.

```bash
RPM_GATEWAY=manual RPM_GATEWAY_API_KEY=test \
  python scripts/examples/ecommerce_gateway_payout.py --env sandbox
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide with examples, edge cases, decision trees, anti-patterns, and production checklist. |
| `SKILL_HE.md` | Hebrew operating guide with Israeli professional terminology and ₪/DD/MM/YYYY localization. |
| `references/api-reference.md` | Israeli payment-gateway and regulation reference with request/response examples and error tables. |
| `references/workflow-guide.md` | End-to-end workflows for launch, ecommerce, B2B payouts, fraud review, migration, support, and reconciliation. |
| `references/troubleshooting.md` | Diagnostic trees, gateway troubleshooting, fraud review, recovery procedures. |
| `references/test-scenarios.md` | 30 concrete automated and manual test scenarios. |
| `references/migration-checklist.md` | Migration plan from spreadsheet, CRM, ecommerce, or previous tools. |
| `references/branding-audit.md` | Distribution-neutrality and visual-reference audit report. |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization QA log. |
| `references/verification-log.md` | Web-validated official-source verification log with pass 1 and pass 2 sources. |
| `src/referral_program_manager/` | Installable Python package. |
| `scripts/referral_program_manager_client.py` | Underscored direct script helper with the same typed client implementation. |
| `scripts/referral-program-manager-cli.py` | CLI wrapper. |
| `scripts/test_referral_program_manager_client.py` | Pytest suite with more than 20 tests. |
| `scripts/examples/` | Runnable scenarios for operating workflows. |
| `metadata.json` | Skill metadata without creator fields. |
| `CHANGELOG.md` | Keep a Changelog format. |
| `LICENSE` | MIT license. |
| `pyproject.toml` | Python project metadata and pytest configuration. |
| `requirements-dev.txt` | Development and test dependencies. |

## Production note

Provider endpoints, permissions, and regulatory duties depend on the merchant account, enabled modules, and actual reward structure. Confirm final production configuration with the payment provider, accountant, and legal advisor before launch.
