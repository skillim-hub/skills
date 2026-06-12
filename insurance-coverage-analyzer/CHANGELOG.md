# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog, and the project uses semantic versioning.


## [2.1.0] - 2026-06-02

### Added

- Added `references/verification-log.md` with two-pass web validation, source snippets, URLs, access date, and status summary.
- Added official-source posture sections to English and Hebrew guides.
- Added verified source matrix to the structured reference guide.

### Changed

- Bumped package metadata, Python package, and project version to 2.1.0.
- Replaced a placeholder government-looking URL with explicit manual portal and calculator guidance.
- Clarified that official public API endpoints and webhook event names were not confirmed for this workflow.
- Clarified that 90-day waiting-period values are scenario review thresholds unless policy wording states otherwise.
- Updated date guidance in reference materials to DD/MM/YYYY where user-facing localization applies.

### Web validation findings

| Check | Status | Pass 1 finding | Pass 2 finding |
|---|---|---|---|
| Current Israeli VAT rate | ✓✓ | 1.1.25 עלה המע"מ ל-18% | The 2025 current rate of VAT is 18%. |
| VAT effective-date interpretation | ✓✓ | מועד החיוב במס... יחול מע"מ בשיעור של 18% | החל מיום 01.01.2025 הוא עומד על 18% |
| Capital Market Authority role | ✓✓ | מופקדת על השירותים הפיננסיים בשווקי הביטוח, הפנסיה והגמל | פעילותם מפוקחת על ידי רשות שוק ההון, ביטוח וחיסכון |
| Har HaBituach purpose | ✓✓ | הוקם למען ציבור המבוטחים ללא כל תשלום | הגבירה את רמת ההזדהות בכניסה לאתר הר הביטוח |
| No official public Har HaBituach API for this skill | ✓✓ | האתר מאגד בתוכו מידע מכלל חברות הביטוח | מדריך לכניסת מבוטחים לאתר הר הביטוח |
| Licensed professional lookup | ✓✓ | איתור סוכני ביטוח... בעלי רישיון | איתור סוכני ביטוח, יועצים פנסיוניים... בעלי רישיון |
| Home insurance calculator | ✓✓ | מציג את תעריפי הביטוח של החברות הפועלות בענף | מחשבון ביטוח דירה, מחשבון ביטוח בריאות... מחשבון ביטוח חיים |
| Home standard policy | ✓✓ | הפוליסה התקנית הכלולה בהן | רשות שוק ההון... מעדכנת את פוליסת ביטוח הדירה |
| Home war or hostilities exclusion posture | ✓✓ | פוליסות ביטוח דירה... אינה כוללת כיסוי לנזקי מלחמה או פעולות איבה | ביטוח כללי |
| Home natural disaster and earthquake check | ✓✓ | ביטוח כנגד אסונות טבע כגון רעידות אדמה, שריפה, שיטפונות | נזק מרעידת אדמה נעשה באמצעות פוליסה תקנית |
| Health calculator | ✓✓ | מציג את תעריפי הביטוח של החברות הפועלות בענף | מחשבון ביטוח בריאות |
| Private health basic policy reform categories | ✓✓ | פוליסת השתלות... תרופות מחוץ לסל ופוליסת ניתוחים | פוליסת תרופות מחוץ לסל ופוליסת ניתוחים |
| Public health basket context | ✓✓ | זכאים לקבל... את מלוא השירותים הקבועים בסל שירותי הבריאות | כל תושב ישראלי מבוטח בביטוח בריאות |
| Supplementary health-plan terminology | ✓✓ | שירותי הביטוח המשלים ניתנים אך ורק לחברי הקופה | שירותי הבריאות הנוספים יכולים לכלול שלושה סוגי כיסוי |
| Life/risk calculator | ✓✓ | לסייע לציבור להשוות בין תעריפי ביטוח החיים | בביטוח חיים למשכנתה, סכום הביטוח ותקופת הביטוח נקבעים |
| Insurance Contract Law | ✓✓ | תוקף: תקף | חוזה ביטוח הוא חוזה בין מבטח לבין מבוטח |
| Supervision Law | ✓✓ | תוקן לאחרונה: 31/03/2026 | רשיון סוכן מתמחה |
| 90-day waiting-period threshold | ✗→✓ | 90-day waiting period | no official 90-day statutory threshold confirmed for this workflow |
| Placeholder endpoint path | ✗→✓ | placeholder government-looking endpoint | manual portal, no confirmed public API endpoint |
| Webhook event names | ✓✓ | no webhook references in source package | official insurance public pages are portal and guide oriented |

## [2.0.1] - 2026-06-02

### Added

- Added branding, author, logo, badge, and public Markdown emoji audit report.
- Added Hebrew QA log for terminology, style, localization, and niqqud checks.
- Added installable Python package under `insurance_coverage_analyzer`.
- Added persisted analysis workflow with `create` and `show` CLI commands.
- Added pytest-asyncio development dependency.

### Changed

- Replaced dynamic script imports with package imports.
- Moved client implementation to an underscored module path and deleted the hyphenated client file.
- Updated README installation to `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated quick start to extract an analysis identifier from the create response and use it in the next command.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print JSON with Hebrew-safe encoding.
- Updated Hebrew documentation to use professional Israeli terminology and DD/MM/YYYY localization.

### Fixed

- Removed public Markdown emoji and logo or badge references where present.
- Confirmed syntax with compileall and expanded the test suite.

## [2.0.0] - 2026-06-02

### Added

- Comprehensive English guide for Israeli health, home, and life policy-level analysis.
- Full Hebrew guide using Israeli professional terminology and ₪ / DD/MM/YYYY localization.
- Policy-level diff model with coverage, deductible, exclusion, waiting-period, and cost comparison.
- Israeli source and regulation reference with structured request and response examples.
- End-to-end workflow guide.
- Troubleshooting guide.
- 30 concrete test scenarios.
- Migration checklist.
- Typed sync and async local analyzer client.
- Typer CLI.
- Runnable examples.
- Pytest suite with at least 20 tests.
- Project packaging files.

### Changed

- Refocused from car-insurance comparison to health, home, and life coverage analysis.
- Renamed the package to `insurance-coverage-analyzer`.
- Expanded metadata tags and bilingual descriptions.
- Standardized neutral imperative documentation style.

### Removed

- Removed author metadata.
- Removed organization branding and distribution callouts.
- Removed logo, badge, and image references.
- Removed car-insurance-first workflow emphasis.
