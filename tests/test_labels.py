from brainchain.labels import build_time_labels


def test_build_time_labels_uses_real_time_and_max_future_price():
    rows = [
        {"source_id": "BTC", "captured_at": "2026-01-01T00:00:00Z", "price_usd": 100},
        {"source_id": "BTC", "captured_at": "2026-01-01T00:30:00Z", "price_usd": 110},
        {"source_id": "BTC", "captured_at": "2026-01-01T02:00:00Z", "price_usd": 150},
        {"source_id": "BTC", "captured_at": "2026-01-01T06:00:00Z", "price_usd": 200},
    ]
    result = build_time_labels(rows, horizons_hours=(1, 6))
    first = result[0]
    assert first["label_1h_max_multiple"] == 1.1
    assert first["label_6h_max_multiple"] == 2.0
    assert first["label_6h_hit_2x"] == 1
