"""Calibration diagnostics for short-horizon price labels."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Mapping


def _price(row: Mapping[str, Any]) -> float | None:
    value = row.get("price")
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def _ts(value: Any) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def calibrate_1h(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Measure realized same-asset returns using the first observation within 1h.

    If ``future_price_1h`` is already supplied, it is used for backwards
    compatibility. Otherwise snapshots are matched by ``source_id`` and
    ``captured_at`` so no observation from another asset can leak into the label.
    """
    materialized = list(rows)
    returns: list[float] = []

    # Preferred path for normalized snapshots: derive the 1h future directly.
    grouped: dict[str, list[tuple[datetime, float]]] = {}
    for row in materialized:
        current = _price(row)
        captured = _ts(row.get("captured_at"))
        asset = row.get("source_id") or row.get("asset") or row.get("asset_id")
        if current is not None and captured is not None and asset is not None:
            grouped.setdefault(str(asset), []).append((captured, current))

    if grouped:
        for observations in grouped.values():
            observations.sort(key=lambda item: item[0])
            for index, (start, current) in enumerate(observations):
                future = next(
                    (
                        price
                        for timestamp, price in observations[index + 1 :]
                        if (timestamp - start).total_seconds() <= 3600
                    ),
                    None,
                )
                if future is not None:
                    returns.append(future / current - 1.0)
    else:
        # Backwards-compatible unit-test/API path.
        for row in materialized:
            current = _price(row)
            try:
                future = float(row.get("future_price_1h"))
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
