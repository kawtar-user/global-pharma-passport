from __future__ import annotations

import argparse
import sys

from src.neuroshorts.config import Settings, setup_logging
from src.neuroshorts.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generation automatique de YouTube Shorts faceless en neuroscience.")
    parser.add_argument("--topic", required=True, help="Sujet du Short, par exemple: Pourquoi la dopamine détruit ta concentration")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = Settings()
    settings.ensure_directories()
    setup_logging(settings.log_level)
    output_path = run_pipeline(args.topic, settings)
    print(f"Video exportee: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

