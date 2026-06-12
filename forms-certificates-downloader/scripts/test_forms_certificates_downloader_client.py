from __future__ import annotations

import asyncio
import csv
import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from forms_certificates_downloader import (
    DocumentRecord,
    DownloaderError,
    FormsCertificatesClient,
    PortalSource,
    SourceNotFoundError,
    default_registry,
    detect_document_type,
    extract_version_hint,
    load_registry,
    normalize_israeli_phone,
    parse_anchor_candidates,
    query_matches,
    sanitize_filename,
    save_registry,
    sha256_bytes,
    validate_mikud,
    validate_teudat_zehut,
)
from forms_certificates_downloader.cli import cli


@pytest.fixture()
def fixture_portal(tmp_path: Path):
    pdf = tmp_path / "tofes-1301-2026.pdf"
    pdf.write_bytes(b"%PDF-1.4\nfirst version\n")
    btl = tmp_path / "maternity-claim.pdf"
    btl.write_bytes(b"%PDF-1.4\nmaternity\n")
    docx = tmp_path / "instructions-2026.docx"
    docx.write_bytes(b"fake docx")
    html = tmp_path / "portal.html"
    html.write_text(
        """
        <html><body>
          <a href="tofes-1301-2026.pdf">טופס 1301 גרסה 2.1 לשנת 2026</a>
          <a href="maternity-claim.pdf">תביעה לדמי לידה</a>
          <a href="instructions-2026.docx">הנחיות 2026</a>
          <a href="/contact">צור קשר</a>
        </body></html>
        """,
        encoding="utf-8",
    )
    source = PortalSource(
        name="fixture",
        authority="Fixture Authority",
        index_url=html.resolve().as_uri(),
        base_url=html.resolve().as_uri(),
        tags=("tax", "forms"),
    )
    registry = tmp_path / "registry.json"
    save_registry(registry, [source])
    return {"tmp": tmp_path, "html": html, "pdf": pdf, "btl": btl, "docx": docx, "source": source, "registry": registry}


def make_client(tmp_path: Path, source: PortalSource) -> FormsCertificatesClient:
    return FormsCertificatesClient(download_dir=tmp_path / "downloads", registry=[source], timeout=5, env="sandbox")


def test_validate_teudat_zehut_valid():
    assert validate_teudat_zehut("123456782") is True


def test_validate_teudat_zehut_rejects_zeros():
    assert validate_teudat_zehut("000000000") is False


def test_validate_teudat_zehut_rejects_bad_check_digit():
    assert validate_teudat_zehut("123456780") is False


def test_phone_mobile_local():
    result = normalize_israeli_phone("052-1234567")
    assert result["valid"] is True
    assert result["type"] == "mobile"
    assert result["local"] == "052-1234567"


def test_phone_mobile_international():
    result = normalize_israeli_phone("+972521234567")
    assert result["valid"] is True
    assert result["local"] == "052-1234567"


def test_phone_landline():
    result = normalize_israeli_phone("03-1234567")
    assert result["valid"] is True
    assert result["type"] == "landline"


def test_phone_invalid():
    assert normalize_israeli_phone("071-1234567")["valid"] is False


def test_mikud_valid():
    assert validate_mikud("6100001") is True


def test_mikud_invalid():
    assert validate_mikud("61001") is False


def test_sanitize_filename_preserves_hebrew_and_removes_bad_chars():
    filename = sanitize_filename("טופס 1301 / 2026?", ".pdf")
    assert "טופס" in filename
    assert "/" not in filename
    assert "?" not in filename
    assert filename.endswith(".pdf")


def test_extract_version_hint_from_hebrew_date():
    assert extract_version_hint("טופס 1301 עודכן 02-06-2026") == "02-06-2026"


def test_extract_version_hint_from_year():
    assert extract_version_hint("טופס 1301 לשנת 2026") == "2026"


def test_detect_document_type_pdf():
    assert detect_document_type("https://example.gov.il/form.pdf") == "pdf"


