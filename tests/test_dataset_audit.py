from brainchain.dataset_audit import audit_rows


def test_audit_reports_assets_and_cadence():
    rows = [
        {"source_id": "BTC", "captured_at": "2026-01-01T00:00:00Z", "price": 1},
        {"source_id": "BTC", "captured_at": "2026-01-01T01:00:00Z", "price": 2},
        {"source_id": "BTC", "captured_at": "2026-01-01T02:00:00Z", "price": 3},
        {"source_id": "ETH", "captured_at": "2026-01-01T00:00:00Z", "price": 1},
    ]
    result = audit_rows(rows)
    assert result["total_rows"] == 4
    assert result["assets"] == 2
    assert result["observations_per_asset"]["BTC"] == 3
    assert result["cadence_hours"]["median"] == 1
    assert result["horizon_observations_available"]["1"] == 1
