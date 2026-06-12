# Troubleshooting

## Before troubleshooting

Confirm that the user is on the official service or appointment channel, the selected service category is correct, Teudat Zehut is 9 digits and valid, phone can receive SMS if SMS is required, and no secret is being shared.

## No available appointments

Likely causes: high demand, narrow date range, narrow city range, wrong service, branch closure, or holiday schedule.

Actions:
1. Expand the date range.
2. Expand the city radius.
3. Try nearby bureaus.
4. Re-check service category.
5. Retry later through the official channel.
6. Do not use appointment brokers or trading groups.

## Appointment disappears before confirmation

Likely cause: the official system did not reserve the slot until final confirmation.

Actions: choose another official slot, complete confirmation in one session, and keep the confirmation message.

## Teudat Zehut rejected

Likely causes: missing leading zero, typo, checksum failure, or passport number entered instead of ID.

Actions: enter exactly 9 digits, strip spaces and hyphens, validate locally, and re-check official records if the number still fails.

## SMS not received

Likely causes: unsupported phone format, roaming, carrier filtering, blocked short-code messages, or wrong number.

Actions: normalize to `05XXXXXXXX`, check signal and blocked SMS, retry once through official channel, and use another valid contact method only if allowed and consented.

## Payment page fails

Likely causes: 3-D Secure blocked, browser extension, unsupported browser, card decline, or official payment provider issue.

Actions: use a current browser, disable interfering extensions, complete payment manually, never share card number or CVV, and keep the official receipt after success.

## Minor appointment blocked

Likely causes: wrong category, missing guardian details, missing consent, or custody/guardianship issue.

Actions: switch to minor workflow, verify official parental-consent requirements, add guardian documents, and avoid custody legal advice.

## Urgent travel but no slots

Likely causes: high demand, eligibility problem, emergency service location mismatch, or travel too close.

Actions: check official urgent travel instructions, use earliest official slot, prepare travel proof if required, avoid promises, and use only published official contact channels.

## User cannot log in

Likely causes: account issue, OTP delivery problem, forgotten password, cookie problem, or browser problem.

Actions: direct the user to official account recovery, never ask for OTP or password, try a supported browser, and complete identity checks only through official channels.

## Existing appointment cannot be changed

Likely causes: confirmation missing, appointment too close, edit policy limitation, or booking made under another account or phone.

Actions: use official cancellation/change link, keep old appointment until replacement is confirmed, avoid duplicates, and contact official support if blocked.

## Bureau information inconsistent

Likely causes: stale cache, changed hours, holiday, security event, or third-party inaccuracy.

Actions: prefer current official pages, verify branch address and hours before travel, add buffer for parking and security screening, and do not rely on local cache alone.

## Helper script errors

| Error | Message | Recovery |
|---|---|---|
| `InvalidTeudatZehut` | ID number failed validation | Correct the number, including leading zeros |
| `InvalidPhone` | Phone cannot be normalized | Use an Israeli mobile or accepted landline |
| `InvalidEmail` | Email syntax failed | Re-enter the address |
| `InvalidDateWindow` | Date range invalid | Use ISO dates and ensure end date is after start date |
| `UnsupportedService` | Service is unknown | Use a documented service key |
| `NoCandidates` | No slots supplied | Paste official candidate slots or widen search |
| `UnsafeSource` | Slot source is not official | Use gov.il or official appointment channel |

## Browser checklist

- Use a current browser.
- Disable VPN if blocked by the official page.
- Disable form-filling extensions if fields break.
- Allow required cookies for official domains.
- Try private browsing for a clean session.
- Keep the official confirmation page or message.

## Data cleanup

1. Delete temporary JSON files containing full ID numbers.
2. Keep only the official confirmation if still needed.
3. Mask ID numbers in notes.
4. Remove stale calendar files after the appointment.
5. Clear shared downloads on business computers.
