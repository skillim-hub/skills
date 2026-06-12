# Test Scenarios

Use these scenarios to validate message quality, timing, compliance, and channel handling. Each scenario includes expected behavior.

| # | Scenario | Input highlights | Expected result |
|---:|---|---|---|
| 1 | Electrician finished job, sentiment unknown | service_completed, WhatsApp, Wednesday 15:00 | Send check-in at 18:30, no review link yet. |
| 2 | Customer replied positively | review_request, positive, review_url | Send neutral review request 10-30 minutes later or next friendly slot. |
| 3 | Customer complained about repair | sentiment negative | Do not request review; send support escalation. |
| 4 | Missing review URL | review_request, positive, no review_url | `should_send=false` or ask for feedback without public review link. |
| 5 | Opted-out contact | consent_status opted_out | Suppress; no message body. |
| 6 | Promotional coupon included | marketing text, consent unknown | Remove promotion or block until opt-in. |
| 7 | SMS after 21:00 | now 21:30 | Schedule next business day 09:30. |
| 8 | Friday 13:00 check-in | Friday after cutoff | Schedule Sunday 09:30. |
| 9 | Saturday attempt | Saturday | Schedule Sunday 09:30. |
| 10 | Accountant missing May documents | business_type accountant, period_label May 2026 | Use `חשבוניות/קבלות`, `דיווח`, due date DD/MM/YYYY. |
| 11 | Invoice reminder with amount | amount 1250 | Format `₪1,250`. |
| 12 | Payment already marked paid | invoice_due but paid true | Do not send reminder; optionally send receipt confirmation. |
| 13 | Appointment reminder for clinic | clinic, appointment_time | Do not include treatment type. |
| 14 | Delivery check-in | delivered yesterday | Ask whether delivery arrived, no immediate review request. |
| 15 | No customer name | customer_name empty | Use `היי,` without placeholder. |
| 16 | English brand name | business_name `FixPro` | Keep brand name, Hebrew body. |
| 17 | Long SMS | sms, review_url long | Warn about length or shorten text. |
| 18 | Duplicate job event | same idempotency key | Treat as already queued; no duplicate send. |
| 19 | Old customer list | event 9 months old | Require manual approval and relevance check. |
| 20 | Consumer asks seller for status | consumer_followup | Produce polite update request. |
| 21 | Lawyer follow-up | sensitive business_type legal | Use generic wording; manual approval. |
| 22 | Customer asked for refund | complaint_open true | Stop review flow and create support message. |
| 23 | Branch-specific review | branch_name and branch review_url | Use branch link and branch context. |
| 24 | Missing business name | business_name empty | Block customer-facing message until completed. |
| 25 | Invalid Israeli phone | phone `12345` | Reject SMS/WhatsApp send. |
| 26 | Holiday blackout configured | holiday date in blackout list | Move to next allowed business window. |
| 27 | Email invoice reminder | channel email | Use formal subject and include enough context. |
| 28 | SMS opt-out phrase inbound | inbound `הסר` | Add suppression for that channel. |
| 29 | WhatsApp policy window expired | last inbound older than provider limit | Use approved template or wait. |
| 30 | Review incentive requested | coupon for review | Block request; suggest neutral non-incentivized review text. |

## Acceptance criteria

A scenario passes when:

- The message is grammatical Hebrew.
- No unresolved placeholders remain.
- The recommended time follows Israeli business rules.
- Consent and opt-out rules are respected.
- Review requests are neutral and non-coercive.
- Sensitive details are removed from SMS and WhatsApp.
- Dates use `DD/MM/YYYY`.
- Amounts use `₪`.
- Machine output can be serialized to JSON.
