from __future__ import annotations

from pathlib import Path

from .models import Scene


def build_sora_prompts(scene_data: list[Scene], output_path: Path | None = None) -> list[str]:
    output_path = output_path or Path("scripts/sora_prompts.txt")
    prompts: list[str] = []
    for scene in scene_data:
        prompt = (
            f"Scene {scene.index} | {scene.label} | vertical 9:16, 1080x1920, faceless neuroscience short, "
            f"hyper cinematic, high contrast lighting, modern intense pacing, subtle handheld energy, "
            f"fast cuts feeling, premium ad realism, realistic textures, dramatic depth, no faces, no talking head, "
            f"focus on objects, screens, silhouettes, neurons, city night mood, French social media style. "
            f"Narrative intent: {scene.text} "
            f"Visual direction: metaphorical neuroscience imagery mixed with everyday life, motion-rich composition, "
            f"clean center framing for subtitles, slight push-in camera, tactile atmosphere."
        )
        scene.sora_prompt = prompt
        prompts.append(prompt)

    lines = []
    for scene, prompt in zip(scene_data, prompts):
        lines.append(f"[Scene {scene.index}] {scene.label}")
        lines.append(prompt)
        lines.append("")
    output_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return prompts
