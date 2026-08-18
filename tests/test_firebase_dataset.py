from brainchain.firebase_dataset import flatten_snapshots, prepare_dataset


def test_flatten_supports_firebase_map_shape():
    payload = {"a": {"id": "BTC", "captured_at": "2026-01-02T00:00:00+00:00"}}
    rows = flatten_snapshots(payload)
    assert rows[0]["source_id"] == "BTC"


def test_prepare_dataset_is_deterministic():
    payload = [
        {"source_id": "ETH", "captured_at": "2026-01-02T00:00:00+00:00"},
        {"source_id": "BTC", "captured_at": "2026-01-03T00:00:00+00:00"},
        {"source_id": "BTC", "captured_at": "2026-01-01T00:00:00+00:00"},
    ]
    rows = prepare_dataset(payload)
    assert [(r["source_id"], r["captured_at"]) for r in rows] == [
        ("BTC", "2026-01-01T00:00:00+00:00"),
        ("BTC", "2026-01-03T00:00:00+00:00"),
        ("ETH", "2026-01-02T00:00:00+00:00"),
    ]
