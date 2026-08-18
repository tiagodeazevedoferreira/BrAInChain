from brainchain.portfolio_backtester import PortfolioConfig, simulate


def test_simulation_applies_threshold_and_costs():
    result = simulate(
        [
            {"probability": 0.9, "target_return": 0.20},
            {"probability": 0.6, "target_return": 1.00},
        ],
        PortfolioConfig(initial_capital=1000, threshold=0.7, fee_rate=0.001, slippage_rate=0.001),
    )
    assert result["trades"] == 1
    assert result["final_capital"] < 1200
    assert result["final_capital"] > 1000
    assert result["roi"] > 0


def test_invalid_position_fraction_rejected():
    try:
        simulate([], PortfolioConfig(position_fraction=1.1))
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
