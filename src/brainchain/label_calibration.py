"""Calibration diagnostics for short-horizon price labels."""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from .labels import build_time_labels


def calibrate_1h(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Measure the observed 1h max-return distribution from raw snapshots.

    The future value is derived point-in-time from snapshots of the same asset;
    callers do not need to materialize a ``future_price_1h`` field.
    """
    labels = build_time_labels(rows, horizons_hours=(1,))
    returns = [
        float(row["label_1h_max_return"])
        for row in labels
        if row.get("label_1h_max_return") is not None
    ]
    returns.sort()

    def pct(p: float) -> float | None:
        if not returns:
            return None
        pos = (len(returns) - 1) * p
        lo = int(pos)
        hi = min(lo + 1, len(returns) - 1)
        return returns[lo] + (returns[hi] - returns[lo]) * (pos - lo)

    return {
        "eligible": len(returns),
        "return": {
            "min": min(returns) if returns else None,
            "p01": pct(0.01),
            "p05": pct(0.05),
            "median": pct(0.50),
            "p95": pct(0.95),
            "p99": pct(0.99),
            "max": max(returns) if returns else None,
        },
        "multipliers": {
            "min": min((1 + x for x in returns), default=None),
            "median": pct(0.50) + 1 if returns else None,
            "max": max((1 + x for x in returns), default=None),
        },
    }
