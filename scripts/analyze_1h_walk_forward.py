"""Read-only 1h walk-forward error analysis against the live Firebase dataset."""
from __future__ import annotations

import json
import sys
from collections import Counter

from brainchain.feature_engineering import build_features
from brainchain.firebase_reader import FirebaseReader
from brainchain.labels import build_time_labels
from brainchain.modeling_1h import prepare_xy, train_1h_baseline
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support


def _feature_history(rows: list[dict]) -> list[dict]:
    return [
        {"timestamp": r.get("captured_at"), "coin_id": r.get("source_id"),
         "symbol": r.get("symbol"), "price": r.get("price_usd"),
         "market_cap": r.get("market_cap_usd"), "volume_24h": r.get("volume_24h_usd"),
         "cmc_rank": r.get("cmc_rank"), "percent_change_1h": r.get("percent_change_1h"),
         "percent_change_24h": r.get("percent_change_24h"), "percent_change_7d": r.get("percent_change_7d")}
        for r in rows
    ]


def _build_rows(snapshots: list[dict]) -> list[dict]:
    labels = build_time_labels(snapshots, horizons_hours=(1,))
    label_map = {(str(r["source_id"]), str(r["captured_at"])): r for r in labels if r.get("label_1h_class")}
    by_asset: dict[str, list[dict]] = {}
    for row in snapshots:
        asset = str(row.get("source_id") or "")
        if asset:
            by_asset.setdefault(asset, []).append(row)
    rows: list[dict] = []
    for asset, history in by_asset.items():
        for feature in build_features(_feature_history(history)):
            label = label_map.get((asset, str(feature.get("timestamp"))))
            if not label:
                continue
            row = dict(feature)
            row["source_id"] = asset
            row["captured_at"] = feature.get("timestamp")
            row["target_1h_label"] = label["label_1h_class"]
            rows.append(row)
    return sorted(rows, key=lambda r: str(r.get("captured_at", "")))


def _class_metrics(y_true: list[int], y_pred: list[int]) -> dict[str, dict[str, float | int]]:
    names = ["down", "neutral", "up"]
    p, r, f, s = precision_recall_fscore_support(y_true, y_pred, labels=[0, 1, 2], zero_division=0)
    return {name: {"precision": float(p[i]), "recall": float(r[i]), "f1": float(f[i]), "support": int(s[i])} for i, name in enumerate(names)}


def main() -> int:
    snapshots = FirebaseReader().read_snapshots()
    rows = _build_rows(snapshots)
    n = len(rows)
    folds = []
    for fold, train_fraction in enumerate((0.40, 0.50, 0.60, 0.70), 1):
        train_end = int(n * train_fraction)
        eval_end = min(n, train_end + int(n * 0.10))
        train_rows, eval_rows = rows[:train_end], rows[train_end:eval_end]
        result = train_1h_baseline(train_rows, eval_rows)
        X_eval, y_eval = prepare_xy(eval_rows)
        pred = result.model.predict(X_eval).tolist()
        majority = Counter(r["target_1h_label"] for r in rows).most_common(1)[0][0]
        cm = confusion_matrix(y_eval, pred, labels=[0, 1, 2]).tolist()
        folds.append({
            "fold": fold,
            "train_rows": len(train_rows),
            "eval_rows": len(eval_rows),
            "eval_start": eval_rows[0].get("captured_at") if eval_rows else None,
            "eval_end": eval_rows[-1].get("captured_at") if eval_rows else None,
            "majority_label": majority,
            "confusion_matrix": {"labels": ["down", "neutral", "up"], "matrix": cm},
            "per_class": _class_metrics(y_eval, pred),
            "prediction_distribution": dict(Counter(pred)),
        })
    payload = {"snapshots": len(snapshots), "labeled_rows": n, "folds": folds}
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
