# Customer-Feedback Collector

Collect Hebrew customer feedback, testimonials, and public reviews for Israeli small businesses, freelancers, clinics, tradespeople, studios, ecommerce shops, and service providers.

The package includes neutral operating guides, Israeli channel templates for WhatsApp, email, and SMS, review-link patterns for Google, Facebook, Zap, Easy, Midrag, B144, compliance checklists, an installable Python package, a Typer CLI, pytest coverage, and runnable examples.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a plan, extract the returned plan identifier, then use that identifier in the dry-run send step.

```bash
PLAN_ID=$(python -m customer_feedback_collector.cli plan \
  --contacts scripts/examples/contacts.csv \
  --business-name "קליניקת הדר" \
  --platform google \
  --google-place-id "ChIJexample" \
  --channel whatsapp \
  --output /tmp/feedback-plan.json \
  | python -c 'import json,sys; print(json.load(sys.stdin)["plan_id"])')

python -m customer_feedback_collector.cli send \
  --plan-json /tmp/feedback-plan.json \
  --plan-id "$PLAN_ID" \
  --dry-run
```

Render one sample message:

```bash
python -m customer_feedback_collector.cli sample-message \
  --business-name "סטודיו נועה" \
  --customer-name "דנה כהן" \
  --channel whatsapp \
  --platform google \
  --google-place-id "ChIJexample"
```

Import the package from Python:

```python
import customer_feedback_collector as cfc

business = cfc.BusinessProfile(display_name="קליניקת הדר", google_place_id="ChIJexample")
contact = cfc.Contact(full_name="דנה כהן", phone="050-123-4567")
message = cfc.render_message(contact, business, platform="google", channel="whatsapp")
print(message.body)
```

Run tests and syntax checks:

```bash
pytest
python -m compileall scripts/ -q
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide with examples, decision trees, edge cases, anti-patterns, troubleshooting, and production checklist. |
| `SKILL_HE.md` | Hebrew guide with Israeli professional terminology, ₪ examples, and DD/MM/YYYY localization. |
| `references/api-reference.md` | API, platform, and Israeli regulation reference with examples and error tables. |
| `references/workflow-guide.md` | End-to-end workflows for WhatsApp, email, SMS, testimonial capture, and low-rating routing. |
| `references/troubleshooting.md` | Practical fixes for delivery, link, Hebrew, consent, rate-limit, and platform issues. |
| `references/test-scenarios.md` | Concrete validation and acceptance scenarios. |
| `references/migration-checklist.md` | Migration checklist from manual review collection, survey-only flows, and generic automations. |
| `references/branding-audit.md` | Branding, attribution, visual-asset, and emoji audit report. |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization correction log. |
| `references/verification-log.md` | Web validation log with two-pass source evidence, corrections, and final unresolved items. |
| `customer_feedback_collector/` | Installable Python package. |
| `scripts/customer_feedback_collector_client.py` | Compatibility client entrypoint. |
| `scripts/customer_feedback_collector_cli.py` | CLI script entrypoint. |
| `scripts/test_customer_feedback_collector_client.py` | pytest suite with more than 20 tests. |
| `scripts/examples/` | Runnable scenario scripts that read environment variables and accept `--env sandbox|production`. |

## Production note

Verify current legal requirements, platform terms, and API versions before production rollout. The reference material is designed for implementation planning and operational guardrails, not legal advice.
