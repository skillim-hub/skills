from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from red_alert_shelter_finder import (
    Alert,
    AlertParseError,
    RedAlertShelterFinderClient,
    Shelter,
    ShelterDataError,
    WatchError,
    haversine_m,
    normalize_area,
    validate_coordinates,
)


def make_client(payload="[]"):
    def transport(url, timeout, headers):
        return payload

    return RedAlertShelterFinderClient(transport=transport, now_provider=lambda: "2026-06-04T12:00:00+03:00")


def test_parse_empty_list():
    assert make_client().parse_alert_payload([]) == []


def test_parse_empty_object_data():
    assert make_client().parse_alert_payload({"id": "", "data": []}) == []


def test_parse_active_dict():
    alerts = make_client().parse_alert_payload({"id": "1", "cat": "1", "title": "ירי רקטות וטילים", "data": ["חיפה"]})
    assert len(alerts) == 1
    assert alerts[0].areas == ("חיפה",)
    assert alerts[0].message_id == "1"


def test_parse_comma_separated_data():
    alerts = make_client().parse_alert_payload({"data": "חיפה, קריית אתא"})
    assert alerts[0].areas == ("חיפה", "קריית אתא")


def test_parse_json_text():
    alerts = make_client().parse_alert_payload('{"id":"2","data":["אשדוד"]}')
    assert alerts[0].areas == ("אשדוד",)


def test_parse_jsonp_text():
    alerts = make_client().parse_alert_payload('callback({"id":"3","data":["רמת גן"]});')
    assert alerts[0].message_id == "3"
    assert alerts[0].areas == ("רמת גן",)


def test_parse_list_of_dicts():
    alerts = make_client().parse_alert_payload([{"id": "1", "data": ["חיפה"]}, {"id": "2", "data": ["אשדוד"]}])
    assert [a.message_id for a in alerts] == ["1", "2"]


def test_parse_list_of_strings():
    alerts = make_client().parse_alert_payload(["חיפה", "אשדוד"])
    assert alerts[0].areas == ("חיפה", "אשדוד")


def test_parse_invalid_json_raises():
    with pytest.raises(AlertParseError):
        make_client().parse_alert_payload("<html>blocked</html>")


def test_normalize_spaces_and_dash():
    assert normalize_area("  תל אביב–יפו  ") == "תל אביב - יפו"


def test_alias_area_match_hebrew():
    c = make_client()
    alerts = c.parse_alert_payload({"data": ["תל אביב - יפו"]})
    assert c.area_in_alerts("תא", alerts) is True


def test_alias_area_match_english():
    c = make_client()
    alerts = c.parse_alert_payload({"data": ["תל אביב - יפו"]})
    assert c.area_in_alerts("tel aviv", alerts) is True


def test_area_no_match():
    c = make_client()
    alerts = c.parse_alert_payload({"data": ["חיפה"]})
    assert c.area_in_alerts("אשדוד", alerts) is False


def test_haversine_zero():
    assert haversine_m(32.0, 34.8, 32.0, 34.8) == pytest.approx(0.0)


def test_haversine_tel_aviv_jerusalem_distance():
    distance = haversine_m(32.0853, 34.7818, 31.7683, 35.2137)
    assert 45_000 < distance < 70_000


def test_shelter_from_mapping():
    s = Shelter.from_mapping({"name": "A", "latitude": "32.07", "longitude": "34.78", "address": "Herzl"})
    assert s.name == "A"
    assert s.address == "Herzl"


def test_shelter_missing_coordinate_raises():
    with pytest.raises(ShelterDataError):
        Shelter.from_mapping({"name": "A", "latitude": "32.07"})


def test_validate_reversed_coordinates_rejected():
    with pytest.raises(ShelterDataError):
        validate_coordinates(34.78, 32.07)


def test_nearest_shelters_sorted():
    c = make_client()
    shelters = [Shelter("Far", 32.09, 34.80), Shelter("Near", 32.071, 34.781)]
    result = c.nearest_shelters(32.07, 34.78, shelters, limit=2)
    assert [s.name for s in result] == ["Near", "Far"]


def test_nearest_shelters_max_distance():
    c = make_client()
    shelters = [Shelter("Near", 32.071, 34.781), Shelter("Far", 33.0, 35.0)]
    result = c.nearest_shelters(32.07, 34.78, shelters, limit=5, max_distance_m=500)
    assert [s.name for s in result] == ["Near"]


