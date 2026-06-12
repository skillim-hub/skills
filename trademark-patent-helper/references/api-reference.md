# Israeli official-source and structured helper reference

## Scope

The Israel Patent Office provides official online filing systems and databases, but ordinary trademark and patent applicants do not usually interact with a stable public JSON filing API. Treat this reference as the equivalent API/regulation guide for a non-API skill: official sources, legal anchors, workflow objects, request/response examples, validation rules, and error tables.

Verify current law, regulations, circulars, forms, fees, portal behavior, and deadlines on official sources before filing.

## Official Israeli and international sources

| Area | Source | Use |
|---|---|---|
| Authority | Israel Patent Office / רשות הפטנטים | Official filing, databases, notices, procedural guidance |
| Trademarks | Trade Marks Ordinance [New Version], 5732-1972 | Registrability, rights, infringement, opposition, cancellation |
| Trademarks | Trade Marks Regulations, 1940 and amendments | Procedure, forms, classification, formal requirements |
| Patents | Patents Law, 5727-1967 | Patentability, ownership, service inventions, examination, opposition, term |
| Patents | Patents Regulations (Office Practice, Procedure, Documents and Fees), 5728-1968 and amendments | Filing formalities, documents, fees, procedure |
| Designs | Designs Law, 5777-2017 | Product appearance protection; adjacent route |
| Classification | Nice Classification | Trademark goods/services classes |
| International marks | Madrid Protocol | International trademark route where available |
| International patents | Patent Cooperation Treaty (PCT) | International patent filing route |
| Priority | Paris Convention | Priority claims for trademarks and patents |
| Patent search | WIPO PATENTSCOPE, Espacenet, USPTO, Google Patents | Prior-art search |
| Trademark search | Israel trademark database | Israeli marks and status |

## Structured request objects

### Trademark request

```json
{
  "kind": "trademark",
  "applicant_name": "Example Ltd.",
  "applicant_type": "company",
  "country": "IL",
  "mark_text": "ZAVILO",
  "mark_type": "word",
  "language": "en",
  "meaning": "Invented word with no known meaning",
  "classes": [
    {"class_no": 25, "items": ["clothing", "shirts", "hats"]},
    {"class_no": 35, "items": ["online retail store services featuring clothing"]}
  ],
  "first_use": "not_used",
  "priority_claim": null,
  "known_similar_marks": [],
  "notes": "File word mark first; consider logo separately."
}
```

### Trademark response

```json
{
  "kind": "trademark",
  "risk_level": "green",
  "summary": "Trademark preparation for ZAVILO.",
  "issues": [],
  "issue_codes": [],
  "classes": [
    {"class_no": 25, "filing_text": "clothing; shirts; hats"},
    {"class_no": 35, "filing_text": "online retail store services featuring clothing"}
  ],
  "next_steps": [
    "Search identical, phonetic, Hebrew, English, and transliteration variants in the Israel trademark database.",
    "Verify current official forms, fees, and goods/services wording before filing.",
    "Save filing receipt, application number, and official correspondence."
  ],
  "warnings": [
    "Registration is not guaranteed and depends on examination and earlier rights."
  ]
}
```

### Patent request

```json
{
  "kind": "patent",
  "title": "Pressure-controlled irrigation valve",
  "applicant_name": "Example AgriTech Ltd.",
  "inventors": ["Dana Cohen", "Yossi Levi"],
  "technical_field": "Irrigation control",
  "problem": "Pressure spikes waste water and damage drip lines.",
  "solution": "A valve assembly uses a downstream pressure sensor and controllable restrictor.",
  "novel_features": [
    "zone-specific pressure threshold selection",
    "automatic restrictor adjustment based on downstream pressure"
  ],
  "public_disclosures": [],
  "prototype_status": "bench prototype",
  "commercial_countries": ["IL", "US", "EU"],
  "known_prior_art": []
}
```

### Patent response

