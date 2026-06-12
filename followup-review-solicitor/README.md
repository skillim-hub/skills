# Follow-Up & Review Solicitor

A neutral skill package for generating Hebrew follow-up messages and review requests for Israeli small businesses, freelancers, and consumer-facing service contexts.

## What it does

- Creates Hebrew follow-up, payment reminder, appointment reminder, delivery check-in, and review request messages.
- Recommends Israeli-friendly send times in `Asia/Jerusalem`.
- Applies consent, opt-out, sentiment, and sensitive-context guardrails.
- Provides an installable Python package, Typer command line helper, runnable examples, and pytest suite.
- Uses ₪ amounts and `DD/MM/YYYY` dates in public-facing output.

## Install

```bash
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

## Quick start with request ID chaining

Create a saved request, extract its ID, then generate the plan from that ID:

```bash
CREATE_RESPONSE=$(python scripts/followup-review-solicitor-cli.py create-request \
  --business-name "אור חשמל" \
  --customer-name "דנה" \
  --event-type service_completed \
  --event-date 03/06/2026 \
  --channel whatsapp \
  --sentiment unknown)

REQUEST_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")

python scripts/followup-review-solicitor-cli.py generate \
  --request-id "$REQUEST_ID" \
  --output text
```

Generate a direct review request after positive feedback:

```bash
python scripts/followup-review-solicitor-cli.py generate \
  --business-name "אור חשמל" \
  --customer-name "דנה" \
  --event-type review_request \
  --event-date 03/06/2026 \
  --channel whatsapp \
  --sentiment positive \
  --review-url "https://g.page/r/example/review"
```

Run tests:

```bash
python -m pytest scripts -q
python -m compileall scripts/ -q
```

## Python usage

```python
from followup_review_solicitor import (
    Channel,
    EventType,
    FollowupRequest,
    FollowupSolicitorClient,
    Sentiment,
)

request = FollowupRequest(
    business_name="אור חשמל",
    customer_name="דנה",
    event_type=EventType.SERVICE_COMPLETED,
    event_date="03/06/2026",
    channel=Channel.WHATSAPP,
    sentiment=Sentiment.UNKNOWN,
)

plan = FollowupSolicitorClient().generate_plan(request)
print(plan.message_he)
```

## Examples

Each example reads environment variables, supports `--env sandbox|production`, and prints JSON with Hebrew preserved.

```bash
SANDBOX_BUSINESS_NAME="אור חשמל" \
SANDBOX_CUSTOMER_NAME="דנה" \
python scripts/examples/service_checkin.py --env sandbox
```

Production-specific variables use the `PROD_` prefix:

```bash
PROD_BUSINESS_NAME="אור חשמל" \
PROD_CUSTOMER_NAME="דנה" \
PROD_REVIEW_URL="https://g.page/r/example/review" \
python scripts/examples/review_request_after_positive_reply.py --env production
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide with examples, decision tree, anti-patterns, and checklist. |
| `SKILL_HE.md` | Hebrew operating guide with Israeli terminology and localized examples. |
| `references/api-reference.md` | Regulatory and integration reference with request/response examples and error tables. |
| `references/workflow-guide.md` | End-to-end workflows for real businesses and consumers. |
| `references/troubleshooting.md` | Troubleshooting for scheduling, consent, messages, channels, and imports. |
| `references/test-scenarios.md` | 30 concrete validation scenarios. |
| `references/migration-checklist.md` | Migration checklist from manual or legacy automations. |
| `references/branding-audit.md` | Audit report for restricted identifiers, image references, and public Markdown cleanup. |
| `references/hebrew-qa-log.md` | Hebrew QA notes and localization changes. |
| `references/verification-log.md` | Web validation log with pass 1 and pass 2 sources. |
| `followup_review_solicitor/` | Installable Python package. |
| `scripts/followup_review_solicitor_client.py` | Underscored script import surface for the client. |
| `scripts/followup-review-solicitor-cli.py` | Command line helper. |
| `scripts/test_followup_review_solicitor_client.py` | Pytest suite with more than 20 tests. |
| `scripts/examples/` | Runnable scenario scripts. |
| `metadata.json` | Skill metadata. |
| `CHANGELOG.md` | Keep-a-Changelog style release notes. |
| `LICENSE` | MIT license. |
| `pyproject.toml` | Installable package and test configuration. |
| `requirements-dev.txt` | Development dependencies. |

## Development notes

- Keep generated messages neutral and concise.
- Keep review requests non-incentivized and non-coercive.
- Verify current legal and platform requirements before production deployment.
