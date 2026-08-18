"""Deterministic training pipeline for the first Crypto AI baseline."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .modeling import train_baseline


@dataclass(frozen=True)
class TrainingConfig:
    target: str = "target_2x_24h"
    min_train_rows: int = 50
    min_validation_rows: int = 10


def _time(row: Mapping[str, Any]) -> str:
    return str(row.get("captured_at", ""))


def temporal_split(rows: Iterable[Mapping[str, Any]], train_ratio: float = 0.70, validation_ratio: float = 0.15):
    """Sort by observation time and split chronologically."""
    if not 0 < train_ratio < 1 or not 0 < validation_ratio < 1 or train_ratio + validation_ratio >= 1:
        raise ValueError("ratios must be positive and leave a test partition")
    ordered = sorted((dict(r) for r in rows), key=_time)
    n = len(ordered)
    train_end = int(n * train_ratio)
    validation_end = train_end + int(n * validation_ratio)
    return ordered[:train_end], ordered[train_end:validation_end], ordered[validation_end:]


def train(rows: Iterable[Mapping[str, Any]], config: TrainingConfig | None = None):
    """Train the baseline only when enough labeled temporal data exists."""
    cfg = config or TrainingConfig()
    train_rows, validation_rows, test_rows = temporal_split(rows)
    if len(train_rows) < cfg.min_train_rows:
        raise ValueError(f"not enough training rows: {len(train_rows)} < {cfg.min_train_rows}")
    if len(validation_rows) < cfg.min_validation_rows:
        raise ValueError(f"not enough validation rows: {len(validation_rows)} < {cfg.min_validation_rows}")
    result = train_baseline(train_rows, validation_rows, cfg.target)
    return {"result": result, "train_rows": train_rows, "validation_rows": validation_rows, "test_rows": test_rows}
