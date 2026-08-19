from brainchain.modeling_1h import FEATURE_COLUMNS, prepare_xy, train_1h_baseline


def row(label):
    return {**{name: 1.0 for name in FEATURE_COLUMNS}, "target_1h_label": label}


def test_prepare_xy_maps_promoted_1h_labels():
    X, y = prepare_xy([row("down"), row("neutral"), row("up"), row("unknown")])
    assert len(X) == 3
    assert y == [0, 1, 2]


def test_prepare_xy_ignores_missing_features():
    broken = row("up")
    broken["volume_change"] = None
    X, y = prepare_xy([broken])
    assert X == []
    assert y == []


def test_1h_baseline_requires_two_classes():
    try:
        train_1h_baseline([row("up"), row("up")], [row("down")])
    except ValueError as exc:
        assert "at least two classes" in str(exc)
    else:
        raise AssertionError("expected ValueError")
