from brainchain.temporal_audit import audit_temporal_coverage


def test_temporal_coverage_respects_each_horizon():
    rows = [
        {"captured_at": "2026-01-01T00:00:00Z"},
        {"captured_at": "2026-01-01T00:30:00Z"},
        {"captured_at": "2026-01-01T02:00:00Z"},
        {"captured_at": "2026-01-01T10:00:00Z"},
    ]
    result = audit_temporal_coverage(rows, horizons_hours=(1, 6, 24))
    assert result["1h"]["eligible"] == 1
    assert result["6h"]["eligible"] == 2
    assert result["24h"]["eligible"] == 3
    assert result["1h"]["max_future_age_hours"] == 0.5
    assert result["6h"]["max_future_age_hours"] == 2.0