def test_nearest_limit_must_be_positive():
    with pytest.raises(ShelterDataError):
        make_client().nearest_shelters(32.07, 34.78, [], limit=0)


def test_load_csv_shelters():
    csv_text = "name,address,city,latitude,longitude\nמקלט 1,הרצל 1,תל אביב - יפו,32.07,34.78\n"
    shelters = make_client().load_shelters_text(csv_text, format_hint="csv")
    assert len(shelters) == 1
    assert shelters[0].city == "תל אביב - יפו"


def test_load_json_shelters():
    text = json.dumps([{"name": "מקלט 1", "latitude": 32.07, "longitude": 34.78}], ensure_ascii=False)
    shelters = make_client().load_shelters_text(text, format_hint="json")
    assert shelters[0].name == "מקלט 1"


def test_load_geojson_shelters():
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [34.78, 32.07]},
                "properties": {"name": "מקלט גאו", "address": "דוגמה 1"},
            }
        ],
    }
    shelters = make_client().load_shelters_payload(geojson)
    assert shelters[0].longitude == 34.78
    assert shelters[0].latitude == 32.07


def test_fetch_current_alerts_uses_transport():
    alerts = make_client('{"id":"9","data":["חיפה"]}').fetch_current_alerts()
    assert alerts[0].message_id == "9"


def test_status_for_area_active():
    c = make_client()
    alerts = c.parse_alert_payload({"id": "1", "data": ["חיפה"]})
    status = c.status_for_area("חיפה", alerts)
    assert status["active"] is True
    assert status["alerts"][0]["message_id"] == "1"


def test_status_for_area_inactive():
    status = make_client().status_for_area("חיפה", [])
    assert status["active"] is False
    assert status["alerts"] == []


def test_action_steps_active_business_outside():
    steps = make_client().action_steps(active=True, outside=True, business=True)
    assert any("protected space" in step for step in steps)
    assert any("dispatch" in step for step in steps)


def test_action_steps_inactive_business():
    steps = make_client().action_steps(active=False, business=True)
    assert any("shift procedure" in step for step in steps)


def test_alert_to_dict_areas_are_list():
    alert = Alert(message_id="1", title="t", areas=("a",))
    assert alert.to_dict()["areas"] == ["a"]


def test_shelter_to_dict_distance_rounded():
    shelter = Shelter("A", 32.07, 34.78, distance_m=123.456)
    assert shelter.to_dict()["distance_m"] == 123.5


@pytest.mark.asyncio
async def test_async_fetch_current_alerts_with_async_transport():
    async def async_transport(url, timeout, headers):
        return '{"id":"10","data":["אשדוד"]}'

    c = RedAlertShelterFinderClient(async_transport=async_transport)
    alerts = await c.fetch_current_alerts_async()
    assert alerts[0].areas == ("אשדוד",)


def test_async_fetch_current_alerts_falls_back_to_thread():
    def transport(url, timeout, headers):
        return '{"id":"11","data":["רמת גן"]}'

    c = RedAlertShelterFinderClient(transport=transport)
    alerts = asyncio.run(c.fetch_current_alerts_async())
    assert alerts[0].message_id == "11"


def test_create_watch_is_deterministic():
    c = make_client()
    first = c.create_watch("תא", environment="sandbox")
    second = c.create_watch("תל אביב - יפו", environment="sandbox")
    assert first.watch_id == second.watch_id
    assert first.canonical_area == "תל אביב - יפו"


def test_create_watch_rejects_environment():
    with pytest.raises(WatchError):
        make_client().create_watch("חיפה", environment="qa")


def test_save_load_and_check_watch(tmp_path):
    c = make_client()
    watch = c.create_watch("חיפה", environment="sandbox")
    path = tmp_path / "watch.json"
    c.save_watch(watch, path)
    loaded = c.load_watch(path, watch.watch_id)
    status = c.check_watch(loaded, c.parse_alert_payload({"data": ["חיפה"]}))
    assert status["watch_id"] == watch.watch_id
    assert status["active"] is True


def test_load_watch_rejects_wrong_id(tmp_path):
    c = make_client()
    watch = c.create_watch("חיפה", environment="sandbox")
    path = tmp_path / "watch.json"
    c.save_watch(watch, path)
    with pytest.raises(WatchError):
        c.load_watch(path, "watch_wrong")


def test_package_import_exposes_client():
    import red_alert_shelter_finder as pkg

    assert hasattr(pkg, "RedAlertShelterFinderClient")
