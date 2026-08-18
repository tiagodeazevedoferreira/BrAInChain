"""Convert Firebase-exported snapshots into chronological training rows."""
from __future__ import annotations

from typing import Any, Iterable, Mapping


def flatten_snapshots(payload: Mapping[str, Any] | Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Flatten common Firebase Realtime Database snapshot shapes."""
    if isinstance(payload, Mapping):
        values = payload.values()
    else:
        values = payload
    rows: list[dict[str, Any]] = []
    for item in values:
        if not isinstance(item, Mapping):
            continue
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
