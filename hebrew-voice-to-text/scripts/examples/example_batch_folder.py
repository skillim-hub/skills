"""Create local jobs for every supported file in a folder."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from hebrew_voice_to_text import HebrewVoiceTextClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("HVTT_ENV", "sandbox"))
    parser.add_argument("--folder", default=os.getenv("HVTT_INPUT_FOLDER", "."))
    parser.add_argument("--jobs-dir", default=os.getenv("HVTT_JOBS_DIR", ".hvt-jobs"))
    args = parser.parse_args()

    client = HebrewVoiceTextClient(env=args.env)
    folder = Path(args.folder)
    suffixes = {".txt", ".json", ".wav", ".mp3", ".m4a", ".ogg", ".opus", ".amr"}
    jobs = []
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.suffix.lower() in suffixes:
            job = client.create_job(path, jobs_dir=args.jobs_dir)
            jobs.append(job.to_dict())

    print(json.dumps({"env": args.env, "jobs": jobs, "count": len(jobs)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
