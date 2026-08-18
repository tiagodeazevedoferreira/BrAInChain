from brainchain.features import build_features


def test_build_features_calculates_volume_market_cap_ratio():
    row = {
        "price_usd": 2.0,
        "market_cap_usd": 100.0,
        "volume_24h_usd": 25.0,
        "percent_change_1h": 1.5,
        "percent_change_24h": 8.0,
        "percent_change_7d": 20.0,
        "rank": 10,
    }
    result = build_features(row)
    assert result["price_usd"] == 2.0
    assert result["volume_market_cap_ratio"] == 0.25
    assert result["percent_change_24h"] == 8.0
