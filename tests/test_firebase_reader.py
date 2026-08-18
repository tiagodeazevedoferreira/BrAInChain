import json

import pytest

from brainchain.firebase_reader import FirebaseReader


def test_missing_database_url_is_rejected(monkeypatch):
    monkeypatch.delenv("FIREBASE_DATABASE_URL", raising=False)
    monkeypatch.setenv("FIREBASE_CREDENTIALS_JSON", json.dumps({"type": "service_account"}))
    with pytest.raises(ValueError, match="FIREBASE_DATABASE_URL"):
        FirebaseReader()


def test_missing_credentials_are_rejected(monkeypatch):
    monkeypatch.setenv("FIREBASE_DATABASE_URL", "https://example.firebaseio.com")
    monkeypatch.delenv("FIREBASE_CREDENTIALS_JSON", raising=False)
    with pytest.raises(ValueError, match="FIREBASE_CREDENTIALS_JSON"):
        FirebaseReader()
