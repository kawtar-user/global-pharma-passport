from __future__ import annotations

import logging
import subprocess
import wave
from pathlib import Path

from openai import OpenAI

from .config import Settings
from .models import ScriptPackage


logger = logging.getLogger(__name__)


def _generate_with_say(script: ScriptPackage, output_path: Path) -> Path:
    aiff_path = output_path.with_suffix(".aiff")
    voice_candidates = ["Thomas", "Amelie"]
    for voice_name in voice_candidates:
        command = ["say", "-v", voice_name, "-r", "185", "-o", str(aiff_path), script.full_script]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0 and aiff_path.exists():
            return aiff_path
    raise RuntimeError(f"Echec du fallback macOS say: {result.stderr.strip()}")


def _validate_wav(path: Path) -> bool:
    try:
        with wave.open(str(path), "rb"):
            return True
    except Exception:
        return False


def generate_voice(script: ScriptPackage, settings: Settings | None = None) -> Path:
    settings = settings or Settings()
    output_path = settings.audio_dir / "voiceover.wav"
    if settings.openai_api_key:
        client = OpenAI(api_key=settings.openai_api_key)
        instructions = (
            "Voix off francaise tres naturelle, rythme moderne, intense mais clair, "
            "avec des pauses legeres pour un format YouTube Shorts faceless."
        )
        try:
            with client.audio.speech.with_streaming_response.create(
                model=settings.tts_model,
                voice=settings.tts_voice,
                input=script.full_script,
                instructions=instructions,
                response_format="wav",
            ) as response:
                response.stream_to_file(output_path)
            if _validate_wav(output_path):
                logger.info("Voix off OpenAI generee: %s", output_path)
                return output_path
        except Exception as exc:
            logger.exception("Echec TTS OpenAI, fallback pyttsx3 active: %s", exc)

    fallback_path = _generate_with_say(script, output_path)
    logger.warning("Voix off locale generee avec macOS say: %s", fallback_path)
    return fallback_path
