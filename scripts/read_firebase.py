"""Read Firebase Realtime Database nodes using repository Secrets."""
from __future__ import annotations

import json
import os

from brainchain.firebase_reader import FirebaseReader


def main() -> int:
    url = os.environ.get("FIREBASE_DATABASE_URL")
    credentials = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    if not url or not credentials:
        raise SystemExit("Firebase Secrets are not configured")

    reader = FirebaseReader(database_url=url, credentials_json=credentials)
    latest = reader.read("/latest")
    snapshots = reader.read("/snapshots")

    print(json.dumps({
        "latest_records": len(latest) if isinstance(latest, dict) else 0,
        "snapshot_records": len(snapshots) if isinstance(snapshots, dict) else 0,
        "latest_type": type(latest).__name__,
        "snapshots_type": type(snapshots).__name__,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
