from brainchain.label_distribution import summarize_label_distribution


def test_summarize_label_distribution_counts_thresholds():
    rows = [
        {"label_6h_max_multiple": 1.5},
        {"label_6h_max_multiple": 2.0},
        {"label_6h_max_multiple": 5.0},
        {"label_6h_max_multiple": 10.0},
        {"label_6h_max_multiple": None},
    ]
    assert summarize_label_distribution(rows, horizons_hours=(6,)) == {
        "6h": {"eligible": 4, "hit_2x": 3, "hit_5x": 2, "hit_10x": 1}
    }
