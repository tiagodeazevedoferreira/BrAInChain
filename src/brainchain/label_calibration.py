"""Calibration diagnostics for short-horizon price labels."""
from __future__ import annotations

from typing import Any, Iterable, Mapping


def _price(row: Mapping[str, Any]) -> float | None:
    value = row.get("price")
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def calibrate_1h(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    # Rows are expected to already contain the supervised 1h future price when available.
    returns = []
    for row in rows:
        current = _price(row)
        future = row.get("future_price_1h")
        try:
            future = float(future)
        except (TypeError, ValueError):
            continue
        if current and future > 0:
            returns.append(future / current - 1.0)

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
