from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from .client import Candidate, RecruitmentAssistantClient, RoleProfile


app = typer.Typer(help="Screen resumes, validate job ads, and schedule interviews for Israeli hiring workflows.")


def _client(env: str) -> RecruitmentAssistantClient:
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    return RecruitmentAssistantClient(env=env)  # local helper, no network call


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _print_json(payload: object) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command()
def screen(
    resume: Annotated[Path, typer.Option("--resume", exists=True, readable=True, help="Resume text file.")],
    role: Annotated[Path, typer.Option("--role", exists=True, readable=True, help="Role profile JSON file.")],
    name: Annotated[str, typer.Option("--name", help="Candidate display name.")] = "Candidate",
    env: Annotated[str, typer.Option("--env", help="sandbox or production.")] = "sandbox",
) -> None:
    role_payload = _load_json(role)
    role_profile = RoleProfile(**role_payload)
    candidate = Candidate(name=name, resume_text=_load_text(resume))
    result = _client(env).screen_resume(candidate, role_profile)
    _print_json(result.to_dict())


@app.command()
def batch(
    candidates: Annotated[Path, typer.Option("--candidates", exists=True, readable=True, help="Candidate JSON array.")],
    role: Annotated[Path, typer.Option("--role", exists=True, readable=True, help="Role profile JSON file.")],
    env: Annotated[str, typer.Option("--env", help="sandbox or production.")] = "sandbox",
) -> None:
    role_profile = RoleProfile(**_load_json(role))
    items = json.loads(candidates.read_text(encoding="utf-8"))
    candidate_items = [Candidate(**item) for item in items]
    results = _client(env).rank_candidates(candidate_items, role_profile)
    _print_json([result.to_dict() for result in results])


@app.command("validate-ad")
def validate_ad(
    input_file: Annotated[Path, typer.Option("--input", exists=True, readable=True, help="Job ad text file.")],
    env: Annotated[str, typer.Option("--env", help="sandbox or production.")] = "sandbox",
) -> None:
    result = _client(env).validate_job_ad(_load_text(input_file))
    _print_json(result.to_dict())


@app.command()
def schedule(
    shortlist: Annotated[Path, typer.Option("--shortlist", exists=True, readable=True, help="Screening results JSON array.")],
    start_date: Annotated[str, typer.Option("--start-date", help="Start date in YYYY-MM-DD.")],
    env: Annotated[str, typer.Option("--env", help="sandbox or production.")] = "sandbox",
    minutes: Annotated[int, typer.Option("--minutes", help="Interview duration in minutes.")] = 45,
    channel: Annotated[str, typer.Option("--channel", help="phone, video, or onsite.")] = "video",
) -> None:
    from .client import ScreeningResult

    payload = json.loads(shortlist.read_text(encoding="utf-8"))
    results = [ScreeningResult(**item) for item in payload]
    slots = _client(env).schedule_interviews(results, start_date=start_date, interview_minutes=minutes, channel=channel)  # type: ignore[arg-type]
    _print_json([slot.to_dict() for slot in slots])


@app.command()
def version() -> None:
    from . import __version__

    typer.echo(__version__)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
