#!/usr/bin/env python3
"""Example: run the CLI nearest command with bundled sample data."""

from pathlib import Path
import subprocess
import sys

base = Path(__file__).resolve().parents[1]
cli = base / "red-alert-shelter-finder-cli.py"
shelters = Path(__file__).with_name("sample_shelters.csv")
result = subprocess.run(
    [sys.executable, str(cli), "nearest", "--lat", "32.074", "--lon", "34.779", "--shelters", str(shelters), "--limit", "2"],
    text=True,
    capture_output=True,
    check=True,
)
print(result.stdout)
