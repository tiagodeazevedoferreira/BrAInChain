"""Feature engineering primitives for crypto market snapshots."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def _num(row: Mapping[str, Any], *keys: str) -> float | None:
    for key in keys:
        try:
            value = row.get(key)
            if value is not None:
                return float(value)
        except (TypeError, ValueError):
            continue
    return None


def build_features(row: Mapping[str, Any]) -> dict[str, float | None]:
    price = _num(row, "price_usd", "price")
    market_cap = _num(row, "market_cap_usd", "market_cap")
    volume = _num(row, "volume_24h_usd", "volume_24h")
    change_1h = _num(row, "percent_change_1h")
    change_24h = _num(row, "percent_change_24h")
    change_7d = _num(row, "percent_change_7d")
    rank = _num(row, "rank")

    return {
        "price_usd": price,
        "market_cap_usd": market_cap,
        "volume_24h_usd": volume,
        "volume_market_cap_ratio": (volume / market_cap) if volume is not None and market_cap and market_cap > 0 else None,
        "percent_change_1h": change_1h,
        "percent_change_24h": change_24h,
        "percent_change_7d": change_7d,
        "rank": rank,
    }


def build_feature_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {**dict(row), **build_features(row)}
        for row in rows
    ]
