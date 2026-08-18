"""CLI entry point for point-in-time feature generation.

This first version operates on a JSON file containing one chronological history
list. Firebase integration will be added after the pure feature layer is
validated by CI.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from brainchain.feature_engineering import build_features


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    history = json.loads(args.input.read_text(encoding="utf-8"))
    features = build_features(history)
    args.output.write_text(json.dumps(features, indent=2), encoding="utf-8")
    print(f"Generated {len(features)} feature rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
