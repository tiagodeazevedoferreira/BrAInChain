from __future__ import annotations

import argparse
import json

from brainchain.dataset_builder import build_dataset
from brainchain.firebase_reader import FirebaseReader
from brainchain.label_magnitude import summarize_label_magnitude


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-assets", type=int, default=0)
    args = parser.parse_args()
    rows = FirebaseReader().read_snapshots()
    if args.max_assets > 0:
        rows = rows[: args.max_assets]
    dataset = build_dataset(rows)
    print(json.dumps(summarize_label_magnitude(dataset), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
