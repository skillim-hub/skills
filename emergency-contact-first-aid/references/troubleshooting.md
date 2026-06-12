# Troubleshooting

## Validation problems

### Review date rejected

Cause: Date is not in `DD-MM-YYYY` or `DD/MM/YYYY`.

Fix: Use `04-06-2026` for English-facing profiles or `04/06/2026` for Hebrew-facing display material.

### Contact missing

Cause: The `contacts` array is empty or misnamed.

Fix: Add at least one contact with name, phone, and priority. Add a second contact for production use.

### Phone rejected

Accepted examples:

- `050-123-4567`
- `0521234567`
- `03-1234567`
- `+972501234567`
- `101`
- `100`
- `102`
- `103`
- `104`
- `106`
- `107`
- `1221`

Avoid extensions only or free text.

### Duplicate priority

Cause: Two contacts have priority 1.

Fix: Assign a clear order such as 1, 2, 3.

### Strict privacy failure

Cause: A 9-digit value looks like an Israeli ID number.

Fix: Remove the value unless a formal and restricted reason exists.

## Operational problems

### Staff call the owner before emergency dispatch

Fix:

1. Place the emergency number section above contacts.
2. Add red flag examples.
3. Drill the first five minutes.
4. Make the owner contact step happen only after dispatch is active.

### Responders cannot find the site

Fix:

1. Add entrance, floor, gate, and landmark.
2. Add parking or loading bay notes.
3. Assign a person to meet responders.
4. Keep access notes current.

### Public sheet exposes medical data

Fix:

1. Run redaction.
2. Print the public sheet only.
3. Store the full profile in restricted storage.
4. Remove old public copies.

### AED location is stale

Fix:

1. Verify monthly.
2. Update the profile immediately after relocation.
3. Update printed sheets.
4. Inform staff during shift briefing.

### Medical notes are vague

Replace vague text with emergency-relevant facts:

- Allergy to penicillin.
- Uses prescribed adrenaline auto-injector.
- Cannot use stairs.
- Uses insulin.

Do not store broad diagnosis history on public or broadly shared sheets.

## CLI problems

### Command not found

Cause: Editable install was not run.

Fix:

```bash
pip install -e .
```

### Typer dependency missing

Cause: Development requirements were not installed.

Fix:

```bash
pip install -r requirements-dev.txt
```

### Profile id not found

Cause: The wrong store directory was used.

Fix: Use the same `--store-dir` for create, validate, wallet-card, and redact.

### File read error

Cause: Relative path was used from a different directory.

Fix: Use an absolute path or run from the package root.

## First-aid scenario problems

### Person is unconscious but breathing

Call 101, place in recovery position if safe, monitor breathing, and prepare the AED.

### Person has chest pain but wants to continue work

Call 101 and keep the person resting. Do not let business pressure decide.

### Child is injured and guardian is unavailable

Call 101 for urgent symptoms. Continue care under dispatcher guidance and document contact attempts.

### Violence or unsafe scene

Move to safety. Call 100. Call 101 for injury when safe.

### Tourist has a medical bracelet

Call 101 for red flags. Use bracelet, wallet card, or phone medical ID only when it does not delay care.

## Maintenance problems

### Old sheets remain posted

Add version and review date to every sheet. Remove outdated copies during every review.

### First-aid kit expired

Replace expired items, record date, and assign a monthly owner.

### Volunteer responder number unverified

Remove from public sheet until local coverage and dispatch route are verified.
