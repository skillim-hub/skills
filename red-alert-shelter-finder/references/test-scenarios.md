# Test Scenarios

Run these scenarios during development, release review, and after any API or dataset change.

| # | Scenario | Input | Expected result |
|---:|---|---|---|
| 1 | No active alerts | `[]` | Alert list is empty; status inactive, not unavailable |
| 2 | Empty object data | `{"data":[]}` | Alert list is empty |
| 3 | Active single locality | `{"data":["חיפה"]}` | חיפה matches active alert |
| 4 | Multiple localities | `["תל אביב - יפו","רמת גן"]` | Both areas parse |
| 5 | Comma-separated data | `"חיפה, קריית אתא"` | Areas split and trim |
| 6 | JSON text | valid JSON string | Payload parses |
| 7 | JSONP wrapper | `callback({...})` | Payload parses |
| 8 | Malformed JSON | `<html>blocked</html>` | Parse error; unavailable |
| 9 | HTTP 403 | blocked feed | Feed unavailable; no false inactive status |
| 10 | HTTP 429 | rate limit | Backoff recommended |
| 11 | Timeout | slow endpoint | Feed unavailable; fallback guidance |
| 12 | Hebrew alias | `תא` | Maps to תל אביב - יפו |
| 13 | English alias | `tel aviv` | Maps to תל אביב - יפו |
| 14 | Hyphen variant | `תל אביב–יפו` | Normalizes to official form |
| 15 | Niqqud present | Hebrew with vowel marks | Normalization removes niqqud |
| 16 | Regional council | council name | No automatic expansion |
| 17 | Valid coordinates | `32.074,34.779` | Nearest shelters sorted |
| 18 | Reversed coordinates | `34.779,32.074` | Validation warning or rejection |
| 19 | GeoJSON shelter | `[34.78,32.07]` | Correct lon/lat interpretation |
| 20 | CSV shelter | lat/lon columns | Records load |
| 21 | Missing shelter coordinate | no latitude | Parse error |
| 22 | Duplicate shelters | same name and point | Deduplication policy can apply |
| 23 | Max distance filter | 500 m | Far shelters excluded |
| 24 | Same distance | equal distance shelters | Sort by name after distance |
| 25 | Active alert plus shelter request | alarm sounding | Protected-space instruction first |
| 26 | Business with customers | grocery store | Staff/customer procedure returned |
| 27 | Delivery rider | rider in transit | Stop, shelter, check in |
| 28 | Clinic patient | procedure underway | Pause safely; assist mobility needs |
| 29 | Feed stale | last update too old | Status unavailable |
| 30 | CLI alerts command | `--area חיפה` | JSON status output |
| 31 | CLI nearest command | local CSV | JSON shelter list |
| 32 | Privacy log check | precise user location | Coordinates redacted unless enabled |

## Release gate

A release passes only when:
- Unit tests pass.
- At least 20 scenario rows are reviewed.
- Hebrew output is checked for natural Israeli professional terminology.
- The package contains no creator field, visual marks, image references, or distribution callouts.
- `metadata.json` version is bumped.
- `CHANGELOG.md` contains the release date.
