import pytest

from brainchain.baseline_metrics import balanced_accuracy, macro_f1, majority_class


def test_majority_class_is_deterministic_for_common_label() -> None:
    assert majority_class(["neutral", "up", "neutral", "down", "neutral"]) == "neutral"


def test_balanced_accuracy() -> None:
    assert balanced_accuracy(["down", "neutral", "up"], ["down", "neutral", "up"]) == 1.0
    assert balanced_accuracy(["down", "neutral", "up"], ["neutral", "neutral", "neutral"]) == pytest.approx(1 / 3)


def test_macro_f1() -> None:
    assert macro_f1(["down", "neutral", "up"], ["down", "neutral", "up"]) == 1.0
    assert macro_f1(["down", "neutral", "up"], ["neutral", "neutral", "neutral"]) == pytest.approx(1 / 6)
