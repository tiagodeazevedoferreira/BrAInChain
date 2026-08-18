"""Build leakage-safe ML datasets from point-in-time features and future labels."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class DatasetSplit:
    train: list[dict[str, Any]]
    validation: list[dict[str, Any]]
    test: list[dict[str, Any]]


def build_training_rows(features: Iterable[Mapping[str, Any]], labels: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Join features and labels by coin/timestamp without including future labels as features."""
    label_map = {(r.get("source_id"), r.get("captured_at")): dict(r) for r in labels}
    rows: list[dict[str, Any]] = []
    for feature in features:
        key = (feature.get("source_id"), feature.get("captured_at"))
        label = label_map.get(key)
        if not label:
            continue
        row = dict(feature)
        for name, value in label.items():
            if name.startswith("target_"):
                row[name] = value
        rows.append(row)
    rows.sort(key=lambda r: str(r.get("captured_at", "")))
    return rows


def temporal_split(rows: Iterable[Mapping[str, Any]], train_ratio: float = 0.70, validation_ratio: float = 0.15) -> DatasetSplit:
    """Split chronologically; never shuffle observations across time boundaries."""
    ordered = sorted((dict(r) for r in rows), key=lambda r: str(r.get("captured_at", "")))
    if not 0 < train_ratio < 1 or not 0 <= validation_ratio < 1 or train_ratio + validation_ratio >= 1:
        raise ValueError("train_ratio + validation_ratio must be between 0 and 1")
    n = len(ordered)
    train_end = int(n * train_ratio)
    validation_end = train_end + int(n * validation_ratio)
    return DatasetSplit(ordered[:train_end], ordered[train_end:validation_end], ordered[validation_end:])
