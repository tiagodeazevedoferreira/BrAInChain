from brainchain.backtesting import BacktestConfig, evaluate_predictions


def test_backtest_metrics_at_threshold():
    rows = [
        {"probability": 0.90, "target": 1},
        {"probability": 0.80, "target": 0},
        {"probability": 0.20, "target": 1},
        {"probability": 0.10, "target": 0},
    ]
    result = evaluate_predictions(rows, BacktestConfig(threshold=0.70))
    assert result["samples"] == 4
    assert result["signals"] == 2
    assert result["precision"] == 0.5
    assert result["recall"] == 0.5
    assert result["f1"] == 0.5


def test_unknown_targets_are_ignored():
    result = evaluate_predictions([{"probability": 0.9, "target": None}])
    assert result["samples"] == 0