def test_detect_document_type_spreadsheet():
    assert detect_document_type("https://example.gov.il/report.xlsx") == "spreadsheet"


def test_parse_anchor_candidates_finds_documents(fixture_portal):
    candidates = parse_anchor_candidates(fixture_portal["html"].read_text(encoding="utf-8"), fixture_portal["html"].as_uri())
    assert len(candidates) == 3
    assert candidates[0][0].startswith("טופס 1301")


def test_query_matches_hebrew_final_letters():
    assert query_matches("אישור מסמכים", "מסמכ") is True


def test_discover_filters_query(fixture_portal, tmp_path):
    client = make_client(tmp_path, fixture_portal["source"])
    records = client.discover("fixture", query="1301")
    assert len(records) == 1
    assert records[0].document_type == "pdf"
    assert records[0].version_hint == "2.1"


def test_discover_unknown_source_raises(fixture_portal, tmp_path):
    client = make_client(tmp_path, fixture_portal["source"])
    with pytest.raises(SourceNotFoundError):
        client.discover("missing")


def test_download_writes_checksum_and_path(fixture_portal, tmp_path):
    client = make_client(tmp_path, fixture_portal["source"])
    record = client.discover("fixture", query="1301")[0]
    downloaded = client.download(record)
    assert Path(downloaded.path or "").exists()
    assert downloaded.checksum_sha256 == sha256_bytes(fixture_portal["pdf"].read_bytes())
    assert downloaded.size_bytes == fixture_portal["pdf"].stat().st_size


def test_track_records_added_then_unchanged(fixture_portal, tmp_path):
    client = make_client(tmp_path, fixture_portal["source"])
    first = client.download(client.discover("fixture", query="1301")[0])
    changes = client.track_records([first])
    assert changes[0].status == "added"
    second = client.download(client.discover("fixture", query="1301")[0])
    changes = client.track_records([second])
    assert changes[0].status == "unchanged"


def test_track_records_updated_when_checksum_changes(fixture_portal, tmp_path):
    client = make_client(tmp_path, fixture_portal["source"])
    first = client.download(client.discover("fixture", query="1301")[0])
    assert client.track_records([first])[0].status == "added"
    fixture_portal["pdf"].write_bytes(b"%PDF-1.4\nsecond version\n")
    second = client.download(client.discover("fixture", query="1301")[0])
    assert client.track_records([second])[0].status == "updated"


def test_track_requires_downloaded_checksum(fixture_portal, tmp_path):
    client = make_client(tmp_path, fixture_portal["source"])
    record = client.discover("fixture", query="1301")[0]
    with pytest.raises(DownloaderError):
        client.track_records([record])


def test_refresh_source_downloads_and_tracks(fixture_portal, tmp_path):
    client = make_client(tmp_path, fixture_portal["source"])
    records, changes = client.refresh_source("fixture", query="1301")
    assert len(records) == 1
    assert changes[0].status == "added"


def test_async_discover_and_download(fixture_portal, tmp_path):
    async def run():
        client = make_client(tmp_path, fixture_portal["source"])
        records = await client.async_discover("fixture", query="לידה")
        downloaded = await client.async_download(records[0])
        return downloaded
    downloaded = asyncio.run(run())
    assert downloaded.path and Path(downloaded.path).exists()


def test_async_refresh_source(fixture_portal, tmp_path):
    async def run():
        client = make_client(tmp_path, fixture_portal["source"])
        return await client.async_refresh_source("fixture", query="1301")
    records, changes = asyncio.run(run())
    assert len(records) == 1
    assert changes[0].status == "added"


def test_find_manifest_records(fixture_portal, tmp_path):
    client = make_client(tmp_path, fixture_portal["source"])
    records, _ = client.refresh_source("fixture", query="1301")
    found = client.find_manifest_records("1301", authority="Fixture")
    assert found[0].document_url == records[0].document_url


