from brainchain.training_dataset_1h import build_1h_training_rows


def test_1h_training_rows_keep_only_complete_horizons() -> None:
    snapshots = [
        {"source_id": "btc", "captured_at": "2026-08-19T10:00:00+00:00", "price_usd": 100.0},
        {"source_id": "btc", "captured_at": "2026-08-19T10:30:00+00:00", "price_usd": 100.1},
        {"source_id": "btc", "captured_at": "2026-08-19T11:00:00+00:00", "price_usd": 100.3},
        {"source_id": "btc", "captured_at": "2026-08-19T12:00:00+00:00", "price_usd": 100.2},
    ]

    rows = build_1h_training_rows(snapshots)

    assert rows
    assert all("target_1h_label" in row for row in rows)
    assert all("target_1h_return" in row for row in rows)
    assert [row["captured_at"] for row in rows] == sorted(row["captured_at"] for row in rows)
