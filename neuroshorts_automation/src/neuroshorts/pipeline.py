from __future__ import annotations

import logging
from pathlib import Path

from moviepy import AudioFileClip

from .config import Settings
from .models import ScriptPackage
from .prompt_builder import build_sora_prompts
from .scene_builder import split_into_scenes
from .script_generator import generate_script
from .subtitles import generate_subtitles
from .utils import slugify, write_json
from .video_assembler import assemble_video
from .voice import generate_voice


logger = logging.getLogger(__name__)


def save_script_assets(script: ScriptPackage, settings: Settings) -> None:
    write_json(settings.scripts_dir / "script_package.json", script.to_dict())
    settings.scripts_dir.joinpath("script.txt").write_text(script.full_script + "\n", encoding="utf-8")
    settings.scripts_dir.joinpath("youtube_metadata.txt").write_text(
        "\n".join(
            [
                f"Titre: {script.title}",
                "",
                f"Description: {script.description}",
                "",
                "Hooks:",
                *[f"- {hook}" for hook in script.hooks],
                "",
                "Hashtags:",
                " ".join(script.hashtags),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_pipeline(topic: str, settings: Settings) -> Path:
    logger.info("Generation du script pour: %s", topic)
    script = generate_script(topic, settings)
    script.scenes = split_into_scenes(script)
    save_script_assets(script, settings)

    logger.info("Generation des prompts Sora")
    build_sora_prompts(script.scenes, settings.scripts_dir / "sora_prompts.txt")

    logger.info("Generation de la voix off")
    voice_path = generate_voice(script, settings)
    voice_probe = AudioFileClip(str(voice_path))
    voice_duration = voice_probe.duration
    voice_probe.close()

    logger.info("Generation des sous-titres")
    subtitles_path = generate_subtitles(
        script=script,
        output_path=settings.subtitles_dir / "subtitles.srt",
        total_duration=voice_duration,
    )

    output_name = f"{slugify(topic)}.mp4"
    output_path = settings.exports_dir / output_name
    logger.info("Assemblage video final")
    return assemble_video(voice_path, script.scenes, subtitles_path, output_path, settings)
