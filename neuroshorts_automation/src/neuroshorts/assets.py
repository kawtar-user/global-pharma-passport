from __future__ import annotations

import math
import wave
from pathlib import Path

import numpy as np


def generate_background_music(output_path: Path, duration: float, volume: float = 0.08) -> Path:
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    pad = (
        0.45 * np.sin(2 * math.pi * 220 * t)
        + 0.25 * np.sin(2 * math.pi * 329.63 * t)
        + 0.18 * np.sin(2 * math.pi * 440 * t)
    )
    envelope = np.minimum(1.0, t / 1.5) * np.minimum(1.0, (duration - t) / 2.5)
    waveform = np.clip(pad * envelope * volume, -1.0, 1.0)
    pcm = (waveform * 32767).astype(np.int16)

    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())
    return output_path

