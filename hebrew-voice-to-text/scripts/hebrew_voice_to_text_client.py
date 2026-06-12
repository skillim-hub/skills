"""Typed helpers for Hebrew voice-to-text workflows."""

from __future__ import annotations

import asyncio
import dataclasses
import hashlib
import json
import re
import shlex
import subprocess
import wave
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


HEBREW_NIQQUD_RE = re.compile(r"[\u0591-\u05C7]")
RTL_MARKS_RE = re.compile(r"[\u200e\u200f\u202a-\u202e]")
MULTI_SPACE_RE = re.compile(r"[ \t\f\v]+")
PHONE_RE = re.compile(r"(?:\+972[-\s]?)?(?:0?5\d|0[23489]|0[77])[-\s]?\d{3}[-\s]?\d{4}")
ID_RE = re.compile(r"(?<!\d)\d{9}(?!\d)")
CREDIT_CARD_RE = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")
BANK_HINT_RE = re.compile(r"(?:חשבון|בנק|סניף|iban|swift)", re.IGNORECASE)
AMOUNT_RE = re.compile(r"(?:₪\s?\d[\d,]*(?:\.\d+)?|\d[\d,]*(?:\.\d+)?\s?₪)")
DATE_DDMMYYYY_RE = re.compile(r"\b(?:0?[1-9]|[12]\d|3[01])/(?:0?[1-9]|1[0-2])/\d{4}\b")
SUPPORTED_AUDIO_SUFFIXES = {".wav", ".mp3", ".m4a", ".ogg", ".opus", ".aac", ".flac", ".webm", ".amr"}


@dataclasses.dataclass(slots=True)
class AudioFileInfo:
    """Basic audio file details."""

    path: str
    suffix: str
    size_bytes: int
    duration_seconds: float | None = None
    channels: int | None = None
    sample_rate_hz: int | None = None
    frames: int | None = None

    @property
    def is_wav(self) -> bool:
        """Return true for WAV input."""
        return self.suffix.lower() == ".wav"

    @property
    def is_supported_audio(self) -> bool:
        """Return true when the suffix is a common audio container."""
        return self.suffix.lower() in SUPPORTED_AUDIO_SUFFIXES


