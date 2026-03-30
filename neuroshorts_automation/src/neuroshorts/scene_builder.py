from __future__ import annotations

from .models import Scene, ScriptPackage


def split_into_scenes(script: ScriptPackage) -> list[Scene]:
    total = float(script.estimated_duration)
    durations = [3.0, 5.0, 6.0, 6.0, 7.0, 7.0, 6.0, max(5.0, total - 40.0)]
    labels = [
        "Hook impact",
        "Neuro explication 1",
        "Neuro explication 2",
        "Neuro explication 3",
        "Exemple reel 1",
        "Exemple reel 2",
        "Transition solution",
        "Finale memorable",
    ]
    texts = [
        script.hook_section,
        "La dopamine pousse ton cerveau a chercher la prochaine recompense.",
        "Trop de stimulations rapides rendent l'effort normal moins attirant.",
        script.explanation_section,
        "Dans la vraie vie, le scroll gagne souvent contre une tache profonde.",
        script.example_section,
        "La bonne nouvelle, c'est que ton attention se reprogramme.",
        script.solution_section,
    ]

    scenes: list[Scene] = []
    cursor = 0.0
    for index, (duration, label, text) in enumerate(zip(durations, labels, texts), start=1):
        start = cursor
        end = cursor + duration
        scenes.append(
            Scene(
                index=index,
                label=label,
                text=text,
                start=round(start, 2),
                end=round(end, 2),
                duration=round(duration, 2),
            )
        )
        cursor = end
    return scenes

