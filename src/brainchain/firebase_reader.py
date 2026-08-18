"""Authenticated Firebase Realtime Database reader.

Credentials are supplied at runtime through environment variables and are never
stored in source control.
"""
from __future__ import annotations

import json
import os
from typing import Any

import firebase_admin
from firebase_admin import credentials, db


class FirebaseReader:
    def __init__(self, database_url: str | None = None, credentials_json: str | None = None):
        self.database_url = database_url or os.environ.get("FIREBASE_DATABASE_URL")
        self.credentials_json = credentials_json or os.environ.get("FIREBASE_CREDENTIALS_JSON")
        if not self.database_url:
            raise ValueError("FIREBASE_DATABASE_URL is required")
        if not self.credentials_json:
            raise ValueError("FIREBASE_CREDENTIALS_JSON is required")
        self._initialize()

    def _initialize(self) -> None:
        try:
            firebase_admin.get_app()
        except ValueError:
            service_account = json.loads(self.credentials_json)
            cred = credentials.Certificate(service_account)
            firebase_admin.initialize_app(cred, {"databaseURL": self.database_url})

    def read(self, path: str = "/") -> Any:
        """Read a Firebase Realtime Database path using service-account auth."""
        return db.reference(path).get()

    def read_snapshots(self) -> list[dict[str, Any]]:
        """Read and normalize the historical snapshot dataset."""
        from brainchain.firebase_training_data import build_training_rows

        payload = self.read("/snapshots") or {}
        return build_training_rows(payload)
