"""Continuous future-return summaries for target selection."""
from __future__ import annotations

from typing import Any, Iterable, Mapping


def summarize_label_magnitude(dataset: Iterable[Mapping[str, Any]], horizons_hours=(1, 6, 24, 72, 168)) -> dict[str, dict[str, float | int | None]]:
    rows = list(dataset)
    result: dict[str, dict[str, float | int | None]] = {}
    for hours in horizons_hours:
        values = sorted(
            float(row[f"label_{hours}h_max_multiple"])
            for row in rows
            if row.get(f"label_{hours}h_max_multiple") is not None
        )
        if not values:
            result[f"{hours}h"] = {"eligible": 0, "min": None, "p25": None, "median": None, "p75": None, "p95": None, "max": None}
            continue
        def q(p: float) -> float:
            if len(values) == 1:
                return values[0]
            pos = (len(values) - 1) * p
            lo, hi = int(pos), min(int(pos) + 1, len(values) - 1)
            return values[lo] + (values[hi] - values[lo]) * (pos - lo)
        result[f"{hours}h"] = {
            "eligible": len(values),
            "min": values[0],
            "p25": q(0.25),
            "median": q(0.50),
            "p75": q(0.75),
            "p95": q(0.95),
            "max": values[-1],
        }
    return result
