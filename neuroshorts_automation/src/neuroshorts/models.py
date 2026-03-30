from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Scene:
    index: int
    label: str
    text: str
    start: float
    end: float
    duration: float
    sora_prompt: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScriptPackage:
    topic: str
    title: str
    description: str
    hashtags: list[str]
    hooks: list[str]
    hook_section: str
    explanation_section: str
    example_section: str
    solution_section: str
    full_script: str
    estimated_duration: float = 45.0
    scenes: list[Scene] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["scenes"] = [scene.to_dict() for scene in self.scenes]
        return payload

