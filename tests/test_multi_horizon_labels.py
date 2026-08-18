from brainchain.multi_horizon_labels import LabelConfig, build_labels


def test_labels_use_future_only_and_multiple_thresholds():
    rows = [
        {"source_id": "X", "captured_at": f"2026-01-0{i}T00:00:00Z", "price": p}
        for i, p in enumerate([1, 1.5, 2, 5, 10], start=1)
    ]
    labels = build_labels(rows, LabelConfig(horizons=(1, 2, 3), thresholds=(2, 5, 10)))
    first = next(x for x in labels if x["captured_at"].startswith("2026-01-01"))
    assert first["entry_price"] == 1
    assert first["max_multiplier_1"] == 1.5
    assert first["max_multiplier_2"] == 2
    assert first["max_multiplier_3"] == 5
    assert first["hit_2x_2"] is True
    assert first["hit_5x_3"] is True
    assert first["hit_10x_3"] is False


def test_incomplete_future_window_is_excluded():
    rows = [
        {"source_id": "X", "captured_at": str(i), "price": 1.0 + i}
        for i in range(3)
    ]
    labels = build_labels(rows, LabelConfig(horizons=(2,), thresholds=(2,)))
    assert len(labels) == 1
