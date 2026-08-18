from brainchain.label_calibration import calibrate_1h


def test_calibrate_1h_reports_distribution():
    rows = [
        {"price": 100, "future_price_1h": 101},
        {"price": 100, "future_price_1h": 102},
        {"price": 100, "future_price_1h": 99},
    ]
    result = calibrate_1h(rows)
    assert result["eligible"] == 3
    assert result["multipliers"]["median"] == 1.01
