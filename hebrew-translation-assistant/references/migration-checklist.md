# Migration checklist

Use this checklist when moving from a generic Hebrew translation prompt, older localization notes, or script-only helper to this package.

## Package structure

- Replace hyphenated Python implementation files with import-safe module files.
- Import from `hebrew_translation_assistant`.
- Use `pip install -e .` before running examples or tests.
- Keep compatibility scripts only as thin entries, not as the main implementation.
- Run `python -m compileall scripts/ -q`.

## Documentation

- Remove branding language, ownership fields, visual branding assets and image references.
- Use neutral imperative voice.
- Keep `LICENSE` with the neutral MIT copyright line.
- Use `₪` and `DD/MM/YYYY` throughout public documentation.
- Remove nikud from Hebrew technical prose.
- Replace generic translation advice with Israeli small-business, freelance, and consumer scenarios.

## Terminology

- Replace `invoice` transliteration with `חשבונית`.
- Replace `privacy policy` transliteration with `מדיניות פרטיות`.
- Replace `refund` transliteration with `החזר כספי`.
- Replace generic `tax` wording with `מע״מ`, `מס הכנסה`, `ניכוי מס במקור`, `חשבונית מס`, `עוסק מורשה`, and `עוסק פטור` according to context.
- Preserve product names, order numbers, URLs, email addresses, and coupon codes.

## Workflow

- Add a register decision step before translation.
- Add a legal/accounting/privacy/accessibility review flag when relevant.
- Add stored request workflows when repeatable CLI output is needed.
- Add scenario tests for idioms, dates, VAT, refunds, gender, and mixed text.

## Tests

- Test sync and async methods.
- Test package imports.
- Test CLI direct translation.
- Test CLI create and show chaining.
- Test glossary export and lookup.
- Test URL and email preservation.
- Test no-nikud validation.
- Test date conversion from `YYYY-MM-DD` to `DD/MM/YYYY`.

## Release checklist

1. Bump `metadata.json` and `pyproject.toml` versions together.
2. Add a Keep a Changelog entry.
3. Run branding audit.
4. Run Hebrew quality audit.
5. Run `pytest`.
6. Run `python -m compileall scripts/ -q`.
7. Bundle the package as a zip.
