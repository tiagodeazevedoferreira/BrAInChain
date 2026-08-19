"""CLI for building the first leakage-safe 1h training dataset."""
from __future__ import annotations

import json
import sys

from brainchain.training_dataset import build_1h_training_rows, temporal_split


def main() -> int:
    payload = json.load(sys.stdin)
    snapshots = payload.get("snapshots", [])
    rows = build_1h_training_rows(snapshots)
    split = temporal_split(rows)
    json.dump(
        {"train": split.train, "validation": split.validation, "test": split.test},
        sys.stdout,
        ensure_ascii=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
