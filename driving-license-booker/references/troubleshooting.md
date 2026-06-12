# Troubleshooting

Use this guide when a workflow cannot proceed normally.

## Identity validation

| Problem | Check | Resolution |
| --- | --- | --- |
| ID has fewer than nine digits | Local validation pads leading zeroes | Confirm that the padded value is accepted by checksum. |
| ID checksum fails | Digits transposed or missing | Request corrected number and retry. |
| Name differs from official record | Spelling, previous surname, or data update issue | Prepare bureau appointment if official service blocks the process. |

## Phone validation

| Problem | Check | Resolution |
| --- | --- | --- |
| Number starts with +972 | Local normalization can convert it | Store as 05XXXXXXXX or 0XXXXXXXX. |
| Landline accepted for customer but SMS needed | Service may require mobile | Ask for mobile number if an SMS step is expected. |
| Missing leading zero | Common copy-paste error | Re-enter the number in local Israeli format. |

## Renewal blockers

| Problem | Operational action |
| --- | --- |
| Medical declaration required | Mark blocker and send official declaration route. |
| Fee unpaid | Keep record ready for handoff, not completed. |
| Expired license | Warn the customer not to rely on renewal until official validity is confirmed. |
| License number missing | Continue intake, but add warning and prepare manual lookup. |
| Data mismatch | Escalate to official service or bureau appointment. |

## Appointment issues

| Problem | Operational action |
| --- | --- |
| No slots in requested city | Offer nearby cities, later dates, or cancellation monitoring by staff. |
| Wrong service selected | Cancel draft and create a correct service handoff. |
| Accessibility need not shown | Contact appointment support and record reference. |
| Customer missed appointment | Create a new handoff and record no-show reason. |

## Practical-test issues

| Problem | Operational action |
| --- | --- |
| Teacher cannot confirm | Keep draft and request new windows. |
| Vehicle class mismatch | Correct license class before coordination. |
| Candidate unavailable after confirmation | Ask teacher for rescheduling options and update local record. |
| Pickup city changed | Regenerate teacher message with new city. |

## Payment issues

| Problem | Operational action |
| --- | --- |
| Card charged but no receipt | Do not retry immediately; check official payment status. |
| Receipt exists but local record missing it | Add receipt metadata and keep original receipt in customer file. |
| Amount dispute | Separate official ₪ fee from private service fee and provide both records. |

## CLI issues

| Problem | Resolution |
| --- | --- |
| Import fails | Run `pip install -e .` from package root. |
| Command not found | Activate virtual environment and reinstall editable package. |
| JSON cannot be parsed | Use command output directly; do not prepend extra shell text. |
| State file empty | Create a record first, then use the returned `request_id`. |
