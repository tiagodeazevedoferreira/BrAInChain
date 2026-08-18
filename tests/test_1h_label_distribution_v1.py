from datetime import datetime, timezone


def classify(rows):
    rows = sorted(rows, key=lambda r: r["captured_at"])
    eligible = 0
    labels = {"up_2pct": 0, "down_2pct": 0, "neutral": 0}
    for i, row in enumerate(rows):
        current = row["price"]
        target = row["captured_at"] + __import__("datetime").timedelta(hours=1)
        future = None
        for candidate in rows[i + 1 :]:
            if candidate["captured_at"] <= target:
                future = candidate
                continue
            break
        if future is None:
            continue
        elapsed = future["captured_at"] - row["captured_at"]
        if elapsed < __import__("datetime").timedelta(minutes=45):
            continue
        eligible += 1
        multiplier = future["price"] / current
        if multiplier >= 1.02:
            labels["up_2pct"] += 1
        elif multiplier <= 0.98:
            labels["down_2pct"] += 1
        else:
            labels["neutral"] += 1
    return eligible, labels


def test_uses_temporal_window_not_next_row():
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = [
        {"captured_at": t0, "price": 100.0},
        {"captured_at": t0.replace(minute=10), "price": 120.0},
        {"captured_at": t0.replace(minute=50), "price": 101.0},
    ]
    eligible, labels = classify(rows)
    assert eligible == 1
    assert labels["up_2pct"] == 0
    assert labels["neutral"] == 1
