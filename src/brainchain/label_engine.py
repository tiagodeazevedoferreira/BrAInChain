"""Build future-looking training labels from historical crypto snapshots."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class LabelConfig:
    horizons_hours: tuple[int, ...] = (24, 168)
    multipliers: tuple[float, ...] = (2.0, 5.0, 10.0)


def _time(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def build_labels(snapshots: Iterable[Mapping[str, Any]], config: LabelConfig | None = None) -> list[dict[str, Any]]:
    """Create point-in-time labels using only observations inside each future window.

    A window is complete only when there is a later observation at or beyond its
    end. Incomplete windows remain None rather than being treated as failures.
    """
    cfg = config or LabelConfig()
    rows = [dict(row) for row in snapshots if row.get("source_id") is not None and row.get("price_usd") is not None]
    groups: dict[Any, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(row["source_id"], []).append(row)

    output: list[dict[str, Any]] = []
    for coin_rows in groups.values():
        coin_rows.sort(key=lambda r: _time(r["captured_at"]))
        for index, current in enumerate(coin_rows):
            current_time = _time(current["captured_at"])
            current_price = float(current["price_usd"])
            future = coin_rows[index + 1 :]
            labels: dict[str, Any] = {}
            last_future_time = _time(future[-1]["captured_at"]) if future else None
            for horizon in cfg.horizons_hours:
                end = current_time + timedelta(hours=horizon)
                complete = last_future_time is not None and last_future_time >= end
                eligible = [r for r in future if _time(r["captured_at"]) <= end]
                for multiplier in cfg.multipliers:
                    key = f"target_{int(multiplier)}x_{horizon}h"
                    labels[key] = None if not complete else int(
                        any(float(r["price_usd"]) >= current_price * multiplier for r in eligible)
                    )
            output.append({"source_id": current["source_id"], "captured_at": current["captured_at"], **labels})
    return output
