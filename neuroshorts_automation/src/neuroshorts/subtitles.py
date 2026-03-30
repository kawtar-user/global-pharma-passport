from __future__ import annotations

from pathlib import Path

from .models import ScriptPackage
from .utils import chunk_words


def _format_timestamp(seconds: float) -> str:
    ms = int(round((seconds - int(seconds)) * 1000))
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def generate_subtitles(
    script: ScriptPackage,
    output_path: Path | None = None,
    total_duration: float | None = None,
) -> Path:
    output_path = output_path or Path("subtitles/subtitles.srt")
    duration = float(total_duration or script.estimated_duration)
    chunks = chunk_words(script.full_script, max_words=5)
    slice_duration = max(1.2, duration / max(1, len(chunks)))
    lines: list[str] = []
    cursor = 0.0

    for idx, chunk in enumerate(chunks, start=1):
        start = cursor
        end = min(duration, start + slice_duration)
        lines.append(str(idx))
        lines.append(f"{_format_timestamp(start)} --> {_format_timestamp(end)}")
        lines.append(chunk)
        lines.append("")
        cursor = end

    output_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return output_path
