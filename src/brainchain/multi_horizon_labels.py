"""Leakage-safe multi-horizon labels for crypto price expansion."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class LabelConfig:
    horizons: tuple[int, ...] = (1, 6, 24, 72)
    thresholds: tuple[float, ...] = (2.0, 5.0, 10.0, 50.0, 100.0, 1000.0)


def _price(row: Mapping[str, Any]) -> float | None:
    value = row.get("price")
    if value is None:
        quote = row.get("quote")
        if isinstance(quote, Mapping):
            usd = quote.get("USD")
            if isinstance(usd, Mapping):
                value = usd.get("price")
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _symbol(row: Mapping[str, Any]) -> str:
    return str(row.get("source_id") or row.get("symbol") or row.get("id") or "")


def build_labels(rows: Iterable[Mapping[str, Any]], config: LabelConfig | None = None) -> list[dict[str, Any]]:
    """Build future-only labels using positional horizons within each asset.

    A row is labeled only when the full requested horizon exists. The current
    row's price is never included in the future maximum, preventing look-ahead
    contamination. Horizons are expressed in number of observations, not wall
    clock hours; cadence must therefore be controlled by the upstream collector.
    """
    cfg = config or LabelConfig()
    if not cfg.horizons or not cfg.thresholds:
        raise ValueError("horizons and thresholds cannot be empty")
    if any(h <= 0 for h in cfg.horizons):
        raise ValueError("horizons must be positive")
    if any(t <= 1 for t in cfg.thresholds):
        raise ValueError("thresholds must be greater than 1")

    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        symbol = _symbol(row)
        if symbol and _price(row) is not None:
            grouped.setdefault(symbol, []).append(row)

    result: list[dict[str, Any]] = []
    max_horizon = max(cfg.horizons)
    for symbol, series in grouped.items():
        series = sorted(series, key=lambda r: str(r.get("captured_at", "")))
        for i, row in enumerate(series):
            end = i + max_horizon
            if end >= len(series):
                continue
            current = _price(row)
            future_prices = [_price(x) for x in series[i + 1 : end + 1]]
            future_prices = [p for p in future_prices if p is not None]
            if current is None or len(future_prices) != max_horizon:
                continue
            labels: dict[str, Any] = {
                "source_id": symbol,
                "captured_at": row.get("captured_at"),
                "entry_price": current,
            }
            for horizon in cfg.horizons:
                window = future_prices[:horizon]
                max_multiplier = max(window) / current
                labels[f"max_multiplier_{horizon}"] = max_multiplier
                for threshold in cfg.thresholds:
                    key = f"hit_{_threshold_key(threshold)}x_{horizon}"
                    labels[key] = max_multiplier >= threshold
            result.append(labels)
    return result


def _threshold_key(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else str(value).replace(".", "_")
