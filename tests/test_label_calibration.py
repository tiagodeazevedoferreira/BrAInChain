from brainchain.label_calibration import calibrate_1h


def test_calibrate_1h_reports_distribution():
    rows = [
        {"price": 100, "future_price_1h": 101},
        {"price": 100, "future_price_1h": 102},
        {"price": 100, "future_price_1h": 99},
    ]
    result = calibrate_1h(rows)
    assert result["eligible"] == 3
    assert result["multipliers"]["median"] == 1.01


def test_calibrate_1h_derives_future_by_same_asset():
    rows = [
        {"source_id": "A", "captured_at": "2026-01-01T00:00:00Z", "price": 100},
        {"source_id": "A", "captured_at": "2026-01-01T00:30:00Z", "price": 110},
        {"source_id": "A", "captured_at": "2026-01-01T02:00:00Z", "price": 120},
        {"source_id": "B", "captured_at": "2026-01-01T00:10:00Z", "price": 50},
        {"source_id": "B", "captured_at": "2026-01-01T02:10:00Z", "price": 75},
    ]
    result = calibrate_1h(rows)
    assert result["eligible"] == 1
    assert result["multipliers"]["median"] == 1.10
