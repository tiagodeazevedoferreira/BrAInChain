from datetime import datetime, timedelta, timezone

import pytest

from brainchain.labels import ONE_HOUR_RETURN_THRESHOLD, build_time_labels


def test_promoted_threshold_is_symmetric():
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = [
        {"source_id": "1", "captured_at": t0, "price_usd": 100.0},
        {"source_id": "1", "captured_at": t0 + timedelta(minutes=50), "price_usd": 100.25},
        {"source_id": "2", "captured_at": t0, "price_usd": 100.0},
        {"source_id": "2", "captured_at": t0 + timedelta(minutes=50), "price_usd": 99.75},
        {"source_id": "3", "captured_at": t0, "price_usd": 100.0},
        {"source_id": "3", "captured_at": t0 + timedelta(minutes=50), "price_usd": 100.20},
    ]

    labeled = build_time_labels(rows, horizons_hours=(1,))
    by_asset = {row["source_id"]: row for row in labeled if row["captured_at"] == t0}

    assert ONE_HOUR_RETURN_THRESHOLD == 0.0025
    assert by_asset["1"]["label_1h_class"] == "up"
    assert by_asset["2"]["label_1h_class"] == "down"
    assert by_asset["3"]["label_1h_class"] == "neutral"


def test_temporal_window_does_not_use_observations_after_one_hour():
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = [
        {"source_id": "1", "captured_at": t0, "price_usd": 100.0},
        {"source_id": "1", "captured_at": t0 + timedelta(minutes=10), "price_usd": 120.0},
        {"source_id": "1", "captured_at": t0 + timedelta(hours=1, minutes=10), "price_usd": 101.0},
    ]

    labeled = build_time_labels(rows, horizons_hours=(1,))
    first = next(row for row in labeled if row["captured_at"] == t0)
    assert first["label_1h_max_return"] == pytest.approx(0.20)
    assert first["label_1h_class"] == "up"
