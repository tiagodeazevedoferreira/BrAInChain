"""Convert Firebase-exported snapshots into chronological training rows."""
from __future__ import annotations

from typing import Any, Iterable, Mapping


def flatten_snapshots(payload: Mapping[str, Any] | Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Flatten flat and nested Firebase Realtime Database snapshot shapes.

    The production store uses ``snapshots/<asset>/<timestamp>``. The adapter
    also accepts the earlier flat ``{key: snapshot}`` representation.
    """
    rows: list[dict[str, Any]] = []
    if not isinstance(payload, Mapping):
        for item in payload:
            if isinstance(item, Mapping):
                row = dict(item)
                if row.get("source_id") is None and row.get("id") is not None:
                    row["source_id"] = row["id"]
                rows.append(row)
        return rows

    for key, item in payload.items():
        if not isinstance(item, Mapping):
            continue
        # Production shape: {asset: {timestamp: snapshot}}
        if item and all(isinstance(v, Mapping) for v in item.values()):
            for timestamp_key, snapshot in item.items():
                row = dict(snapshot)
                row.setdefault("source_id", key)
                row.setdefault("captured_at", timestamp_key.replace("_", "."))
                rows.append(row)
        else:
            row = dict(item)
            if row.get("source_id") is None and row.get("id") is not None:
                row["source_id"] = row["id"]
            rows.append(row)
    return rows


def prepare_dataset(payload: Mapping[str, Any] | Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Return deterministic chronological rows ready for feature/label joins."""
    rows = flatten_snapshots(payload)
    rows = [r for r in rows if r.get("source_id") is not None and r.get("captured_at") is not None]
    return sorted(rows, key=lambda r: (str(r["source_id"]), str(r["captured_at"])))
