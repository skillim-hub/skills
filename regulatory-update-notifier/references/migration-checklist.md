# Migration Checklist

## From a hyphenated script layout to the installable package

- Delete imports that load a Python file with a hyphenated name.
- Use `from regulatory_update_notifier import ...`.
- Install locally with `pip install -e .`.
- Keep CLI invocation through `python -m regulatory_update_notifier.cli` or the project entry point.
- Keep `scripts/regulatory_update_notifier_client.py` only as the underscored script implementation mirror.
- Do not reintroduce a hyphenated client module.

## README and setup

- Replace `pip install -e ".[dev]"` with:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

- Ensure `pytest-asyncio` appears in development requirements.
- Run both test and syntax checks:

```bash
pytest -q
python -m compileall scripts/ -q
```

## Configuration migration

Old profile fields:

```json
{
  "industry": "ecommerce",
  "keywords": "cancellation"
}
```

New profile fields:

```json
{
  "id": "stable-id",
  "name": "Online shop",
  "industries": ["ecommerce"],
  "keywords": ["cancellation"],
  "locale": "he",
  "environment": "sandbox"
}
```

## CLI migration

Old scan:

```bash
python scripts/regulatory-update-notifier-cli.py scan --industry ecommerce --keyword cancellation
```

Preferred scan:

```bash
python -m regulatory_update_notifier.cli scan --profile profile.json --profile-id "$PROFILE_ID" --env sandbox
```

## Localization migration

- Convert Hebrew prose dates to `DD/MM/YYYY`.
- Keep `₪` for amounts.
- Replace freelancer with עצמאי in Hebrew prose.
- Replace ecommerce with מסחר מקוון in Hebrew prose.
- Remove ניקוד from technical prose.

## Verification checklist

- No hyphenated client module remains.
- Package import works from a clean environment.
- CLI can create a profile, extract its id, and use the id in scan.
- Examples accept `--env sandbox` and `--env production`.
- Examples read environment variables for profile, keywords, locale, and output paths.
- Public Markdown contains no emoji, logos, badges, banners, or attribution callouts.
- License uses the approved neutral copyright holder.


## v2.2.0 web-validated source migration

- Add the Government Legislation Site to public-consultation monitors.
- Add a second-pass validation step for tax rates, thresholds, fees, percentages, official forms, and endpoint paths.
- Remove hard-coded example thresholds from public summaries unless the active official source contains the value.
- Treat Knesset OData maintenance or geo-block HTML as an availability issue, not as an empty result.
- Record access date and short source quote for every production regulatory claim.
