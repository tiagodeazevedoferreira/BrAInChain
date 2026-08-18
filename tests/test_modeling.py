import pytest
from brainchain.modeling import FEATURE_COLUMNS, prepare_xy


def row(label):
    return {**{name: 1.0 for name in FEATURE_COLUMNS}, "target_2x_24h": label}


def test_prepare_xy_ignores_unknown_labels_and_missing_features():
    X, y = prepare_xy([row(1), row(0), row(None)], "target_2x_24h")
    assert len(X) == 2 and y == [1, 0]
    broken = row(1); broken["volume_change"] = None
    X, y = prepare_xy([broken], "target_2x_24h")
    assert X == [] and y == []


def test_baseline_requires_two_classes():
    from brainchain.modeling import train_baseline
    with pytest.raises(ValueError, match="both positive and negative"):
        train_baseline([row(1), row(1)], [row(0)], "target_2x_24h")
