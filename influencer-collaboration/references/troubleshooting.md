# Troubleshooting

Use this guide when scoring, outreach, approval, tracking, or reporting produces unexpected results.

## Scoring issues

| Symptom | Likely cause | Correction |
|---|---|---|
| A large creator receives a low score | Low Israeli audience share, weak niche match, or poor engagement | Inspect score components and request audience proof |
| A small creator receives a high score | Strong local fit and healthy engagement | Keep in shortlist when campaign is local |
| Budget score is unexpectedly low | Estimated fee exceeds campaign budget | Reduce deliverables, shorten usage rights, or increase budget |
| Engagement score is too high for a giveaway post | Imported averages include giveaways or viral outliers | Recalculate using comparable posts only |
| Risk score is low | Brand conflicts or suspicious metric ratios | Move to manual review and request analytics screenshots |
| Ranking changes after adding deliverables | Fee estimate increased | Separate mandatory deliverables from optional add-ons |

## CSV import issues

| Error | Cause | Fix |
|---|---|---|
| Missing `handle` | CSV header is absent or misspelled | Use the documented header names |
| Invalid platform | Platform value is outside allowed list | Use instagram, tiktok, youtube, facebook, linkedin, blog, or other |
| Percent values too large | Imported 91 instead of 0.91 | Divide by 100 |
| Hebrew text appears broken | File encoding is not UTF-8 | Export as UTF-8 or UTF-8 with BOM |
| Empty rows become profiles | Spreadsheet has trailing rows | Delete blank rows before export |
| Conflicts do not parse | Separator differs | Use a pipe between conflicts |

## Outreach issues

| Symptom | Likely cause | Correction |
|---|---|---|
| Creator ignores the message | Request is too generic or budget is missing | Add objective, dates, deliverables, and budget range |
| Creator replies with only a price | Data request was not explicit | Ask for recent audience data and example reports |
| Negotiation becomes unclear | Payment, product, usage, and exclusivity are mixed | Split each topic into a separate line |
| Creator refuses disclosure | Terms are not aligned | Do not proceed without clear commercial disclosure |
| Creator requests full prepayment | Payment risk is high | Use milestone payment or partial payment after approval |
| Creator wants broad usage rights | Scope is expensive | Limit duration, placement, and paid media use |

## Hebrew wording issues

| Symptom | Likely cause | Correction |
|---|---|---|
| Message sounds too formal | Corporate wording for a creator relationship | Use concise, respectful, direct wording |
| Message sounds too casual | Missing business details | Add objective, dates, and deliverables |
| Disclosure line is vague | Uses only `תודה ל` or `קיבלתי מ` | Use clear wording such as `פרסומת` or `בשיתוף` |
| Date format is confusing | Mixed formats | Use DD/MM/YYYY |
| Budget wording is unclear | Does not state whether tax is included | State `לפני מע"מ ככל שרלוונטי` or confirm status separately |

## Campaign tracking issues

| Symptom | Likely cause | Correction |
|---|---|---|
| Coupon cannot attribute sales | Same code used by all creators | Generate one code per creator |
| Clicks do not appear | Link sticker or link parameter missing | Test link before publication |
| Story data lost | Screenshot not saved before expiry | Add a reporting deadline before expiry |
| Sales data does not match platform clicks | Attribution window differs | Define measurement window in advance |
| Leads duplicated | Same person submits more than once | Deduplicate by phone or email where lawful |
| Revenue not recorded | Point-of-sale or booking system lacks source field | Add coupon or source field before launch |

## Performance interpretation issues

| Result | Interpretation | Next action |
|---|---|---|
| High ROAS and high conversion | Strong commercial fit | Renew and negotiate defined content reuse |
| High reach and low clicks | Creative attracted attention but weak intent | Test clearer offer or different call to action |
| High clicks and low leads | Landing page mismatch | Adjust page, form length, or offer |
| Good leads and low sales | Sales follow-up issue | Review response time and call script |
| Low cost and poor brand fit | Cheap traffic does not equal value | Stop or reserve for awareness only |
| Strong comments and weak direct sales | Possible long consideration cycle | Retarget engaged users if permitted |

## CLI issues

| Symptom | Cause | Fix |
|---|---|---|
| Command not found | Package not installed editable | Run `pip install -e .` from the project root |
| Import fails | Running script before installation | Install the package or run inside the project environment |
| Typer error on arguments | Missing required file path | Provide profile, brief, or CSV path as shown in README |
| Output escapes Hebrew | Custom wrapper changed JSON settings | Use `json.dumps(..., ensure_ascii=False, indent=2)` |

## Testing issues

| Symptom | Cause | Fix |
|---|---|---|
| Async tests fail | `pytest-asyncio` missing | Run `pip install -r requirements-dev.txt` |
| Compile check fails | Syntax issue in a script | Run `python -m compileall scripts/ -q` and inspect the file |
| Example cannot import module | Editable install not active | Run `pip install -e .` |
| Date parsing fails | Wrong format | Use ISO `YYYY-MM-DD` or local `DD/MM/YYYY` where documented |

## Escalation checklist

Escalate to a qualified professional when any of these apply:

- The campaign collects personal details from leads at scale.
- The content includes health, finance, legal, insurance, credit, minors, alcohol, lotteries, or professional claims.
- The creator requests exclusivity or broad paid-media usage.
- Payment terms, VAT status, withholding, or invoice duties are unclear.
- A consumer may rely on a claim for safety, health, or financial decisions.
- A dispute appears likely over non-publication, late publication, missing disclosure, or unauthorized content use.
