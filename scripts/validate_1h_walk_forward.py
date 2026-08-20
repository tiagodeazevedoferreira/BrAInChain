"""Read-only walk-forward validation for the 1h candidate model."""
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


def _evaluate(train_rows: list[dict], eval_rows: list[dict]) -> dict:
    result = train_1h_baseline(train_rows, eval_rows)
    X, y = prepare_xy(eval_rows)
    pred = result.model.predict(X)
    labels = {"down": 0, "neutral": 1, "up": 2}
    counts = {k: sum(r["target_1h_label"] == k for r in eval_rows) for k in labels}
    majority = max(counts, key=counts.get)
    majority_pred = [labels[majority]] * len(y)
    return {
        "rows": len(eval_rows),
        "train_rows": len(train_rows),
        "labels": counts,
        "model_balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "model_macro_f1": float(f1_score(y, pred, average="macro", zero_division=0)),
        "baseline_balanced_accuracy": float(balanced_accuracy_score(y, majority_pred)),
        "baseline_macro_f1": float(f1_score(y, majority_pred, average="macro", zero_division=0)),
        "majority_label": majority,
    }


def main() -> int:
    snapshots = FirebaseReader().read_snapshots()
    rows = _build_rows(snapshots)
    n = len(rows)
    if n < 1000:
        raise RuntimeError(f"Not enough labeled rows for walk-forward validation: {n}")

    # Four expanding-window folds. Each evaluation window is 10% of the
    # chronological sample, while training always contains only earlier data.
    folds = []
    for i, train_fraction in enumerate((0.40, 0.50, 0.60, 0.70), start=1):
        train_end = int(n * train_fraction)
        eval_end = min(n, train_end + int(n * 0.10))
        train_rows = rows[:train_end]
        eval_rows = rows[train_end:eval_end]
        folds.append({
            "fold": i,
            "train_start": str(train_rows[0]["captured_at"]),
            "train_end": str(train_rows[-1]["captured_at"]),
            "eval_start": str(eval_rows[0]["captured_at"]),
            "eval_end": str(eval_rows[-1]["captured_at"]),
            **_evaluate(train_rows, eval_rows),
        })

    mean_model_bacc = sum(f["model_balanced_accuracy"] for f in folds) / len(folds)
    mean_baseline_bacc = sum(f["baseline_balanced_accuracy"] for f in folds) / len(folds)
    mean_model_f1 = sum(f["model_macro_f1"] for f in folds) / len(folds)
    mean_baseline_f1 = sum(f["baseline_macro_f1"] for f in folds) / len(folds)

    payload = {
        "snapshots": len(snapshots),
        "labeled_rows": n,
        "folds": folds,
        "summary": {
            "mean_model_balanced_accuracy": mean_model_bacc,
            "mean_baseline_balanced_accuracy": mean_baseline_bacc,
            "mean_model_macro_f1": mean_model_f1,
            "mean_baseline_macro_f1": mean_baseline_f1,
            "folds_beating_baseline_bacc": sum(
                f["model_balanced_accuracy"] > f["baseline_balanced_accuracy"] for f in folds
            ),
            "folds_beating_baseline_f1": sum(
                f["model_macro_f1"] > f["baseline_macro_f1"] for f in folds
            ),
        },
        "method": "expanding chronological walk-forward, 4 folds, 40/50/60/70% train with 10% evaluation windows",
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
