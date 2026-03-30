from __future__ import annotations

import logging
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    AudioFileClip,
    ColorClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    VideoFileClip,
    concatenate_videoclips,
)

from .assets import generate_background_music
from .config import Settings
from .models import Scene
from .utils import clamp


logger = logging.getLogger(__name__)


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def _create_prompt_card(scene: Scene, settings: Settings) -> ImageClip:
    width, height = settings.width, settings.height
    image = Image.new("RGB", (width, height), color=(8, 10, 18))
    draw = ImageDraw.Draw(image)

    for y in range(height):
        ratio = y / max(1, height - 1)
        color = (
            int(10 + 40 * ratio),
            int(14 + 30 * (1 - ratio)),
            int(20 + 90 * ratio),
        )
        draw.line([(0, y), (width, y)], fill=color)

    draw.ellipse((80, 160, width - 80, width + 20), outline=(90, 180, 255), width=6)
    draw.rectangle((90, 1240, width - 90, 1670), fill=(12, 16, 28))

    title_font = _font(62)
    body_font = _font(40)
    draw.text((100, 120), f"SCENE {scene.index}", fill=(180, 220, 255), font=title_font)
    draw.text((100, 230), scene.label.upper(), fill=(255, 255, 255), font=title_font)
    draw.multiline_text(
        (120, 1280),
        scene.text,
        fill=(236, 240, 255),
        font=body_font,
        spacing=18,
        align="left",
    )
    return ImageClip(np.array(image)).with_duration(scene.duration)


def _clip_zoom(clip: ImageClip | VideoFileClip) -> ImageClip | VideoFileClip:
    return clip.resized(lambda t: 1.0 + min(0.08, t * 0.015)).with_position("center")


def _load_or_create_scene_clip(scene: Scene, settings: Settings) -> ImageClip | VideoFileClip:
    supported = [settings.clips_dir / f"scene_{scene.index}.mp4", settings.clips_dir / f"{scene.index}.mp4"]
    for path in supported:
        if path.exists():
            loaded = VideoFileClip(str(path))
            loaded = loaded.subclipped(0, min(scene.duration, loaded.duration))
            return _clip_zoom(
                loaded.resized(height=settings.height).cropped(
                    width=settings.width,
                    height=settings.height,
                    x_center=settings.width / 2,
                    y_center=settings.height / 2,
                )
            )
    return _clip_zoom(_create_prompt_card(scene, settings))


def _parse_srt_entries(subtitle_path: Path) -> list[tuple[float, float, str]]:
    entries: list[tuple[float, float, str]] = []
    blocks = subtitle_path.read_text(encoding="utf-8").strip().split("\n\n")
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 3:
            continue
        timing = lines[1]
        start_raw, end_raw = timing.split(" --> ")
        text = " ".join(lines[2:])
        entries.append((_ts_to_seconds(start_raw), _ts_to_seconds(end_raw), text))
    return entries


def _ts_to_seconds(value: str) -> float:
    hh, mm, rest = value.split(":")
    ss, ms = rest.split(",")
    return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000


def _build_subtitle_layer(subtitle_path: Path, settings: Settings) -> list[TextClip]:
    layers: list[TextClip] = []
    for start, end, text in _parse_srt_entries(subtitle_path):
        clip = (
            TextClip(
                text=text.upper(),
                font_size=58,
                color="white",
                stroke_color="black",
                stroke_width=2,
                method="caption",
                size=(settings.width - 130, None),
                text_align="center",
            )
            .with_start(start)
            .with_end(end)
            .with_position(("center", settings.height - 420))
        )
        layers.append(clip)
    return layers


def assemble_video(
    audio: Path,
    clips: list[Scene],
    subtitles: Path,
    output: Path,
    settings: Settings | None = None,
) -> Path:
    settings = settings or Settings()
    voice_clip = AudioFileClip(str(audio))
    total_duration = voice_clip.duration
    logger.info("Duree voix off detectee: %.2fs", total_duration)

    adjusted_scenes: list[Scene] = []
    accumulated = 0.0
    for idx, scene in enumerate(clips):
        remaining = max(0.5, total_duration - accumulated)
        if idx == len(clips) - 1:
            duration = remaining
        else:
            planned = scene.duration
            duration = clamp(planned, 2.5, remaining - (len(clips) - idx - 1) * 2.5)
        adjusted_scenes.append(
            Scene(
                index=scene.index,
                label=scene.label,
                text=scene.text,
                start=accumulated,
                end=accumulated + duration,
                duration=duration,
                sora_prompt=scene.sora_prompt,
            )
        )
        accumulated += duration

    visual_clips = []
    for scene in adjusted_scenes:
        clip = _load_or_create_scene_clip(scene, settings).with_duration(scene.duration)
        clip = clip.with_fps(settings.fps)
        if clip.w != settings.width or clip.h != settings.height:
            clip = clip.resized((settings.width, settings.height))
        visual_clips.append(clip)

        if len(visual_clips) > 1 and random.random() > 0.45:
            flash = ColorClip((settings.width, settings.height), color=(245, 248, 255), duration=0.08).with_opacity(0.05)
            visual_clips.append(flash)

    base_video = concatenate_videoclips(visual_clips, method="compose").with_duration(total_duration)
    subtitle_layers = _build_subtitle_layer(subtitles, settings)

    music_path = settings.audio_dir / "background_music.wav"
    generate_background_music(music_path, duration=total_duration + 0.25, volume=settings.background_music_volume)
    music_clip = AudioFileClip(str(music_path)).with_duration(total_duration).with_volume_scaled(settings.background_music_volume)
    final_audio = CompositeAudioClip([voice_clip.with_volume_scaled(1.0), music_clip])

    final_video = CompositeVideoClip([base_video, *subtitle_layers], size=(settings.width, settings.height)).with_audio(final_audio)
    final_video.write_videofile(
        str(output),
        codec="libx264",
        audio_codec="aac",
        fps=settings.fps,
        preset="medium",
        threads=4,
        ffmpeg_params=["-pix_fmt", "yuv420p"],
        logger=None,
    )
    final_video.close()
    voice_clip.close()
    music_clip.close()
    base_video.close()
    return output
