from brainchain.training_dataset import build_training_rows, temporal_split


def test_join_keeps_targets_separate_from_features():
    features = [{"source_id": 1, "captured_at": "2026-01-01T00:00:00Z", "momentum": 2.0}]
    labels = [{"source_id": 1, "captured_at": "2026-01-01T00:00:00Z", "target_2x_24h": 1}]
    rows = build_training_rows(features, labels)
    assert rows == [{"source_id": 1, "captured_at": "2026-01-01T00:00:00Z", "momentum": 2.0, "target_2x_24h": 1}]


def test_temporal_split_does_not_shuffle():
    rows = [{"captured_at": f"2026-01-0{i}T00:00:00Z", "value": i} for i in range(1, 11)]
    split = temporal_split(rows)
    assert split.train[-1]["value"] < split.validation[0]["value"]
    assert split.validation[-1]["value"] < split.test[0]["value"]
