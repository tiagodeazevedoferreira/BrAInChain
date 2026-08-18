"""First interpretable ML baseline for crypto opportunity classification."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

FEATURE_COLUMNS = (
    "price_change_1h", "price_change_24h", "price_change_7d",
    "return_since_previous", "price_acceleration", "volume_change",
    "market_cap_change", "volume_market_cap_ratio", "price_volatility",
    "cmc_rank", "observations_seen",
)

@dataclass(frozen=True)
class BaselineResult:
    model: Any
    feature_columns: tuple[str, ...]
    target: str
    metrics: dict[str, float]


def prepare_xy(rows: Iterable[dict[str, Any]], target: str) -> tuple[list[list[float]], list[int]]:
    X, y = [], []
    for row in rows:
        label = row.get(target)
        if label not in (0, 1):
            continue
        values = []
        for name in FEATURE_COLUMNS:
            value = row.get(name)
            if value is None:
                break
            try:
                values.append(float(value))
            except (TypeError, ValueError):
                break
        else:
            X.append(values); y.append(int(label))
    return X, y


def train_baseline(train_rows: Iterable[dict[str, Any]], validation_rows: Iterable[dict[str, Any]], target: str) -> BaselineResult:
    """Train an interpretable logistic-regression baseline on temporal splits."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, precision_score, recall_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    X_train, y_train = prepare_xy(train_rows, target)
    X_val, y_val = prepare_xy(validation_rows, target)
    if len(set(y_train)) < 2:
        raise ValueError("training data needs both positive and negative examples")
    if not X_val:
        raise ValueError("validation data has no complete labeled rows")
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced"))
    model.fit(X_train, y_train)
    predictions = model.predict(X_val)
    metrics = {
        "accuracy": float(accuracy_score(y_val, predictions)),
        "precision": float(precision_score(y_val, predictions, zero_division=0)),
        "recall": float(recall_score(y_val, predictions, zero_division=0)),
    }
    return BaselineResult(model, FEATURE_COLUMNS, target, metrics)
