# Workflow Guide

Use these workflows to deliver consistent alert and shelter assistance.

## Workflow 1: Consumer asks whether a locality has an active alert

Input:

```text
יש עכשיו התרעה בחיפה?
```

Steps:

1. Normalize the locality name.
2. Fetch the current alert payload.
3. Parse the payload into alert objects.
4. Match the normalized locality against alert areas.
5. Return active, inactive, or unavailable.
6. Add immediate safety guidance.

Inactive template:

```text
לא נמצאה התרעה פעילה עבור חיפה בנתונים הנוכחיים. התרעות עשויות להשתנות בתוך שניות. השאירו התראות פעילות והישארו קרובים למרחב מוגן.
```

Active template:

```text
נמצאה התרעה פעילה עבור חיפה. היכנסו עכשיו למרחב המוגן הקרוב והישארו בו עד לקבלת הנחיה רשמית לצאת.
```

Unavailable template:

```text
נתוני ההתרעות אינם זמינים כרגע. אם נשמעת אזעקה או מתקבלת הנחיה רשמית, היכנסו מיד למרחב המוגן הקרוב.
```

## Workflow 2: Person outside asks for nearest public shelter

Input:

```text
I am at 32.074, 34.779. Find shelters near me.
```

Steps:

1. Validate coordinates.
2. Load a shelter dataset.
3. Calculate Haversine distance to each shelter.
4. Sort by distance and name.
5. Return the nearest 3–5 shelters.
6. Warn not to travel during an active alarm if a closer protected space is available.

Output:

```text
Nearest public shelters:
1. מקלט ציבורי 12 — הרצל 10, תל אביב - יפו — about 145 m
2. מקלט ציבורי 13 — דיזנגוף 50, תל אביב - יפו — about 480 m

If an alarm is sounding now, enter the closest protected space immediately; do not walk to a farther shelter.
```

## Workflow 3: Small store during business hours

Input:

```text
Create a red-alert procedure for a 6-person grocery in Ashdod.
```

Steps:

1. Identify customer-facing risk.
2. Define roles:
   - Shift lead: announces movement to protected space.
   - Floor worker: guides customers.
   - Cashier: stops checkout and leaves register.
   - Back-room worker: checks storage and service areas.
3. Define movement path and fallback protected space.
4. Define post-event headcount.
5. Define customer communication.
6. Define drill schedule and documentation.

Procedure:

```text
When an alert is received:
1. Stop checkout immediately.
2. Tell customers: “היכנסו עכשיו למרחב המוגן הקרוב. השאירו עגלות במקום.”
3. Guide customers through the marked route.
4. Do not lock the entrance while people are moving.
5. Keep everyone inside until official guidance permits exit.
6. After exit, count staff, check customers, document the event time, and resume only after the shift lead approves.
```

## Workflow 4: Delivery business

Steps:

1. Add dispatch city and delivery zones to the locality watch list.
2. Pause dispatch on active alert.
3. Send rider instruction:
   - Stop safely.
   - Enter closest protected space.
   - Do not continue delivery during the waiting period.
   - Confirm status after exit.
4. Send customer delay message.
5. Resume dispatch after riders check in.

Customer message:

```text
בשל התרעה באזור, המשלוח נעצר זמנית לפי הנחיות הבטיחות. זמן ההגעה יתעדכן לאחר חזרת השליח לפעילות. תודה על ההבנה.
```

## Workflow 5: Clinic or service provider

Steps:

1. Map patients, staff, treatment rooms, and protected-space capacity.
2. Define safe stop points for procedures.
3. Assign assistance for patients with mobility needs.
4. Keep emergency kit and essential medication accessible.
5. Pause non-urgent treatment during alert.
6. Record event in operational log, not medical notes unless clinically relevant.

## Workflow 6: Office display or kiosk

Steps:

1. Configure a short timeout.
2. Poll according to the approved source policy.
3. Display active alert in large text.
4. Show protected-space instructions first.
5. Show shelter map only when it does not encourage unsafe travel.
6. Display last-updated timestamp.
7. If feed fails, display `נתוני התרעה אינם זמינים` and fallback guidance.

## Workflow 7: Developer integration

Install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e . -r requirements-dev.txt
```

Check alert feed:

```bash
python scripts/red_alert_shelter_finder_cli.py alerts --area "תל אביב"
```

Find nearest shelter:

```bash
python scripts/red_alert_shelter_finder_cli.py nearest --lat 32.074 --lon 34.779 --shelters data/shelters.csv
```

Run tests:

```bash
pytest -q
```

## Workflow 8: Incident log

| Field | Example |
|---|---|
| Date | 04/06/2026 |
| Time | 14:32 |
| Locality | אשדוד |
| Source | Alert feed |
| Status | Active alert |
| Action | Staff and customers entered protected space |
| Issues | Back-room door blocked |
| Follow-up | Clear route; repeat drill |

Avoid storing exact customer locations or personal details.


## Workflow 9: create and check a saved watch

Create a watch record, extract the `watch_id`, and check it in the next step.

```bash
CREATE_RESPONSE=$(red-alert-shelter-finder create-watch --env sandbox --area "חיפה" --output .watch-haifa.json)
WATCH_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["watch_id"])' <<< "$CREATE_RESPONSE")
red-alert-shelter-finder check-watch --env sandbox --watch-id "$WATCH_ID" --watch-file .watch-haifa.json
```

Expected create response:

```json
{
  "watch_id": "watch_...",
  "area": "חיפה",
  "canonical_area": "חיפה",
  "environment": "sandbox",
  "created_at": "2026-06-04T12:00:00+03:00"
}
```
