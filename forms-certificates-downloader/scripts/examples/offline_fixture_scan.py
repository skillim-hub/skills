#!/usr/bin/env python3
"""Run discovery and version tracking against local offline fixtures."""
from pathlib import Path

from _common import build_parser, print_json
from forms_certificates_downloader import FormsCertificatesClient, PortalSource


def main() -> None:
    parser = build_parser("Run an offline fixture scan.")
    args = parser.parse_args()

    fixture_dir = Path(args.download_dir).resolve() / "offline-fixture"
    fixture_dir.mkdir(parents=True, exist_ok=True)

    pdf = fixture_dir / "tofes-1301.pdf"
    pdf.write_bytes(b"%PDF-1.4\nfixture form\n")

    portal = fixture_dir / "portal.html"
    portal.write_text('<a href="tofes-1301.pdf">טופס 1301 לשנת 2026</a>', encoding="utf-8")

    source = PortalSource(
        name="offline",
        authority="Offline Fixture Authority",
        index_url=portal.as_uri(),
        base_url=portal.as_uri(),
        tags=("fixture", "tax"),
    )

    client = FormsCertificatesClient(download_dir=fixture_dir / "downloads", registry=[source], env=args.env)
    records, changes = client.refresh_source("offline", query=args.query or "1301", max_results=args.limit)
    print_json({
        "env": args.env,
        "records": [record.to_dict() for record in records],
        "changes": [change.to_dict() for change in changes],
    })


if __name__ == "__main__":
    main()
