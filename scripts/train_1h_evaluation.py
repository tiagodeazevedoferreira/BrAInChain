"""Read-only 1h training evaluation against the live Firebase dataset."""
from __future__ import annotations

import json
import sys

from brainchain.feature_engineering import build_features
from brainchain.firebase_reader import FirebaseReader
from brainchain.labels import build_time_labels
from brainchain.modeling_1h import prepare_xy, train_1h_baseline
from sklearn.metrics import balanced_accuracy_score, f1_score


def _feature_history(rows: list[dict]) -> list[dict]:
    return [
        {
            "timestamp": row.get("captured_at"),
            "coin_id": row.get("source_id"),
            "symbol": row.get("symbol"),
            "price": row.get("price_usd"),
            "market_cap": row.get("market_cap_usd"),
            "volume_24h": row.get("volume_24h_usd"),
            "cmc_rank": row.get("cmc_rank"),
            "percent_change_1h": row.get("percent_change_1h"),
            "percent_change_24h": row.get("percent_change_24h"),
            "percent_change_7d": row.get("percent_change_7d"),
        }
        for row in rows
    ]


def _build_rows(snapshots: list[dict]) -> list[dict]:
    labels = build_time_labels(snapshots, horizons_hours=(1,))
    label_map = {
        (str(r["source_id"]), str(r["captured_at"])): r
        for r in labels
        if r.get("label_1h_class")
    }

    by_asset: dict[str, list[dict]] = {}
    for row in snapshots:
        asset = str(row.get("source_id") or "")
        if asset:
            by_asset.setdefault(asset, []).append(row)

    rows: list[dict] = []
    for asset, history in by_asset.items():
        for feature in build_features(_feature_history(history)):
            key = (asset, str(feature.get("timestamp")))
            label = label_map.get(key)
            if not label:
                continue
            row = dict(feature)
            row["source_id"] = asset
            row["captured_at"] = feature.get("timestamp")
            row["target_1h_label"] = label["label_1h_class"]
            rows.append(row)
    return sorted(rows, key=lambda r: str(r.get("captured_at", "")))


def main() -> int:
    reader = FirebaseReader()
    snapshots = reader.read_snapshots()
    rows = _build_rows(snapshots)

    n = len(rows)
    train_end = int(n * 0.70)
    val_end = train_end + int(n * 0.15)
    train_rows = rows[:train_end]
    validation_rows = rows[train_end:val_end]
    test_rows = rows[val_end:]

    result = train_1h_baseline(train_rows, validation_rows)
    X_test, y_test = prepare_xy(test_rows)
    predictions = result.model.predict(X_test)

    label_ids = {"down": 0, "neutral": 1, "up": 2}
    counts = {label: sum(r["target_1h_label"] == label for r in rows) for label in label_ids}
    majority = max(counts, key=counts.get) if counts else None
    majority_id = label_ids[majority] if majority else None
    majority_predictions = [majority_id] * len(y_test) if majority_id is not None else []

    payload = {
        "snapshots": len(snapshots),
        "labeled_rows": n,
        "train_rows": len(train_rows),
        "validation_rows": len(validation_rows),
        "test_rows": len(test_rows),
        "labels": counts,
        "model": {
            "validation_balanced_accuracy": result.metrics["balanced_accuracy"],
            "validation_macro_f1": result.metrics["macro_f1"],
            "test_balanced_accuracy": float(balanced_accuracy_score(y_test, predictions)),
            "test_macro_f1": float(f1_score(y_test, predictions, average="macro", zero_division=0)),
        },
        "baseline_test": {
            "strategy": "majority_class",
            "majority_label": majority,
            "balanced_accuracy": float(balanced_accuracy_score(y_test, majority_predictions)) if y_test else None,
            "macro_f1": float(f1_score(y_test, majority_predictions, average="macro", zero_division=0)) if y_test else None,
        },
        "features": list(result.feature_columns),
        "temporal_split": "70/15/15 chronological",
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
