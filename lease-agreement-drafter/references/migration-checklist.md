# Migration Checklist

Use this checklist when moving from earlier package layouts to version 1.2.0.

## Python imports

Replace script-path imports with package imports:

```python
from lease_agreement_drafter import LeaseAgreementDrafterClient
```

Do not import from hyphenated script filenames. Hyphenated Python modules cannot be imported normally.

## CLI

Use the installed console command:

```bash
lease-agreement-drafter schema --env sandbox
```

Script wrappers remain available under `scripts/` with underscored filenames for direct execution.

## Installation

Use editable installation during development:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

## Examples

Run examples with an explicit environment:

```bash
python scripts/examples/apartment_standard.py --env sandbox
python scripts/examples/office_freelancer_vat.py --env production
```

Examples read `LEASE_DRAFTER_API_KEY` and print JSON with readable Hebrew.

## Tests

Run:

```bash
pytest -q
python -m compileall scripts/ -q
```

## Data format

- Keep dates as DD/MM/YYYY in public examples.
- Keep amounts as numeric ILS values in JSON and display as ₪ in Markdown.
- Keep `property_type` as `apartment` or `office`.
- Keep `language` as `he` or `en`.

## Removed layout

- Hyphenated client implementation file.
- Branding-sensitive metadata.
- Badge, brand image, and header image references.
- Public Markdown emoji.
