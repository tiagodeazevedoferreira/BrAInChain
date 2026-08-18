"""Time-based supervised labels for historical market observations."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Iterable, Mapping


def _ts(value: Any) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _price(row: Mapping[str, Any]) -> float | None:
    try:
        value = row.get("price_usd", row.get("price"))
        return float(value) if value is not None and float(value) > 0 else None
    except (TypeError, ValueError):
        return None


def build_time_labels(rows: Iterable[Mapping[str, Any]], horizons_hours=(1, 6, 24, 72, 168)) -> list[dict[str, Any]]:
    """Create point-in-time labels without using observations after each horizon."""
    ordered = sorted(
        (row for row in rows if _ts(row.get("captured_at")) is not None and _price(row) is not None),
        key=lambda r: (_ts(r.get("source_id")) or _ts(r.get("captured_at")), _ts(r.get("captured_at"))),
    )
    by_asset: dict[str, list[Mapping[str, Any]]] = {}
    for row in ordered:
        asset = str(row.get("source_id") or row.get("symbol") or row.get("id") or "")
        if asset:
            by_asset.setdefault(asset, []).append(row)

    result: list[dict[str, Any]] = []
    for asset, asset_rows in by_asset.items():
        for row in asset_rows:
            start = _ts(row["captured_at"])
            start_price = _price(row)
            if start is None or start_price is None:
                continue
            out = {"source_id": asset, "captured_at": row["captured_at"], "price_usd": start_price}
            for hours in horizons_hours:
                end = start + timedelta(hours=hours)
                future_prices = [
                    p for future in asset_rows
                    if start < (_ts(future.get("captured_at")) or start) <= end
                    for p in [_price(future)]
                    if p is not None
                ]
                prefix = f"label_{hours}h"
                out[f"{prefix}_max_return"] = (max(future_prices) / start_price - 1.0) if future_prices else None
                out[f"{prefix}_max_multiple"] = (max(future_prices) / start_price) if future_prices else None
                out[f"{prefix}_hit_2x"] = int(max(future_prices) >= start_price * 2) if future_prices else None
                out[f"{prefix}_hit_5x"] = int(max(future_prices) >= start_price * 5) if future_prices else None
                out[f"{prefix}_hit_10x"] = int(max(future_prices) >= start_price * 10) if future_prices else None
            result.append(out)
    return result
