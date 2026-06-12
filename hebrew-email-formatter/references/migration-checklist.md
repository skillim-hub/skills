# Migration Checklist

Use this checklist when replacing older prompts or scripts with this neutral Hebrew formatting skill.

## Scope

- [ ] Treat the skill as a drafting and formatting layer.
- [ ] Require user review before sending.
- [ ] Keep delivery channels and attachments outside the formatter unless handled by a separate secure tool.
- [ ] Remove branding, visual assets, creator metadata, and distribution callouts.

## File and import changes

- [ ] Remove any hyphenated client script.
- [ ] Use `hebrew_email_formatter` as the installable package.
- [ ] Use `scripts/hebrew_email_formatter_client.py` for the structured helper.
- [ ] Use `hebrew-email-formatter` as the installed command name.
- [ ] Update examples to import from `hebrew_email_formatter`.

## Documentation

- [ ] Use `DD/MM/YYYY` in all examples.
- [ ] Use `₪` for Israeli amounts.
- [ ] Add review notes for missing VAT status.
- [ ] Avoid slash-heavy gender forms.
- [ ] Remove unnecessary personal data.
- [ ] Avoid legal and tax conclusions unless supplied.

## Validation

- [ ] Run `python -m pytest scripts/test_hebrew_email_formatter_client.py -q`.
- [ ] Run `python -m compileall scripts/ -q`.
- [ ] Run at least two example scripts with `--env sandbox`.
- [ ] Confirm no public Markdown emoji remain.
- [ ] Confirm no visual asset links remain.
