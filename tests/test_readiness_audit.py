from brainchain.readiness_audit import audit_readiness


def test_readiness_reports_horizon_gaps():
    rows = [
        {"source_id": "A", "captured_at": "2026-01-01T00:00:00Z"},
        {"source_id": "A", "captured_at": "2026-01-01T01:00:00Z"},
        {"source_id": "A", "captured_at": "2026-01-01T02:00:00Z"},
        {"source_id": "B", "captured_at": "2026-01-01T00:00:00Z"},
        {"source_id": "B", "captured_at": "2026-01-01T00:30:00Z"},
    ]
    result = audit_readiness(rows)
    assert result["assets"] == 2
    assert result["max_history_hours"] == 2.0
    assert result["horizons"]["1h"]["assets_with_history"] == 1
    assert result["horizons"]["6h"]["assets_with_history"] == 0
    assert result["horizons"]["6h"]["hours_until_first_asset"] == 4.0
