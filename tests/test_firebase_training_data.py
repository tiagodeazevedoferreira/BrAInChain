from brainchain.firebase_training_data import build_training_rows


def test_build_training_rows_uses_snapshots():
    payload = {
        "a": {"source_id": "BTC", "captured_at": "2026-01-02T00:00:00+00:00"},
        "b": {"source_id": "BTC", "captured_at": "2026-01-01T00:00:00+00:00"},
    }
    rows = build_training_rows(payload)
    assert len(rows) == 2
    assert rows[0]["captured_at"] < rows[1]["captured_at"]
