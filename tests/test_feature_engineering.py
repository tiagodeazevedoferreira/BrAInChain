from brainchain.feature_engineering import build_features


def test_features_are_point_in_time_and_backward_only():
    history = [
        {"timestamp": "2026-01-01T00:00:00Z", "coin_id": 1, "symbol": "ABC", "price": 1, "market_cap": 1000, "volume_24h": 100},
        {"timestamp": "2026-01-01T01:00:00Z", "coin_id": 1, "symbol": "ABC", "price": 2, "market_cap": 2000, "volume_24h": 200},
        {"timestamp": "2026-01-01T02:00:00Z", "coin_id": 1, "symbol": "ABC", "price": 6, "market_cap": 6000, "volume_24h": 600},
    ]
    features = build_features(history)

    assert len(features) == 3
    assert features[0]["is_first_observation"] is True
    assert features[1]["return_since_previous"] == 100.0
    assert features[2]["return_since_previous"] == 200.0
    assert features[2]["price_acceleration"] == 100.0
    assert features[2]["volume_market_cap_ratio"] == 0.1


def test_missing_previous_values_are_safe():
    history = [{"timestamp": "2026-01-01T00:00:00Z", "coin_id": 1, "symbol": "ABC", "price": 1}]
    features = build_features(history)
    assert features[0]["return_since_previous"] is None
    assert features[0]["price_acceleration"] is None
