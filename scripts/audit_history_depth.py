from __future__ import annotations

import argparse
import json

from brainchain.firebase_reader import FirebaseReader
from brainchain.history_depth import audit_history_depth


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-assets", type=int, default=0)
    args = parser.parse_args()
    rows = FirebaseReader().read_snapshots()
    if args.max_assets > 0:
        rows = rows[: args.max_assets]
    print(json.dumps(audit_history_depth(rows), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
