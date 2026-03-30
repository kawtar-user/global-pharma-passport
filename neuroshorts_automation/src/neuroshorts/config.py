from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")


@dataclass
class Settings:
    root_dir: Path = ROOT_DIR
    input_dir: Path = ROOT_DIR / "input"
    scripts_dir: Path = ROOT_DIR / "scripts"
    audio_dir: Path = ROOT_DIR / "audio"
    clips_dir: Path = ROOT_DIR / "clips"
    subtitles_dir: Path = ROOT_DIR / "subtitles"
    exports_dir: Path = ROOT_DIR / "exports"
    config_dir: Path = ROOT_DIR / "config"
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    tts_model: str = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
    tts_voice: str = os.getenv("OPENAI_TTS_VOICE", "alloy")
    background_music_volume: float = float(os.getenv("BACKGROUND_MUSIC_VOLUME", "0.08"))
    default_duration: int = int(os.getenv("DEFAULT_DURATION_SECONDS", "46"))
    fps: int = int(os.getenv("VIDEO_FPS", "30"))
    width: int = 1080
    height: int = 1920
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    def ensure_directories(self) -> None:
        for path in (
            self.input_dir,
            self.scripts_dir,
            self.audio_dir,
            self.clips_dir,
            self.subtitles_dir,
            self.exports_dir,
            self.config_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

