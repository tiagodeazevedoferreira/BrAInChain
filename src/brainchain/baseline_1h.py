"""Deterministic baselines and metrics for the 1h classification target."""
from __future__ import annotations

from collections import Counter
from typing import Iterable, Mapping, Sequence

LABELS = ("down", "neutral", "up")


def majority_label(labels: Iterable[str]) -> str:
    counts = Counter(labels)
    if not counts:
        raise ValueError("labels must not be empty")
    return min(LABELS, key=lambda label: (-counts.get(label, 0), LABELS.index(label)))


def majority_predictions(labels: Sequence[str]) -> list[str]:
    label = majority_label(labels)
    return [label] * len(labels)


def balanced_accuracy(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    if len(y_true) != len(y_pred) or not y_true:
        raise ValueError("y_true and y_pred must have equal non-zero length")
    recalls = []
    for label in LABELS:
        actual = sum(value == label for value in y_true)
        if actual:
            recalls.append(sum(a == label and p == label for a, p in zip(y_true, y_pred)) / actual)
    return sum(recalls) / len(recalls)


def macro_f1(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    if len(y_true) != len(y_pred) or not y_true:
        raise ValueError("y_true and y_pred must have equal non-zero length")
    scores = []
    for label in LABELS:
        tp = sum(a == label and p == label for a, p in zip(y_true, y_pred))
        fp = sum(a != label and p == label for a, p in zip(y_true, y_pred))
        fn = sum(a == label and p != label for a, p in zip(y_true, y_pred))
        if tp == 0 and (fp or fn):
            scores.append(0.0)
            continue
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return sum(scores) / len(scores)


def evaluate_baseline(labels: Sequence[str]) -> Mapping[str, float | str]:
    prediction = majority_label(labels)
    predictions = [prediction] * len(labels)
    return {
        "strategy": "majority_class",
        "majority_label": prediction,
        "balanced_accuracy": balanced_accuracy(labels, predictions),
        "macro_f1": macro_f1(labels, predictions),
    }
