"""Command line interface for Hebrew voice-to-text workflows."""

from __future__ import annotations

import json
import os
from pathlib import Path

import click

from hebrew_voice_to_text import HebrewVoiceTextClient


def _json(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--env",
    "environment",
    type=click.Choice(["sandbox", "production"]),
    default=lambda: os.getenv("HVTT_ENV", "sandbox"),
    show_default="HVTT_ENV or sandbox",
    help="Execution environment label.",
)
@click.version_option("2.2.0")
@click.pass_context
def main(ctx: click.Context, environment: str) -> None:
    """Transcribe and prepare Hebrew voice-to-text outputs."""
    ctx.obj = {"env": environment}


@main.command()
@click.argument("path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.pass_context
def inspect(ctx: click.Context, path: Path) -> None:
    """Inspect an audio file."""
    client = HebrewVoiceTextClient(env=ctx.obj["env"])
    info = client.inspect_audio(path)
    click.echo(_json({field: getattr(info, field) for field in info.__dataclass_fields__}))


@main.command()
@click.argument("text")
@click.option("--no-punctuation", is_flag=True, help="Do not add terminal punctuation.")
@click.pass_context
def normalize(ctx: click.Context, text: str, no_punctuation: bool) -> None:
    """Normalize Hebrew transcript text."""
    client = HebrewVoiceTextClient(env=ctx.obj["env"])
    click.echo(client.normalize_hebrew_text(text, add_punctuation=not no_punctuation))


@main.command()
@click.argument("text")
@click.pass_context
def redact(ctx: click.Context, text: str) -> None:
    """Redact common sensitive values from text."""
    client = HebrewVoiceTextClient(env=ctx.obj["env"])
    click.echo(client.redact_sensitive_text(text))


@main.command("create-job")
@click.argument("path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--jobs-dir", type=click.Path(file_okay=False, path_type=Path), default=Path(".hvt-jobs"), show_default=True)
@click.option("--expected-speakers", default=1, show_default=True)
@click.option("--speaker-labels/--no-speaker-labels", default=True, show_default=True)
@click.option("--sensitivity", default="medium", show_default=True)
@click.option("--output", "outputs", multiple=True, default=("txt", "json"), show_default=True)
@click.pass_context
def create_job(
    ctx: click.Context,
    path: Path,
    jobs_dir: Path,
    expected_speakers: int,
    speaker_labels: bool,
    sensitivity: str,
    outputs: tuple[str, ...],
) -> None:
    """Create a local provider-neutral transcription job."""
    client = HebrewVoiceTextClient(env=ctx.obj["env"])
    job = client.create_job(
        path,
        expected_speakers=expected_speakers,
        speaker_labels=speaker_labels,
        sensitivity=sensitivity,
        outputs=outputs,
        jobs_dir=jobs_dir,
    )
    job_file = jobs_dir / f"{job.id}.json"
    response = {
        "id": job.id,
        "env": job.env,
        "job_file": str(job_file),
        "next": f"show-job {job.id} --jobs-dir {jobs_dir}",
    }
    click.echo(_json(response))


@main.command("show-job")
@click.argument("job_id")
@click.option("--jobs-dir", type=click.Path(exists=True, file_okay=False, path_type=Path), default=Path(".hvt-jobs"), show_default=True)
@click.pass_context
def show_job(ctx: click.Context, job_id: str, jobs_dir: Path) -> None:
    """Print a persisted job request."""
    client = HebrewVoiceTextClient(env=ctx.obj["env"])
    job = client.load_job(job_id, jobs_dir)
    click.echo(_json(client.build_provider_request(job)))


@main.command()
@click.argument("path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--provider-command", default=lambda: os.getenv("HVTT_PROVIDER_COMMAND"), help="Command that prints provider JSON. Supports {input}, {language}, and {env}.")
@click.option("--language", default=lambda: os.getenv("HVTT_LANGUAGE", "he-IL"), show_default="HVTT_LANGUAGE or he-IL")
@click.option("--job-id", default=None, help="Optional job identifier to attach to output.")
@click.option("--output-dir", type=click.Path(file_okay=False, path_type=Path), default=Path("out"), show_default=True)
@click.option("--format", "formats", multiple=True, default=("txt", "json"), show_default=True)
@click.option("--summary/--no-summary", default=True, show_default=True)
@click.pass_context
def transcribe(
    ctx: click.Context,
    path: Path,
    provider_command: str | None,
    language: str,
    job_id: str | None,
    output_dir: Path,
    formats: tuple[str, ...],
    summary: bool,
) -> None:
    """Transcribe input via provider command or parse text/JSON input."""
    client = HebrewVoiceTextClient(provider_command=provider_command, default_language=language, env=ctx.obj["env"])
    result = client.transcribe(path, language=language, job_id=job_id)
    written = client.save_result(result, output_dir, formats=formats)
    payload = {"written": [str(item) for item in written]}
    if summary:
        payload["summary"] = client.summarize_result(result)
    click.echo(_json(payload))


@main.command("run-job")
@click.argument("job_id")
@click.option("--jobs-dir", type=click.Path(exists=True, file_okay=False, path_type=Path), default=Path(".hvt-jobs"), show_default=True)
@click.option("--provider-command", default=lambda: os.getenv("HVTT_PROVIDER_COMMAND"), help="Command that prints provider JSON.")
@click.option("--output-dir", type=click.Path(file_okay=False, path_type=Path), default=Path("out"), show_default=True)
@click.pass_context
def run_job(ctx: click.Context, job_id: str, jobs_dir: Path, provider_command: str | None, output_dir: Path) -> None:
    """Run a persisted job using local parsing or provider command."""
    client = HebrewVoiceTextClient(provider_command=provider_command, env=ctx.obj["env"])
    job = client.load_job(job_id, jobs_dir)
    result = client.transcribe(job.source_file, provider_command=provider_command, language=job.language, job_id=job.id)
    written = client.save_result(result, output_dir, formats=job.outputs)
    click.echo(_json({"id": job.id, "written": [str(item) for item in written], "summary": client.summarize_result(result)}))


if __name__ == "__main__":
    main()
