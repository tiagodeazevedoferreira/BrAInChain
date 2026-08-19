from datetime import datetime, timezone

from brainchain.training_labels_1h import build_1h_labels


def snapshot(source_id: str, captured_at: str, price_usd: float) -> dict:
    return {"source_id": source_id, "captured_at": captured_at, "price_usd": price_usd}


def test_builds_up_down_and_neutral_at_promoted_threshold() -> None:
    rows = [
        snapshot("up", "2026-08-19T10:00:00+00:00", 100.0),
        snapshot("up", "2026-08-19T11:00:00+00:00", 100.25),
        snapshot("down", "2026-08-19T10:00:00+00:00", 100.0),
        snapshot("down", "2026-08-19T11:00:00+00:00", 99.75),
        snapshot("neutral", "2026-08-19T10:00:00+00:00", 100.0),
        snapshot("neutral", "2026-08-19T11:00:00+00:00", 100.10),
    ]

    labels = {row["source_id"]: row["target_1h_label"] for row in build_1h_labels(rows)}

    assert labels == {"up": "up", "down": "down", "neutral": "neutral"}


def test_does_not_use_observation_before_one_hour() -> None:
    rows = [
        snapshot("btc", "2026-08-19T10:00:00+00:00", 100.0),
        snapshot("btc", "2026-08-19T10:30:00+00:00", 101.0),
        snapshot("btc", "2026-08-19T11:00:00+00:00", 100.0),
    ]

    labels = build_1h_labels(rows)

    assert labels[0]["target_1h_return"] == 0.0
    assert labels[0]["target_1h_label"] == "neutral"


def test_incomplete_horizon_is_not_labeled() -> None:
    rows = [snapshot("btc", "2026-08-19T10:00:00+00:00", 100.0)]

    assert build_1h_labels(rows) == []


# Keep timezone parsing explicit in the test fixture contract.
def test_fixture_is_aware_datetime() -> None:
    value = datetime.fromisoformat("2026-08-19T10:00:00+00:00")
    assert value.tzinfo == timezone.utc
