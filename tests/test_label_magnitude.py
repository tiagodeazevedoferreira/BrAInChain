from brainchain.label_magnitude import summarize_label_magnitude


def test_summarize_label_magnitude():
    dataset = [
        {"label_6h_max_multiple": 1.0},
        {"label_6h_max_multiple": 1.1},
        {"label_6h_max_multiple": 1.5},
        {"label_6h_max_multiple": 2.0},
    ]
    summary = summarize_label_magnitude(dataset, horizons_hours=(6,))
    assert summary["6h"]["eligible"] == 4
    assert summary["6h"]["median"] == 1.3
    assert summary["6h"]["max"] == 2.0
