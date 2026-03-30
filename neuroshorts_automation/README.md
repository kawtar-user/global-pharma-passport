# NeuroShorts Automation

Pipeline Python modulaire pour generer automatiquement des YouTube Shorts faceless en francais sur la neuroscience.

## Ce que fait le systeme

1. prend un sujet en entree
2. genere un script court ultra engageant
3. cree une voix off realiste
4. decoupe le script en 8 scenes
5. genere un prompt video cinematographique Sora pour chaque scene
6. sauvegarde les prompts dans `scripts/sora_prompts.txt`
7. cree `subtitles/subtitles.srt`
8. assemble voix off, clips, sous-titres et musique de fond
9. exporte un MP4 vertical H.264 pret pour YouTube Shorts

## Structure

```text
neuroshorts_automation/
├── input/
├── scripts/
├── audio/
├── clips/
├── subtitles/
├── exports/
├── config/
├── src/neuroshorts/
├── .env.example
├── main.py
└── requirements.txt
```

## Installation

```bash
cd /Users/kawtar/Documents/New\ project\ 3/neuroshorts_automation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Ajoute ensuite ta cle OpenAI dans `.env`.

## Execution

```bash
python main.py --topic "Pourquoi la dopamine détruit ta concentration"
```

## Sorties generees

- `scripts/script_package.json` : package editorial complet
- `scripts/script.txt` : script voix off
- `scripts/youtube_metadata.txt` : titre, description, hooks, hashtags
- `scripts/sora_prompts.txt` : prompts scene par scene
- `audio/voiceover.wav` : voix off
- `subtitles/subtitles.srt` : sous-titres
- `exports/<slug>.mp4` : video finale

## Gestion des clips

Le systeme fonctionne de deux manieres :

- si tu poses des clips reels dans `clips/scene_1.mp4` a `clips/scene_8.mp4`, ils seront utilises automatiquement
- sinon, le pipeline cree des clips visuels stylises temporaires pour que l'export final fonctionne quand meme

Cela permet de generer d'abord les prompts Sora, puis de remplacer facilement les clips avec les rendus reels.

## Notes techniques

- format video : `1080x1920`
- duree cible : environ `35 a 55 sec`
- sous-titres lisibles centres bas
- cuts rapides entre scenes
- leger zoom sur les plans
- export final en `H.264` (`libx264`) + audio AAC
- musique de fond discrete generee automatiquement

## Fonctions principales

- `generate_script(topic)`
- `generate_voice(script)`
- `split_into_scenes(script)`
- `build_sora_prompts(scene_data)`
- `generate_subtitles(script)`
- `assemble_video(audio, clips, subtitles, output)`

## Conseils

- pour une voix vraiment premium, renseigne `OPENAI_API_KEY`
- si la cle OpenAI est absente, le script passe en mode fallback local pour le texte et la voix
- pour un resultat visuel premium, genere tes videos Sora a partir de `scripts/sora_prompts.txt` puis place-les dans `clips/`
