from brainchain.dataset_builder import build_dataset, training_counts


def test_dataset_builder_keeps_features_and_time_labels():
    rows = [
        {"source_id": "BTC", "captured_at": "2026-01-01T00:00:00Z", "price_usd": 100, "market_cap_usd": 1000, "volume_24h_usd": 100, "percent_change_1h": 1, "percent_change_24h": 5, "percent_change_7d": 10, "rank": 1},
        {"source_id": "BTC", "captured_at": "2026-01-01T00:30:00Z", "price_usd": 110, "market_cap_usd": 1100, "volume_24h_usd": 110, "percent_change_1h": 2, "percent_change_24h": 6, "percent_change_7d": 11, "rank": 1},
        {"source_id": "BTC", "captured_at": "2026-01-01T02:00:00Z", "price_usd": 150, "market_cap_usd": 1200, "volume_24h_usd": 120, "percent_change_1h": 3, "percent_change_24h": 7, "percent_change_7d": 12, "rank": 1},
    ]
    dataset = build_dataset(rows, horizons_hours=(1, 6))
    assert len(dataset) == 3
    assert dataset[0]["volume_market_cap_ratio"] == 0.1
    assert dataset[0]["label_1h_max_multiple"] == 1.1
    assert dataset[0]["label_6h_max_multiple"] == 1.5
    assert training_counts(dataset, horizons_hours=(1, 6)) == {"1h": 2, "6h": 1}
