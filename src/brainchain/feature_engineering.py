"""Feature engineering for historical crypto market snapshots.

Features are strictly backward-looking: no future observation is used to build
features for a given timestamp. This keeps the dataset suitable for temporal
backtesting and supervised learning.
"""
from __future__ import annotations

from datetime import datetime, timezone
from math import log
from statistics import pstdev
from typing import Any, Iterable


def _num(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _pct_change(current: float | None, previous: float | None) -> float | None:
    if current is None or previous is None or previous == 0:
        return None
    return (current / previous - 1.0) * 100.0


def _acceleration(current_change: float | None, previous_change: float | None) -> float | None:
    if current_change is None or previous_change is None:
        return None
    return current_change - previous_change


def _volatility(prices: Iterable[float]) -> float | None:
    values = [p for p in prices if p is not None and p > 0]
    if len(values) < 2:
        return None
    returns = [log(values[i] / values[i - 1]) for i in range(1, len(values))]
    return pstdev(returns) if returns else None


def build_features(history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build point-in-time features from chronological observations.

    Expected observation fields include timestamp, price, market_cap, volume_24h,
    percent_change_1h/24h/7d, cmc_rank and date_added. Missing fields remain None.
    """
    ordered = sorted(history, key=lambda x: str(x.get("timestamp", "")))
    result: list[dict[str, Any]] = []

    for i, current in enumerate(ordered):
        previous = ordered[i - 1] if i else None
        previous2 = ordered[i - 2] if i >= 2 else None
        price = _num(current.get("price"))
        prev_price = _num(previous.get("price")) if previous else None
        prev2_price = _num(previous2.get("price")) if previous2 else None
        volume = _num(current.get("volume_24h"))
        prev_volume = _num(previous.get("volume_24h")) if previous else None
        market_cap = _num(current.get("market_cap"))
        prev_market_cap = _num(previous.get("market_cap")) if previous else None

        price_change = _pct_change(price, prev_price)
        previous_price_change = _pct_change(prev_price, prev2_price)
        volume_change = _pct_change(volume, prev_volume)
        market_cap_change = _pct_change(market_cap, prev_market_cap)

        features = {
            "timestamp": current.get("timestamp"),
            "coin_id": current.get("coin_id") or current.get("id"),
            "symbol": current.get("symbol"),
            "price": price,
            "market_cap": market_cap,
            "volume_24h": volume,
            "cmc_rank": _num(current.get("cmc_rank")),
            "price_change_1h": _num(current.get("percent_change_1h")),
            "price_change_24h": _num(current.get("percent_change_24h")),
            "price_change_7d": _num(current.get("percent_change_7d")),
            "return_since_previous": price_change,
            "price_acceleration": _acceleration(price_change, previous_price_change),
            "volume_change": volume_change,
            "market_cap_change": market_cap_change,
            "volume_market_cap_ratio": (volume / market_cap) if volume is not None and market_cap not in (None, 0) else None,
            "price_volatility": _volatility([_num(x.get("price")) for x in ordered[max(0, i - 5): i + 1]]),
            "is_first_observation": i == 0,
            "observations_seen": i + 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        result.append(features)

    return result
