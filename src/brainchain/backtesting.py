"""Leakage-aware offline evaluation utilities for the Crypto AI baseline."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class BacktestConfig:
    threshold: float = 0.70
    initial_capital: float = 1000.0


def evaluate_predictions(rows: Iterable[Mapping[str, Any]], config: BacktestConfig | None = None) -> dict[str, float]:
    """Evaluate binary model predictions without simulating order execution.

    Rows must contain ``probability`` and ``target``. Unknown targets are ignored.
    This v1 deliberately measures signal quality only; portfolio execution comes later.
    """
    cfg = config or BacktestConfig()
    usable = [r for r in rows if r.get("target") is not None and r.get("probability") is not None]
    if not usable:
        return {"samples": 0.0, "signals": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0}

    tp = fp = fn = signals = 0
    for row in usable:
        predicted = float(row["probability"]) >= cfg.threshold
        actual = int(row["target"]) == 1
        signals += int(predicted)
        tp += int(predicted and actual)
        fp += int(predicted and not actual)
        fn += int((not predicted) and actual)

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"samples": float(len(usable)), "signals": float(signals), "precision": precision, "recall": recall, "f1": f1}
