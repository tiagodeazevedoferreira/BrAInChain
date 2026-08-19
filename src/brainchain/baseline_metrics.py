"""Small dependency-free classification metrics for temporal baseline evaluation."""
from __future__ import annotations

from collections import Counter
from typing import Iterable


def majority_class(values: Iterable[str]) -> str:
    labels = list(values)
    if not labels:
        raise ValueError("at least one label is required")
    return Counter(labels).most_common(1)[0][0]


def balanced_accuracy(y_true: Iterable[str], y_pred: Iterable[str]) -> float:
    truth = list(y_true)
    pred = list(y_pred)
    if len(truth) != len(pred) or not truth:
        raise ValueError("y_true and y_pred must have equal non-zero length")
    classes = sorted(set(truth))
    recalls = []
    for label in classes:
        indices = [i for i, value in enumerate(truth) if value == label]
        recalls.append(sum(pred[i] == label for i in indices) / len(indices))
    return sum(recalls) / len(recalls)


def macro_f1(y_true: Iterable[str], y_pred: Iterable[str]) -> float:
    truth = list(y_true)
    pred = list(y_pred)
    if len(truth) != len(pred) or not truth:
        raise ValueError("y_true and y_pred must have equal non-zero length")
    classes = sorted(set(truth) | set(pred))
    scores = []
    for label in classes:
        tp = sum(t == label and p == label for t, p in zip(truth, pred))
        fp = sum(t != label and p == label for t, p in zip(truth, pred))
        fn = sum(t == label and p != label for t, p in zip(truth, pred))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return sum(scores) / len(scores)