@dataclasses.dataclass(slots=True)
class TranscriptionSegment:
    """One transcript segment."""

    start: float
    end: float
    speaker: str
    text: str
    confidence: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize the segment."""
        data: dict[str, Any] = {
            "start": self.start,
            "end": self.end,
            "speaker": self.speaker,
            "text": self.text,
        }
        if self.confidence is not None:
            data["confidence"] = self.confidence
        return data


@dataclasses.dataclass(slots=True)
class TranscriptionResult:
    """Transcript result with segments and warnings."""

    language: str
    segments: list[TranscriptionSegment]
    duration_seconds: float | None = None
    warnings: list[str] = dataclasses.field(default_factory=list)
    sensitive_terms: list[str] = dataclasses.field(default_factory=list)
    source_path: str | None = None
    job_id: str | None = None

    @property
    def text(self) -> str:
        """Render speaker-labelled plain text."""
        lines: list[str] = []
        for segment in self.segments:
            prefix = f"{segment.speaker}: " if segment.speaker else ""
            lines.append(prefix + segment.text)
        return "\n".join(lines)

    @property
    def word_count(self) -> int:
        """Count whitespace-delimited words."""
        return sum(len(segment.text.split()) for segment in self.segments)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the full result."""
        return {
            "language": self.language,
            "duration_seconds": self.duration_seconds,
            "segments": [segment.to_dict() for segment in self.segments],
            "warnings": list(self.warnings),
            "sensitive_terms": list(self.sensitive_terms),
            "source_path": self.source_path,
            "job_id": self.job_id,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "TranscriptionResult":
        """Create a result from provider JSON."""
        segments = [
            TranscriptionSegment(
                start=float(item.get("start", 0.0)),
                end=float(item.get("end", 0.0)),
                speaker=str(item.get("speaker", "דובר 1")),
                text=str(item.get("text", "")),
                confidence=float(item["confidence"]) if item.get("confidence") is not None else None,
            )
            for item in data.get("segments", [])
        ]
        return cls(
            language=str(data.get("language", "he-IL")),
            segments=segments,
            duration_seconds=float(data["duration_seconds"]) if data.get("duration_seconds") is not None else None,
            warnings=[str(item) for item in data.get("warnings", [])],
            sensitive_terms=[str(item) for item in data.get("sensitive_terms", [])],
            source_path=str(data["source_path"]) if data.get("source_path") is not None else None,
            job_id=str(data["job_id"]) if data.get("job_id") is not None else None,
        )


@dataclasses.dataclass(slots=True)
class JobSpec:
    """Provider-neutral job request."""

    id: str
    source_file: str
    language: str = "he-IL"
    expected_speakers: int = 1
    speaker_labels: bool = True
    sensitivity: str = "medium"
    env: str = "sandbox"
    outputs: list[str] = dataclasses.field(default_factory=lambda: ["txt", "json"])

    def to_dict(self) -> dict[str, Any]:
        """Serialize the job request."""
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "JobSpec":
        """Create a job request from JSON."""
        return cls(
            id=str(data["id"]),
            source_file=str(data["source_file"]),
            language=str(data.get("language", "he-IL")),
            expected_speakers=int(data.get("expected_speakers", 1)),
            speaker_labels=bool(data.get("speaker_labels", True)),
            sensitivity=str(data.get("sensitivity", "medium")),
            env=str(data.get("env", "sandbox")),
            outputs=[str(item) for item in data.get("outputs", ["txt", "json"])],
        )


class ProviderCommandError(RuntimeError):
    """Raised when a provider command fails or emits invalid output."""


class HebrewVoiceTextClient:
    """Provider-neutral Hebrew transcription helper."""

    def __init__(
        self,
        provider_command: Sequence[str] | str | None = None,
        default_language: str = "he-IL",
        default_speaker: str = "דובר 1",
        env: str = "sandbox",
    ) -> None:
        self.provider_command = provider_command
        self.default_language = default_language
        self.default_speaker = default_speaker
        self.env = validate_env(env)

    def inspect_audio(self, path: str | Path) -> AudioFileInfo:
        """Inspect file size and WAV metadata when available."""
        input_path = Path(path)
        if not input_path.exists():
            raise FileNotFoundError(str(input_path))
        info = AudioFileInfo(
            path=str(input_path),
            suffix=input_path.suffix.lower(),
            size_bytes=input_path.stat().st_size,
        )
        if input_path.suffix.lower() == ".wav":
            with wave.open(str(input_path), "rb") as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                info.frames = frames
                info.sample_rate_hz = rate
                info.channels = wav_file.getnchannels()
                info.duration_seconds = frames / float(rate) if rate else None
        return info

    def normalize_hebrew_text(self, text: str, add_punctuation: bool = True) -> str:
        """Remove Hebrew marks, collapse spacing, and add light terminal punctuation."""
        normalized = RTL_MARKS_RE.sub("", text)
        normalized = HEBREW_NIQQUD_RE.sub("", normalized)
        normalized = normalized.replace("״", '"').replace("׳", "'")
        normalized = normalized.replace("–", "-").replace("—", "-")
        normalized = re.sub(r"\s+([,.!?;:])", r"\1", normalized)
        normalized = re.sub(r"([,.!?;:])(?=\S)", r"\1 ", normalized)
        normalized = MULTI_SPACE_RE.sub(" ", normalized).strip()
        normalized = re.sub(r"\s*\n\s*", "\n", normalized)
        if add_punctuation:
            normalized = self.add_light_punctuation(normalized)
        return normalized

    def add_light_punctuation(self, text: str) -> str:
        """Add sentence-ending punctuation without guessing internal punctuation."""
        stripped = text.strip()
        if not stripped:
            return ""
        if stripped[-1] in ".!?…":
            return stripped
        question_cues = ("מה ", "מי ", "מתי ", "איפה ", "למה ", "כמה ", "האם ", "אפשר ", "צריך ")
        if stripped.startswith(question_cues):
            return stripped + "?"
        return stripped + "."

    def detect_sensitive_terms(self, text: str) -> list[str]:
        """Detect common Israeli sensitive values."""
        terms: list[str] = []
        if PHONE_RE.search(text):
            terms.append("phone")
        if ID_RE.search(text):
            terms.append("israeli_id")
        if CREDIT_CARD_RE.search(text):
            terms.append("payment_card")
        if BANK_HINT_RE.search(text):
            terms.append("banking")
        if AMOUNT_RE.search(text):
            terms.append("amount")
        return sorted(set(terms))

    def redact_sensitive_text(self, text: str) -> str:
        """Redact common sensitive values while keeping text readable."""
        redacted = PHONE_RE.sub(lambda m: self._redact_phone(m.group(0)), text)
        redacted = ID_RE.sub(lambda m: "*" * 8 + m.group(0)[-1], redacted)
        redacted = CREDIT_CARD_RE.sub("[כרטיס טושטש]", redacted)
        return redacted

    def label_segments(
        self,
        raw_segments: Iterable[Mapping[str, Any] | str],
        speaker_labels: Sequence[str] | None = None,
    ) -> list[TranscriptionSegment]:
        """Normalize and label transcript segments."""
        labels = list(speaker_labels or [self.default_speaker]) or [self.default_speaker]
        segments: list[TranscriptionSegment] = []
        for index, item in enumerate(raw_segments):
            if isinstance(item, str):
                text = item
                start = float(index)
                end = float(index + 1)
                speaker = labels[index % len(labels)]
                confidence = None
            else:
                text = str(item.get("text", ""))
                start = float(item.get("start", index))
                end = float(item.get("end", start))
                speaker = str(item.get("speaker") or labels[index % len(labels)])
                confidence = float(item["confidence"]) if item.get("confidence") is not None else None
            segments.append(
                TranscriptionSegment(
                    start=start,
                    end=end,
                    speaker=speaker,
                    text=self.normalize_hebrew_text(text),
                    confidence=confidence,
                )
            )
        return segments

    def parse_provider_payload(
        self,
        payload: str | bytes | Mapping[str, Any],
        source_path: str | None = None,
        job_id: str | None = None,
    ) -> TranscriptionResult:
        """Parse provider output with either segments or a single text field."""
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        data = json.loads(payload) if isinstance(payload, str) else dict(payload)
        if "segments" not in data and "text" in data:
            data["segments"] = [{"start": 0.0, "end": 0.0, "speaker": self.default_speaker, "text": data["text"]}]
        if "segments" not in data:
            raise ProviderCommandError("Provider output must include 'segments' or 'text'.")
        result = TranscriptionResult.from_dict(
            {
                "language": data.get("language", self.default_language),
                "duration_seconds": data.get("duration_seconds"),
                "segments": data.get("segments", []),
                "warnings": data.get("warnings", []),
                "sensitive_terms": data.get("sensitive_terms", []),
                "source_path": source_path or data.get("source_path"),
                "job_id": job_id or data.get("job_id"),
            }
        )
        result.segments = self.label_segments([segment.to_dict() for segment in result.segments])
        result.sensitive_terms = sorted(set(result.sensitive_terms + self.detect_sensitive_terms(result.text)))
        return result

    def transcribe(
        self,
        path: str | Path,
        *,
        provider_command: Sequence[str] | str | None = None,
        language: str | None = None,
        job_id: str | None = None,
    ) -> TranscriptionResult:
        """Transcribe text/JSON locally or invoke a provider command for audio."""
        input_path = Path(path)
        if not input_path.exists():
            raise FileNotFoundError(str(input_path))
        final_language = language or self.default_language
        if input_path.suffix.lower() == ".json":
            return self.parse_provider_payload(input_path.read_text(encoding="utf-8"), source_path=str(input_path), job_id=job_id)
        if input_path.suffix.lower() in {".txt", ".md"}:
            result = TranscriptionResult(
                language=final_language,
                segments=self.label_segments([input_path.read_text(encoding="utf-8")]),
                source_path=str(input_path),
                job_id=job_id,
            )
            result.sensitive_terms = self.detect_sensitive_terms(result.text)
            return result
        command = provider_command or self.provider_command
        if command is None:
            raise ProviderCommandError("No provider command configured. Supply a command that prints JSON with segments.")
        completed = subprocess.run(
            self.format_provider_command(command, input_path, final_language),
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise ProviderCommandError(completed.stderr.strip() or "Provider command failed.")
        try:
            result = self.parse_provider_payload(completed.stdout, source_path=str(input_path), job_id=job_id)
        except json.JSONDecodeError as exc:
            raise ProviderCommandError("Provider command did not emit valid JSON.") from exc
        if result.duration_seconds is None:
            try:
                result.duration_seconds = self.inspect_audio(input_path).duration_seconds
            except Exception:
                pass
        return result

    async def async_transcribe(
        self,
        path: str | Path,
        *,
        provider_command: Sequence[str] | str | None = None,
        language: str | None = None,
        job_id: str | None = None,
    ) -> TranscriptionResult:
        """Run transcribe in a worker thread."""
        return await asyncio.to_thread(
            self.transcribe,
            path,
            provider_command=provider_command,
            language=language,
            job_id=job_id,
        )

    def save_result(
        self,
        result: TranscriptionResult,
        output_dir: str | Path,
        *,
        stem: str | None = None,
        formats: Sequence[str] = ("txt", "json"),
    ) -> list[Path]:
        """Write transcript outputs in selected formats."""
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = stem or (Path(result.source_path).stem if result.source_path else "transcript")
        paths: list[Path] = []
        for fmt in formats:
            fmt_lower = fmt.lower()
            path = out_dir / f"{stem}.{fmt_lower}"
            if fmt_lower == "txt":
                path.write_text(render_txt(result), encoding="utf-8")
            elif fmt_lower == "json":
                path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
            elif fmt_lower == "srt":
                path.write_text(render_srt(result), encoding="utf-8")
            elif fmt_lower == "vtt":
                path.write_text(render_vtt(result), encoding="utf-8")
            elif fmt_lower == "md":
                path.write_text(render_markdown(result), encoding="utf-8")
            else:
                raise ValueError(f"Unsupported output format: {fmt}")
            paths.append(path)
        return paths

    def create_job(
        self,
        source_file: str | Path,
        *,
        expected_speakers: int = 1,
        speaker_labels: bool = True,
        sensitivity: str = "medium",
        outputs: Sequence[str] = ("txt", "json"),
        jobs_dir: str | Path | None = None,
    ) -> JobSpec:
        """Create a deterministic local job specification."""
        input_path = Path(source_file)
        if not input_path.exists():
            raise FileNotFoundError(str(input_path))
        job_id = build_job_id(input_path, self.env, self.default_language)
        job = JobSpec(
            id=job_id,
            source_file=str(input_path),
            language=self.default_language,
            expected_speakers=max(1, int(expected_speakers)),
            speaker_labels=bool(speaker_labels),
            sensitivity=sensitivity,
            env=self.env,
            outputs=[str(item) for item in outputs],
        )
        if jobs_dir is not None:
            self.write_job(job, jobs_dir)
        return job

    def write_job(self, job: JobSpec, jobs_dir: str | Path) -> Path:
        """Persist a job JSON file."""
        directory = Path(jobs_dir)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{job.id}.json"
        path.write_text(json.dumps(job.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def load_job(self, job_id: str, jobs_dir: str | Path) -> JobSpec:
        """Load a persisted job JSON file."""
        path = Path(jobs_dir) / f"{job_id}.json"
        if not path.exists():
            raise FileNotFoundError(str(path))
        return JobSpec.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def build_provider_request(self, job: JobSpec) -> dict[str, Any]:
        """Create a provider-neutral request body."""
        return {
            "id": job.id,
            "input": {"file": job.source_file, "language": job.language},
            "options": {
                "punctuation": True,
                "speaker_labels": job.speaker_labels,
                "expected_speakers": job.expected_speakers,
                "timestamps": True,
                "sensitivity": job.sensitivity,
            },
            "outputs": job.outputs,
            "environment": job.env,
        }

    def summarize_result(self, result: TranscriptionResult) -> dict[str, Any]:
        """Return compact quality and privacy summary."""
        return {
            "job_id": result.job_id,
            "language": result.language,
            "segments": len(result.segments),
            "word_count": result.word_count,
            "duration_seconds": result.duration_seconds,
            "sensitive_terms": result.sensitive_terms,
            "warnings": result.warnings,
        }

    def format_provider_command(self, command: Sequence[str] | str, input_path: Path, language: str) -> list[str]:
        """Substitute provider command placeholders."""
        parts = shlex.split(command) if isinstance(command, str) else [str(part) for part in command]
        values = {"input": str(input_path), "language": language, "lang": language, "env": self.env}
        return [part.format(**values) for part in parts]

    def _redact_phone(self, value: str) -> str:
        digits = re.sub(r"\D", "", value)
        if len(digits) < 7:
            return "[טלפון טושטש]"
        local_digits = digits[-10:] if digits.startswith("972") else digits
        return f"{local_digits[:3]}-***{local_digits[-4:]}"


def build_job_id(path: str | Path, env: str = "sandbox", language: str = "he-IL") -> str:
    """Build a stable local job identifier."""
    input_path = Path(path)
    stat = input_path.stat()
    seed = f"{input_path.resolve()}|{stat.st_size}|{int(stat.st_mtime)}|{env}|{language}"
    return "hvt_" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]


def validate_env(env: str) -> str:
    """Validate environment name."""
    if env not in {"sandbox", "production"}:
        raise ValueError("env must be either 'sandbox' or 'production'.")
    return env


def format_timestamp(seconds: float, *, vtt: bool = False) -> str:
    """Format seconds as SRT or VTT timestamp."""
    milliseconds = int(round(max(seconds, 0.0) * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    separator = "." if vtt else ","
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{millis:03d}"


def render_txt(result: TranscriptionResult) -> str:
    """Render plain text."""
    return result.text + ("\n" if result.text else "")


def render_srt(result: TranscriptionResult) -> str:
    """Render SubRip subtitles."""
    blocks: list[str] = []
    for index, segment in enumerate(result.segments, start=1):
        text = f"{segment.speaker}: {segment.text}" if segment.speaker else segment.text
        blocks.append(f"{index}\n{format_timestamp(segment.start)} --> {format_timestamp(segment.end)}\n{text}")
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def render_vtt(result: TranscriptionResult) -> str:
    """Render WebVTT subtitles."""
    blocks = ["WEBVTT", ""]
    for segment in result.segments:
        text = f"{segment.speaker}: {segment.text}" if segment.speaker else segment.text
        blocks.append(f"{format_timestamp(segment.start, vtt=True)} --> {format_timestamp(segment.end, vtt=True)}")
        blocks.append(text)
        blocks.append("")
    return "\n".join(blocks)


def render_markdown(result: TranscriptionResult) -> str:
    """Render Markdown transcript."""
    lines = [
        "# Transcript",
        "",
        f"- Language: {result.language}",
        f"- Duration: {result.duration_seconds if result.duration_seconds is not None else '[unknown]'}",
        f"- Sensitive terms: {', '.join(result.sensitive_terms) if result.sensitive_terms else 'none detected'}",
        "",
        "## Segments",
        "",
    ]
    for segment in result.segments:
        lines.append(
            f"- `{format_timestamp(segment.start, vtt=True)}-{format_timestamp(segment.end, vtt=True)}` "
            f"**{segment.speaker}:** {segment.text}"
        )
    return "\n".join(lines) + "\n"


def validate_consent(consent: bool, sensitivity: str = "medium") -> None:
    """Block medium or high sensitivity processing without consent or lawful basis."""
    if not consent and sensitivity.lower() in {"medium", "high"}:
        raise PermissionError("Consent or a lawful basis is required before processing this audio.")


__all__ = [
    "AudioFileInfo",
    "HebrewVoiceTextClient",
    "JobSpec",
    "ProviderCommandError",
    "TranscriptionResult",
    "TranscriptionSegment",
    "build_job_id",
    "format_timestamp",
    "render_markdown",
    "render_srt",
    "render_txt",
    "render_vtt",
    "validate_consent",
    "validate_env",
]
