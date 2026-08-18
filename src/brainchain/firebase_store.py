"""Firebase Realtime Database persistence adapter.

Credentials are supplied through environment variables and are never stored in
Git. Snapshots are immutable historical observations, while ``latest`` keeps a
cheap point-in-time view for downstream feature engineering.
"""

from __future__ import annotations

import json
import os
from typing import Any, Iterable, Mapping


class FirebaseStoreError(RuntimeError):
    """Raised when Firebase cannot be initialized or written to."""


class FirebaseStore:
    def __init__(self, database_url: str | None = None, credentials_json: str | None = None):
        self.database_url = database_url or os.getenv("FIREBASE_DATABASE_URL")
        self.credentials_json = credentials_json or os.getenv("FIREBASE_CREDENTIALS_JSON")
        self._db = None
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return
        if not self.database_url:
            raise FirebaseStoreError("FIREBASE_DATABASE_URL is not configured")
        if not self.credentials_json:
            raise FirebaseStoreError("FIREBASE_CREDENTIALS_JSON is not configured")

        try:
            import firebase_admin
            from firebase_admin import credentials, db

            credential = credentials.Certificate(json.loads(self.credentials_json))
            if not firebase_admin._apps:
                firebase_admin.initialize_app(credential, {"databaseURL": self.database_url})
            self._db = db
            self._initialized = True
        except Exception as exc:  # firebase-admin exposes several concrete init errors
            raise FirebaseStoreError(f"Firebase initialization failed: {exc}") from exc

    def write_snapshots(self, snapshots: Iterable[Mapping[str, Any]]) -> int:
        """Persist immutable history and update the latest view for each asset.

        Historical observations live at ``snapshots/<asset>/<timestamp>`` and
        are never overwritten by a later collection. ``latest/<asset>`` is a
        convenience index containing the most recent observation seen by this
        process. The timestamp key is deterministic, so retrying the same
        captured snapshot is idempotent.
        """
        self.initialize()
        count = 0
        for snapshot in snapshots:
            source_id = snapshot.get("source_id")
            captured_at = snapshot.get("captured_at")
            if source_id is None or captured_at is None:
                raise FirebaseStoreError("snapshot requires source_id and captured_at")

            # Firebase keys cannot contain '.', '#', '$', '[', or ']'. ISO 8601
            # contains ':' which is safe, but replace '.' for a compact key.
            timestamp_key = str(captured_at).replace(".", "_")
            snapshot_data = dict(snapshot)
            history_path = f"snapshots/{source_id}/{timestamp_key}"
            latest_path = f"latest/{source_id}"

            self._db.reference(history_path).set(snapshot_data)
            self._db.reference(latest_path).set(snapshot_data)
            count += 1
        return count
