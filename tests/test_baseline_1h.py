from brainchain.baseline_1h import balanced_accuracy, evaluate_baseline, majority_label


def test_majority_label_is_deterministic_on_ties():
    assert majority_label(["up", "down", "neutral"]) == "down"


def test_majority_baseline_on_balanced_classes():
    result = evaluate_baseline(["down", "neutral", "up"] * 3)
    assert result["strategy"] == "majority_class"
    assert result["majority_label"] == "down"
    assert result["balanced_accuracy"] == 1 / 3
    assert result["macro_f1"] == 1 / 6


def test_balanced_accuracy_perfect_predictions():
    labels = ["down", "neutral", "up", "down"]
    assert balanced_accuracy(labels, labels) == 1.0
