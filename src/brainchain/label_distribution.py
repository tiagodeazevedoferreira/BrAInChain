"""Summaries of future-return label distributions."""
from __future__ import annotations

from typing import Any, Iterable, Mapping


def summarize_label_distribution(dataset: Iterable[Mapping[str, Any]], horizons_hours=(1, 6, 24, 72, 168), thresholds=(2, 5, 10)) -> dict[str, Any]:
    rows = list(dataset)
    result: dict[str, Any] = {}
    for hours in horizons_hours:
        values = [row.get(f"label_{hours}h_max_multiple") for row in rows]
        values = [float(value) for value in values if value is not None]
        summary: dict[str, Any] = {"eligible": len(values)}
        for threshold in thresholds:
            summary[f"hit_{threshold}x"] = sum(value >= threshold for value in values)
        result[f"{hours}h"] = summary
    return result