```json
{
  "kind": "patent",
  "risk_level": "yellow",
  "summary": "Patent preparation for Pressure-controlled irrigation valve.",
  "issues": [],
  "issue_codes": [],
  "next_steps": [
    "Do not disclose publicly before filing strategy is confirmed.",
    "Prepare an invention disclosure with technical field, problem, solution, alternatives, drawings, and advantages.",
    "Run a prior-art search across patent databases and non-patent sources.",
    "Ask a patent attorney to review patentability and draft claims when commercial value matters.",
    "Verify current official filing requirements and fees before submission."
  ],
  "warnings": [
    "Patentability requires novelty, utility, and inventive step.",
    "This helper does not submit applications or replace professional drafting."
  ]
}
```

## CLI examples

Assess a trademark request:

```bash
python scripts/trademark-patent-helper-cli.py assess examples/sample-trademark.json --format json
```

Assess a patent request:

```bash
python scripts/trademark-patent-helper-cli.py assess examples/sample-patent.json --format markdown
```

Generate a template:

```bash
python scripts/trademark-patent-helper-cli.py template patent
```

Classify a description:

```bash
python scripts/trademark-patent-helper-cli.py intake "brand name for an online jewelry store" --format json
```

## Error and warning table

| Code | Situation | Meaning | Fix |
|---|---|---|---|
| MISSING_KIND | `kind` missing | Workflow cannot be selected | Use `trademark` or `patent`, or provide enough facts for intake |
| UNKNOWN_KIND | Unsupported `kind` | Asset is outside main scope | Use trademark/patent or route to design/copyright/legal workflow |
| MISSING_MARK | No mark text/logo description | Trademark cannot be assessed | Provide exact wording or logo description |
| MISSING_CLASSES | No goods/services | Classes cannot be selected | Add classes or plain-language goods/services |
| INVALID_CLASS | Class outside 1-45 | Nice class invalid | Use class 1 through 45 |
| DESCRIPTIVE_MARK | Mark appears descriptive | Registrability risk | Choose distinctive mark or prepare evidence |
| BROAD_CLASSES | Many unrelated classes | Cost/vulnerability risk | Limit to real goods/services |
| REGULATED_FIELD | Sensitive field detected | Extra legal restrictions may apply | Check sector-specific law before filing/marketing |
| MISSING_TITLE | Patent lacks title | Invention record incomplete | Add concise technical title |
| MISSING_TECHNICAL_DETAIL | Patent lacks implementation | Idea may be underdeveloped | Add components, steps, architecture, parameters |
| NO_NOVEL_FEATURES | No novelty statement | Inventive concept unclear | List concrete differences from known solutions |
| PUBLIC_DISCLOSURE | Public disclosure reported | Novelty risk | Build timeline and seek professional review |
| OWNERSHIP_RISK | Employee/contractor/founder/university facts | Applicant may not own rights | Review agreements and assignments |
| BUSINESS_METHOD_RISK | Commercial method without technical detail | Patentability concern | Identify technical problem/effect |
| DATE_FORMAT | Date ambiguous | Localization issue | Use DD/MM/YYYY for Hebrew-local records |
| FILE_UPLOAD | Portal rejects file | File/session problem | Check format, size, filename, encryption, session |

## Official-procedure checklist

### Trademarks

- Confirm sign is capable of distinguishing goods/services.
- Confirm applicant owns or is entitled to file the mark.
- Confirm goods/services match Nice Classification.
- Check absolute grounds: descriptive, generic, misleading, official symbols, public policy.
- Check relative grounds: confusing similarity to earlier marks.
- Prepare translation and transliteration.
- Prepare priority document if claiming priority.
- Track publication, opposition, office actions, registration, renewals, and use evidence.

### Patents

- Confirm invention is technical, useful, new, and non-obvious.
- Confirm no harmful public disclosure occurred.
- Confirm inventors and applicant/assignee.
- Check employee, contractor, university, hospital, funding, and founder obligations.
- Prepare enabling disclosure with drawings and alternatives.
- Draft claims supported by the specification.
- Consider Paris Convention and PCT deadlines for international strategy.
- Track examination, office actions, acceptance, opposition, grant, renewals, and foreign deadlines.
