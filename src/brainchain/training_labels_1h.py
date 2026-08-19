"""Build the first training target: 1h return class using the promoted 0.25% threshold."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Iterable, Mapping

ONE_HOUR_RETURN_THRESHOLD = 0.0025


def _time(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def build_1h_labels(snapshots: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Create leakage-safe 1h labels from the first observation at/after +1h.

    Rows without an observation at or beyond the one-hour horizon are omitted
    because their future outcome is not yet known.
    """
    rows = [dict(row) for row in snapshots if row.get("source_id") is not None and row.get("price_usd") is not None]
    groups: dict[Any, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(row["source_id"], []).append(row)

    output: list[dict[str, Any]] = []
    for coin_rows in groups.values():
        coin_rows.sort(key=lambda r: _time(r["captured_at"]))
        for index, current in enumerate(coin_rows):
            current_time = _time(current["captured_at"])
            horizon_end = current_time + timedelta(hours=1)
            future = [r for r in coin_rows[index + 1 :] if _time(r["captured_at"]) >= horizon_end]
            if not future:
                continue
            future_row = future[0]
            base_price = float(current["price_usd"])
            future_price = float(future_row["price_usd"])
            change = (future_price / base_price) - 1.0
            if change >= ONE_HOUR_RETURN_THRESHOLD:
                label = "up"
            elif change <= -ONE_HOUR_RETURN_THRESHOLD:
                label = "down"
            else:
                label = "neutral"
            output.append({
                "source_id": current["source_id"],
                "captured_at": current["captured_at"],
                "target_1h_return": change,
                "target_1h_label": label,
            })
    return output
