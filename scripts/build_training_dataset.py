"""CLI for joining feature and label JSON exports and creating temporal splits."""
from __future__ import annotations

import json
import sys

from brainchain.training_dataset import build_training_rows, temporal_split


def main() -> int:
    payload = json.load(sys.stdin)
    features = payload.get("features", [])
    labels = payload.get("labels", [])
    rows = build_training_rows(features, labels)
    split = temporal_split(rows)
    json.dump({"train": split.train, "validation": split.validation, "test": split.test}, sys.stdout, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
