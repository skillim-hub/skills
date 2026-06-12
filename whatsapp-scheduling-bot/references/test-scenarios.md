# Test Scenarios

Run these scenarios before production. Each scenario includes input, expected behavior, and acceptance criteria.

## 1. Normalize Israeli Mobile

Input: `054-123-4567`

Expected: `972541234567`

Acceptance: phone is valid for WhatsApp API.

## 2. Normalize +972 Mobile

Input: `+972 54 123 4567`

Expected: `972541234567`

Acceptance: no duplicate leading zero remains.

## 3. Normalize Landline

Input: `03-123-4567`

Expected: `97231234567`

Acceptance: landline format is accepted where the sender can deliver.

## 4. Reject Short Phone

Input: `541234567`

Expected: validation error.

Acceptance: no message is sent.

## 5. Reject Letters in Phone

Input: `054-abc-4567`

Expected: validation error.

Acceptance: operator sees a clear error.

## 6. Direct Booking

Input contains name, phone, service, date, time, duration, price, and location.

Expected: appointment is created and confirmation uses Hebrew, `DD/MM/YYYY`, and `₪`.

Acceptance: status is `confirmed`.

## 7. New Appointment Request

Incoming:

```text
אפשר תור למחר בבוקר?
```

Expected: bot asks for service or offers slots if service is known.

Acceptance: no appointment is created before clear selection.

## 8. Offer Three Slots

Calendar has five slots.

Expected: bot sends at most three options.

Acceptance: message is short and numbered.

## 9. Customer Selects Slot

Customer replies `1`.

Expected: selected slot is held, event is created, confirmation sent.

Acceptance: reminder jobs are created.

## 10. 24-Hour Reminder Due

Appointment: `18/06/2026 10:30`

Now: `17/06/2026 10:31`

Expected: 24-hour reminder is due.

Acceptance: one reminder is sent.

## 11. 2-Hour Reminder Not Due

Appointment: `18/06/2026 10:30`

Now: `18/06/2026 07:30`

Expected: 2-hour reminder is not due.

Acceptance: reminder remains pending.

## 12. Duplicate Reminder

Worker runs twice.

Expected: first run sends; second run skips.

Acceptance: one provider message ID exists.

## 13. Cancel Before Reminder

Appointment cancelled before reminder time.

Expected: reminder skipped.

Acceptance: no WhatsApp send.

## 14. Reschedule Recalculates Reminders

Move from `18/06/2026 10:30` to `19/06/2026 13:00`.

Expected: old reminders replaced.

Acceptance: new reminder send times match new appointment.

## 15. Customer Confirms

Reply: `1`

Expected: appointment remains confirmed and confirmation response is recorded.

Acceptance: optional short acknowledgement inside service window.

## 16. Customer Requests Change

Reply: `2`

Expected: reschedule/cancel options are offered.

Acceptance: no cancellation until intent is clear.

## 17. Customer Cancels

Reply: `3` or `בטלי לי`

Expected: cancellation flow starts and policy is checked.

Acceptance: calendar and reminders are updated.

## 18. Ambiguous Reply

Reply:

```text
סבבה
```

Expected: bot checks context or asks for a numbered reply.

Acceptance: no destructive action.

## 19. Voice Note

Incoming type: `audio`

Expected: route to staff or transcription.

Acceptance: no automatic appointment created.

## 20. Webhook Verification Success

Token matches.

Expected: HTTP 200 and challenge body.

Acceptance: response body equals challenge exactly.

## 21. Webhook Verification Failure

Token differs.

Expected: HTTP 403.

Acceptance: no subscription is accepted.

## 22. Template Variables

Template has seven placeholders.

Expected: builder supplies seven parameters.

Acceptance: no mismatch error.

## 23. Hebrew Template Language

Expected payload language: `he`.

Acceptance: provider receives `{"code": "he"}`.

## 24. Sensitive Medical Request

Incoming:

```text
אני צריך ייעוץ רפואי דחוף
```

Expected: route to staff.

Acceptance: bot gives no medical advice.

## 25. Opt-Out

Incoming:

```text
הסר
```

Expected: opt-out flag set and acknowledgement sent once.

Acceptance: future non-essential reminders skipped.

## 26. Friday Closed by Default

Appointment requested on Friday.

Expected: reject unless Friday is enabled.

Acceptance: alternatives offered.

## 27. Saturday Closed by Default

Appointment requested on Saturday.

Expected: reject.

Acceptance: no booking created.

## 28. After-Hours Request

Requested at `22:00`.

Expected: reject or offer working-hour alternatives.

Acceptance: no appointment outside hours.

## 29. Price Formatting

Input price: `250`

Expected: `₪250`

Acceptance: no `NIS`, `ILS`, or misplaced symbol.

## 30. Address Formatting

Input address: `רחוב הרצל 10, תל אביב`

Expected: address on a separate line in reminder.

Acceptance: readable on a WhatsApp mobile screen.

## 31. CSV Import

CSV contains three future appointments.

Expected: valid rows load, invalid rows report errors, no automatic sends unless selected.

Acceptance: import report includes valid, skipped, invalid.

## 32. Provider 401

API returns 401.

Expected: no retry storm.

Acceptance: token rotation alert.

## 33. Provider 429

API returns 429.

Expected: queue and backoff.

Acceptance: no duplicate customer messages.

## 34. Provider 5xx

API returns 500.

Expected: retry with jitter.

Acceptance: skip if appointment starts before retry.

## 35. Calendar Conflict

Slot selected but booked manually.

Expected: offer alternatives.

Acceptance: no duplicate calendar event.

## 36. Multiple Appointments Same Phone

Phone belongs to parent booking two children.

Expected: ask which appointment.

Acceptance: no wrong cancellation.

## 37. Daylight Saving

Appointment around Israel DST change.

Expected: timezone-aware calculations.

Acceptance: reminder send time is correct.

## 38. Customer Uses English STOP

Incoming: `STOP`

Expected: opt-out.

Acceptance: state persists.

## 39. Waiting List Offer

Cancellation opens a slot.

Expected: offer with expiry.

Acceptance: only eligible customer can claim.

## 40. Staff Daily Review

End-of-day job runs.

Expected: summary with total appointments, sent reminders, failures, open changes, cancellations.

Acceptance: staff can act on all exceptions.
