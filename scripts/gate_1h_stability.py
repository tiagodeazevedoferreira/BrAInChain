"""Read-only stability gate for the 1h candidate model."""
from __future__ import annotations

import json
import statistics
import sys
from collections import Counter

from sklearn.metrics import balanced_accuracy_score, f1_score

from brainchain.feature_engineering import build_features
from brainchain.firebase_reader import FirebaseReader
from brainchain.labels import build_time_labels
from brainchain.modeling_1h import prepare_xy, train_1h_baseline


def _history(rows):
    return [{"timestamp": r.get("captured_at"), "coin_id": r.get("source_id"),
             "symbol": r.get("symbol"), "price": r.get("price_usd"),
             "market_cap": r.get("market_cap_usd"), "volume_24h": r.get("volume_24h_usd"),
             "cmc_rank": r.get("cmc_rank"), "percent_change_1h": r.get("percent_change_1h"),
             "percent_change_24h": r.get("percent_change_24h"), "percent_change_7d": r.get("percent_change_7d")}
            for r in rows]


def build_rows(snapshots):
    labels = build_time_labels(snapshots, horizons_hours=(1,))
    label_map = {(str(r["source_id"]), str(r["captured_at"])): r
                 for r in labels if r.get("label_1h_class")}
    by_asset = {}
    for row in snapshots:
        asset = str(row.get("source_id") or "")
        if asset:
            by_asset.setdefault(asset, []).append(row)
    rows = []
    for asset, history in by_asset.items():
        for feature in build_features(_history(history)):
            label = label_map.get((asset, str(feature.get("timestamp"))))
            if not label:
                continue
            row = dict(feature)
            row["source_id"] = asset
            row["captured_at"] = feature.get("timestamp")
            row["target_1h_label"] = label["label_1h_class"]
            rows.append(row)
    return sorted(rows, key=lambda r: str(r.get("captured_at", "")))


def main():
    rows = build_rows(FirebaseReader().read_snapshots())
    n = len(rows)
    folds = []
    for fold, train_fraction in enumerate((0.40, 0.50, 0.60, 0.70), 1):
        train_end = int(n * train_fraction)
        eval_end = min(n, train_end + int(n * 0.10))
        train_rows, eval_rows = rows[:train_end], rows[train_end:eval_end]
        result = train_1h_baseline(train_rows, eval_rows)
        X, y = prepare_xy(eval_rows)
        pred = result.model.predict(X)
        majority = Counter(r["target_1h_label"] for r in train_rows).most_common(1)[0][0]
        baseline = [majority] * len(y)
        folds.append({
            "fold": fold,
            "model_balanced_accuracy": float(balanced_accuracy_score(y, pred)),
            "model_macro_f1": float(f1_score(y, pred, average="macro", zero_division=0)),
            "baseline_balanced_accuracy": float(balanced_accuracy_score(y, baseline)),
            "baseline_macro_f1": float(f1_score(y, baseline, average="macro", zero_division=0)),
            "prediction_distribution": dict(Counter(map(int, pred))),
        })

    bacc = [f["model_balanced_accuracy"] for f in folds]
    f1 = [f["model_macro_f1"] for f in folds]
    concentration = [max(f["prediction_distribution"].values()) / sum(f["prediction_distribution"].values()) for f in folds]
    gate = {
        "passed": min(bacc) > 0.36 and min(f1) > 0.25 and max(concentration) < 0.90,
        "thresholds": {"min_balanced_accuracy": 0.36, "min_macro_f1": 0.25, "max_prediction_concentration": 0.90},
        "worst_fold_balanced_accuracy": min(bacc),
        "worst_fold_macro_f1": min(f1),
        "max_prediction_concentration": max(concentration),
        "bacc_stdev": statistics.pstdev(bacc),
        "f1_stdev": statistics.pstdev(f1),
    }
    json.dump({"labeled_rows": n, "folds": folds, "gate": gate}, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if gate["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
