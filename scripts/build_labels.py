"""CLI helper for building training labels from in-memory/exported snapshots."""
from __future__ import annotations

import json
import sys

from brainchain.label_engine import build_labels


def main() -> int:
    payload = json.load(sys.stdin)
    if not isinstance(payload, list):
        raise SystemExit("input must be a JSON list of snapshots")
    json.dump(build_labels(payload), sys.stdout, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
