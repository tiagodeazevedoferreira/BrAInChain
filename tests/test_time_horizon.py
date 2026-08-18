from datetime import datetime, timezone

from brainchain.time_horizon import future_window


def test_future_window_uses_wall_clock_time():
    rows = [
        {"captured_at": "2026-01-01T00:30:00+00:00"},
        {"captured_at": "2026-01-01T02:00:00+00:00"},
        {"captured_at": "2026-01-01T07:00:00+00:00"},
    ]
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    result = future_window(rows, start, 6)
    assert len(result) == 2
    assert result[-1]["captured_at"].startswith("2026-01-01T02")
