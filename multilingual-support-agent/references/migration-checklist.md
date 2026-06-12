# Migration Checklist

Use this checklist when replacing ad-hoc multilingual replies, spreadsheet templates, or a single-language support bot.

## Discovery

- Export existing templates and classify by language.
- Identify active channels: WhatsApp, email, website chat, phone notes, social inbox, CRM.
- List business policies: refunds, returns, cancellations, warranty, shipping, privacy, marketing consent.
- Identify the accounting system and document types in use.
- Identify courier and payment providers.
- Identify the owner of high-risk approvals.

## Cleanup

- Remove organization-specific branding, decorative images, and personal attribution.
- Remove promises that conflict with business policy.
- Replace full-card-number requests with last-four wording.
- Replace legal, tax, and accounting conclusions with escalation wording.
- Normalize dates to DD/MM/YYYY and shekel amounts to ₪.
- Remove duplicated templates that differ only by tone.

## Localization

- Review Hebrew with a fluent Israeli business-service reviewer.
- Review Arabic for professional Modern Standard Arabic.
- Review Russian for formal customer-service tone.
- Review English for Israeli operating context.
- Preview RTL and LTR rendering in every channel.
- Confirm that Hebrew prose has no nikud in technical content.

## Technical migration

- Install with `pip install -e .`.
- Install development dependencies with `pip install -r requirements-dev.txt`.
- Replace hyphenated import hacks with `from multilingual_support_agent import SupportAgentClient`.
- Store environment settings in variables instead of hard-coded scripts.
- Add `--env sandbox|production` to every local runbook.
- Use structured JSON outputs for logging and tests.
- Add a human-review queue for high-risk classifications.

## Rollout

- Run the full pytest suite.
- Run `python -m compileall scripts/ -q`.
- Run at least 20 scenario tests before production.
- Start with human review for all medium and high-risk tickets.
- Track wrong-language rate, escalation rate, refund promise errors, privacy handling errors, and reopened tickets.
- Review templates after the first 50 real conversations.
- Schedule recurring review for legal, tax, privacy, accessibility, and consumer-protection changes.
