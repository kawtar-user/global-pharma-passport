from __future__ import annotations

import json
import logging
from typing import Any

from openai import OpenAI

from .config import Settings
from .models import ScriptPackage


logger = logging.getLogger(__name__)


def _fallback_script(topic: str, duration: int) -> ScriptPackage:
    title = f"{topic} : la vérité que ton cerveau cache"
    hooks = [
        f"Et si {topic.lower()} contrôlait déjà tes journées sans que tu le voies ?",
        f"Le vrai piège derrière {topic.lower()}, c'est dans ton cerveau.",
        f"Ton cerveau adore {topic.lower()}, mais ça te coûte plus que tu crois.",
    ]
    hook = hooks[0]
    explanation = (
        "La dopamine n'est pas le plaisir, c'est le signal qui te pousse à chercher encore. "
        "Quand ton cerveau reçoit trop de micro-récompenses, il s'habitue à l'instantané et trouve l'effort normal beaucoup plus fade."
    )
    example = (
        "C'est pour ça qu'après dix minutes de scroll, ouvrir un cours, lire un livre ou finir un dossier "
        "te semble presque douloureux. Ton cerveau compare un effort lent à des récompenses ultra rapides."
    )
    solution = (
        "La sortie, c'est de recréer du contraste : coupe les stimulations pendant quelques minutes, "
        "commence par une seule tâche simple, et laisse ton attention redevenir rare. "
        "La concentration revient quand la surcharge disparaît."
    )
    description = "Une explication simple et intense sur la dopamine, la concentration et comment reprendre le contrôle."
    hashtags = [
        "#neuroscience",
        "#dopamine",
        "#concentration",
        "#productivite",
        "#cerveau",
        "#shortsfr",
        "#habitudes",
        "#discipline",
        "#focus",
        "#psychologie",
    ]
    full_script = " ".join([hook, explanation, example, solution])
    return ScriptPackage(
        topic=topic,
        title=title,
        description=description,
        hashtags=hashtags,
        hooks=hooks,
        hook_section=hook,
        explanation_section=explanation,
        example_section=example,
        solution_section=solution,
        full_script=full_script,
        estimated_duration=float(duration),
    )


def _coerce_script(payload: dict[str, Any], topic: str, duration: int) -> ScriptPackage:
    hooks = payload.get("hooks") or []
    while len(hooks) < 3:
        hooks.append(f"Ce que ton cerveau fait avec {topic.lower()} va te surprendre.")

    full_script = " ".join(
        [
            payload["hook_section"].strip(),
            payload["explanation_section"].strip(),
            payload["example_section"].strip(),
            payload["solution_section"].strip(),
        ]
    )
    hashtags = payload.get("hashtags") or []
    hashtags = [tag if tag.startswith("#") else f"#{tag}" for tag in hashtags][:10]

    return ScriptPackage(
        topic=topic,
        title=payload["title"].strip(),
        description=payload["description"].strip(),
        hashtags=hashtags,
        hooks=hooks[:3],
        hook_section=payload["hook_section"].strip(),
        explanation_section=payload["explanation_section"].strip(),
        example_section=payload["example_section"].strip(),
        solution_section=payload["solution_section"].strip(),
        full_script=full_script,
        estimated_duration=float(payload.get("estimated_duration", duration)),
    )


def generate_script(topic: str, settings: Settings | None = None) -> ScriptPackage:
    settings = settings or Settings()
    duration = settings.default_duration
    if not settings.openai_api_key:
        logger.warning("OPENAI_API_KEY absent. Utilisation du fallback local pour le script.")
        return _fallback_script(topic, duration)

    client = OpenAI(api_key=settings.openai_api_key)
    prompt = f"""
Tu crées des scripts YouTube Shorts faceless en français sur la neuroscience.
Sujet : {topic}

Contraintes obligatoires :
- public 18-35 ans
- ton simple, captivant, viral, moderne, intense
- pas académique
- durée 35 à 55 secondes
- structure :
  1. 0 à 3 sec : hook très fort
  2. 3 à 20 sec : explication neuroscientifique ultra simple
  3. 20 à 40 sec : exemple concret de la vie réelle
  4. 40 à 55 sec : mini solution ou phrase finale mémorable
- sortie en français uniquement
- phrases courtes et punchy

Réponds uniquement en JSON avec ce schéma :
{{
  "title": "titre YouTube",
  "description": "description courte",
  "hashtags": ["#a", "... 10 max"],
  "hooks": ["variante 1", "variante 2", "variante 3"],
  "hook_section": "texte",
  "explanation_section": "texte",
  "example_section": "texte",
  "solution_section": "texte",
  "estimated_duration": 46
}}
""".strip()

    try:
        response = client.responses.create(
            model=settings.openai_model,
            input=prompt,
            temperature=0.9,
        )
        content = response.output_text.strip()
        payload = json.loads(content)
        return _coerce_script(payload, topic, duration)
    except Exception as exc:
        logger.exception("Echec génération script via OpenAI, fallback local activé: %s", exc)
        return _fallback_script(topic, duration)
