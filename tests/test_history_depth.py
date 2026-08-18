from brainchain.history_depth import audit_history_depth


def test_history_depth_groups_by_asset():
    rows = [
        {"source_id": "A", "captured_at": "2026-01-01T00:00:00Z"},
        {"source_id": "A", "captured_at": "2026-01-01T02:00:00Z"},
        {"source_id": "B", "captured_at": "2026-01-01T00:00:00Z"},
        {"source_id": "B", "captured_at": "2026-01-01T00:30:00Z"},
    ]
    result = audit_history_depth(rows)
    assert result["assets"] == 2
    assert result["history_hours"]["min"] == 0.5
    assert result["history_hours"]["max"] == 2.0
    assert result["assets_with_1h_history"] == 1
    assert result["assets_with_6h_history"] == 0
