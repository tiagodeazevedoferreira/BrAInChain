from brainchain.label_engine import build_labels


def test_labels_are_based_only_on_future_prices():
    rows = [
        {"source_id": 1, "captured_at": "2026-01-01T00:00:00+00:00", "price_usd": 1.0},
        {"source_id": 1, "captured_at": "2026-01-01T12:00:00+00:00", "price_usd": 2.0},
        {"source_id": 1, "captured_at": "2026-01-02T00:00:00+00:00", "price_usd": 5.0},
        {"source_id": 1, "captured_at": "2026-01-08T00:00:00+00:00", "price_usd": 10.0},
    ]
    labels = build_labels(rows)
    first = labels[0]
    assert first["target_2x_24h"] == 1
    assert first["target_5x_24h"] == 1
    assert first["target_5x_168h"] == 1


def test_incomplete_horizon_is_unknown_not_failure():
    rows = [
        {"source_id": 7, "captured_at": "2026-01-01T00:00:00+00:00", "price_usd": 1.0},
        {"source_id": 7, "captured_at": "2026-01-01T01:00:00+00:00", "price_usd": 1.1},
    ]
    labels = build_labels(rows)
    assert labels[0]["target_2x_24h"] is None
