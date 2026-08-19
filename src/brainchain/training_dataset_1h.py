"""Compose point-in-time features with the promoted 1h target."""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from brainchain.training_labels_1h import build_1h_labels


def build_1h_training_rows(snapshots: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Return snapshot features joined to leakage-safe 1h labels."""
    source_rows = [dict(row) for row in snapshots]
    labels = build_1h_labels(source_rows)
    label_map = {(row["source_id"], row["captured_at"]): row for row in labels}

    rows: list[dict[str, Any]] = []
    for snapshot in source_rows:
        key = (snapshot.get("source_id"), snapshot.get("captured_at"))
        label = label_map.get(key)
        if label is None:
            continue
        row = dict(snapshot)
        row["target_1h_return"] = label["target_1h_return"]
        row["target_1h_label"] = label["target_1h_label"]
        rows.append(row)
    rows.sort(key=lambda row: str(row.get("captured_at", "")))
    return rows
