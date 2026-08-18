from brainchain.label_calibration import calibrate_1h


def test_calibrate_1h_derives_distribution_from_temporal_rows():
    rows = [
        {"source_id": "A", "captured_at": "2026-01-01T00:00:00Z", "price_usd": 100},
        {"source_id": "A", "captured_at": "2026-01-01T00:30:00Z", "price_usd": 101},
        {"source_id": "A", "captured_at": "2026-01-01T02:00:00Z", "price_usd": 105},
        {"source_id": "B", "captured_at": "2026-01-01T00:00:00Z", "price_usd": 200},
        {"source_id": "B", "captured_at": "2026-01-01T00:20:00Z", "price_usd": 198},
    ]
    result = calibrate_1h(rows)
    assert result["eligible"] == 2
    assert result["multipliers"]["min"] == 0.99
    assert result["multipliers"]["max"] == 1.01
