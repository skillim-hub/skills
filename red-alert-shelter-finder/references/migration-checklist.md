# Migration Checklist

Use this checklist when replacing an older alert/shelter skill, migrating from ad-hoc scripts, or moving a prototype into production.

## 1. Inventory current behavior

- Identify the current alert endpoint and headers.
- Identify the shelter dataset source.
- List supported localities and aliases.
- List polling intervals.
- List stored user data.
- List notification channels.
- List Hebrew and English message templates.

## 2. Remove disallowed package elements

- Remove creator metadata.
- Remove visual marks and image references.
- Remove distribution callouts.
- Remove nonessential organization names.
- Use neutral imperative voice.
- Update license to “the required neutral copyright holder

## 3. Replace parsing

- Parse empty list as valid no-active-alert result.
- Parse object payload with `data`.
- Parse callback-wrapped JSON.
- Treat malformed payload as unavailable.
- Add tests for every schema seen in production.

## 4. Replace locality matching

- Add Unicode normalization.
- Add Hebrew punctuation normalization.
- Add alias table.
- Keep exact official area names.
- Do not expand regional councils without verified mapping.

## 5. Replace shelter lookup

- Convert shelter data to WGS84 latitude/longitude.
- Confirm GeoJSON order `[longitude, latitude]`.
- Add source timestamp.
- Add validation for Israel coordinate bounds.
- Mark opening status as unverified unless supplied by source.
- Keep a last-known-good local copy.

## 6. Replace user messages

- Active alert: action first.
- Inactive: no active alert found, with freshness caveat.
- Unavailable: data unavailable, with fallback safety guidance.
- Hebrew: natural professional terminology.
- Use DD/MM/YYYY and ₪ in Hebrew business outputs.

## 7. Replace operations

- Add monitoring for status code, latency, payload size, parse failures, and staleness.
- Add backoff.
- Add incident log.
- Add monthly drills.
- Add release scenario review.

## 8. Validate privacy

- Do not log precise location by default.
- Redact coordinates in debug output.
- Limit retention.
- Avoid storing home/workplace labels unless required.
- Review privacy obligations before production storage.

## 9. Run tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

Expected: all tests pass.

## 10. Cutover

- Deploy read-only first.
- Compare old and new results where practical.
- Enable notifications only after no false inactive states are observed.
- Keep rollback instructions.
- Record final release date in `CHANGELOG.md`.