def test_export_manifest_csv(fixture_portal, tmp_path):
    client = make_client(tmp_path, fixture_portal["source"])
    client.refresh_source("fixture", query="1301")
    output = client.export_manifest_csv(tmp_path / "register.csv")
    with output.open(encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    assert rows and rows[0]["title"].startswith("טופס")


def test_registry_roundtrip(fixture_portal, tmp_path):
    out = tmp_path / "out-registry.json"
    save_registry(out, [fixture_portal["source"]])
    loaded = load_registry(out)
    assert loaded[0].name == "fixture"
    assert loaded[0].tags == ("tax", "forms")


def test_default_registry_has_core_sources():
    names = {source.name for source in default_registry()}
    assert "tax-authority-public-forms" in names
    assert "bituach-leumi-forms" in names
    assert "bituach-leumi-certificates" in names


def test_create_and_run_download_request(fixture_portal, tmp_path):
    client = make_client(tmp_path, fixture_portal["source"])
    request = client.create_download_request("fixture", query="1301", limit=1, env="sandbox")
    assert len(request.request_id) == 32
    result = client.run_download_request(request.request_id)
    assert result["request_id"] == request.request_id
    assert len(result["downloaded"]) == 1
    assert result["changes"][0]["status"] == "added"


def test_invalid_environment_rejected(tmp_path):
    with pytest.raises(ValueError):
        FormsCertificatesClient(download_dir=tmp_path, env="demo")


def test_document_record_roundtrip_key_stable():
    record = DocumentRecord(
        authority="רשות המסים",
        title="טופס 1301",
        source_url="https://example.gov.il",
        document_url="https://example.gov.il/forms/1301.pdf",
        document_type="pdf",
    )
    data = record.to_dict()
    loaded = DocumentRecord.from_dict(data)
    assert loaded.key == record.key
    assert "1301.pdf" in loaded.key


def test_cli_list_sources_json(fixture_portal):
    runner = CliRunner()
    result = runner.invoke(cli, ["list-sources", "--env", "sandbox", "--download-dir", str(fixture_portal["tmp"] / "d"), "--registry", str(fixture_portal["registry"]), "--json-output"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload[0]["name"] == "fixture"


def test_cli_create_request_then_run_request(fixture_portal):
    runner = CliRunner()
    download_dir = fixture_portal["tmp"] / "cli-downloads"
    create = runner.invoke(
        cli,
        [
            "create-request",
            "fixture",
            "--query",
            "1301",
            "--limit",
            "1",
            "--env",
            "sandbox",
            "--download-dir",
            str(download_dir),
            "--registry",
            str(fixture_portal["registry"]),
            "--json-output",
        ],
    )
    assert create.exit_code == 0, create.output
    request_id = json.loads(create.output)["request_id"]
    run = runner.invoke(
        cli,
        [
            "run-request",
            request_id,
            "--env",
            "sandbox",
            "--download-dir",
            str(download_dir),
            "--registry",
            str(fixture_portal["registry"]),
            "--json-output",
        ],
    )
    assert run.exit_code == 0, run.output
    assert json.loads(run.output)["changes"][0]["status"] == "added"


def test_cli_validate_json():
    runner = CliRunner()
    result = runner.invoke(cli, ["validate", "tz", "123456782", "--json-output"])
    assert result.exit_code == 0
    assert json.loads(result.output)["valid"] is True


def test_default_registry_urls_are_web_validated():
    by_name = {source.name: source for source in default_registry()}
    assert by_name["tax-authority-gov-il"].index_url.endswith("/departments/israel_tax_authority")
    assert by_name["tax-authority-public-forms"].index_url.endswith("/topics/income_tax_israel_tax_authority")
    assert by_name["gov-il-services"].index_url == "https://www.gov.il/he/services"
    assert by_name["corporations-authority"].index_url.endswith("/departments/israeli_corporations_authority")


def test_default_registry_schema_contains_version_two_package_sources():
    names = [source.name for source in default_registry()]
    assert len(names) >= 6
    assert names.count("tax-authority-public-forms") == 1
