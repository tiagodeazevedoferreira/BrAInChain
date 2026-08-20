"""Interpretable multiclass ML baseline for the promoted 1h target."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = (
    "price_change_1h", "price_change_24h", "price_change_7d",
    "return_since_previous", "price_acceleration", "volume_change",
    "market_cap_change", "volume_market_cap_ratio", "price_volatility",
    "cmc_rank", "observations_seen",
)
LABEL_TO_ID = {"down": 0, "neutral": 1, "up": 2}


@dataclass(frozen=True)
class ModelResult:
    model: Any
    feature_columns: tuple[str, ...]
    target: str
    metrics: dict[str, float]


def prepare_xy(rows: Iterable[dict[str, Any]], target: str = "target_1h_label") -> tuple[list[list[float]], list[int]]:
    X: list[list[float]] = []
    y: list[int] = []
    for row in rows:
        raw_label = row.get(target)
        if raw_label in LABEL_TO_ID:
            label = LABEL_TO_ID[raw_label]
        elif raw_label in (0, 1, 2):
            label = int(raw_label)
        else:
            continue
        values: list[float] = []
        for name in FEATURE_COLUMNS:
            value = row.get(name)
            if value is None:
                break
            try:
                values.append(float(value))
            except (TypeError, ValueError):
                break
        else:
            X.append(values)
            y.append(label)
    return X, y


def train_1h_baseline(
    train_rows: Iterable[dict[str, Any]],
    validation_rows: Iterable[dict[str, Any]],
    target: str = "target_1h_label",
) -> ModelResult:
    """Train a temporal-split logistic regression baseline for 1h classes."""
    X_train, y_train = prepare_xy(train_rows, target)
    X_val, y_val = prepare_xy(validation_rows, target)
    if len(set(y_train)) < 2:
        raise ValueError("training data needs at least two classes")
    if not X_val:
        raise ValueError("validation data has no complete labeled rows")
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=1000, class_weight="balanced"),
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_val)
    metrics = {
        "balanced_accuracy": float(balanced_accuracy_score(y_val, predictions)),
        "macro_f1": float(f1_score(y_val, predictions, average="macro", zero_division=0)),
    }
    return ModelResult(model, FEATURE_COLUMNS, target, metrics)
