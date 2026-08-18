"""Build a supervised dataset from snapshots, features and time-based labels."""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from .features import build_features
from .labels import build_time_labels

FEATURE_KEYS = (
    "price_usd",
    "market_cap_usd",
    "volume_24h_usd",
    "volume_market_cap_ratio",
    "percent_change_1h",
    "percent_change_24h",
    "percent_change_7d",
    "rank",
)


def build_dataset(rows: Iterable[Mapping[str, Any]], horizons_hours=(1, 6, 24, 72, 168)) -> list[dict[str, Any]]:
    """Return rows containing point-in-time features and future labels.

    Rows without a future observation for a requested horizon are retained,
    but their corresponding label fields are None. This preserves the raw
    historical sample count while making training eligibility explicit.
    """
    source = [dict(row) for row in rows]
    labels = build_time_labels(source, horizons_hours=horizons_hours)
    labels_by_key = {(row["source_id"], row["captured_at"]): row for row in labels}

    dataset: list[dict[str, Any]] = []
    for row in source:
        asset = str(row.get("source_id") or row.get("symbol") or row.get("id") or "")
        key = (asset, row.get("captured_at"))
        label_row = labels_by_key.get(key)
        if label_row is None:
            continue
        features = build_features(row)
        output = {
            "source_id": asset,
            "captured_at": row.get("captured_at"),
            **{key: features.get(key) for key in FEATURE_KEYS},
        }
        for key, value in label_row.items():
            if key.startswith("label_"):
                output[key] = value
        dataset.append(output)
    return dataset


def training_counts(dataset: Iterable[Mapping[str, Any]], horizons_hours=(1, 6, 24, 72, 168)) -> dict[str, int]:
    """Count rows with an observed future label for each horizon."""
    rows = list(dataset)
    return {
        f"{hours}h": sum(row.get(f"label_{hours}h_max_multiple") is not None for row in rows)
        for hours in horizons_hours
    }
