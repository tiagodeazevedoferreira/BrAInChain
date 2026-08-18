"""Simple deterministic portfolio simulation for offline model signals."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class PortfolioConfig:
    initial_capital: float = 1000.0
    threshold: float = 0.70
    fee_rate: float = 0.001
    slippage_rate: float = 0.001
    position_fraction: float = 1.0


def simulate(rows: Iterable[Mapping[str, Any]], config: PortfolioConfig | None = None) -> dict[str, Any]:
    """Simulate one-bar entries/exits from precomputed probabilities and prices.

    Each row is a decision point with ``probability``, ``target_return`` and
    optionally ``price``. A qualifying signal invests a fixed fraction of current
    capital and realizes ``target_return`` on the next observed outcome. Fees and
    slippage are charged on entry and exit. This is an offline abstraction, not
    an exchange execution engine.
    """
    cfg = config or PortfolioConfig()
    if not 0 <= cfg.position_fraction <= 1:
        raise ValueError("position_fraction must be between 0 and 1")
    if cfg.initial_capital <= 0:
        raise ValueError("initial_capital must be positive")

    capital = float(cfg.initial_capital)
    equity_peak = capital
    max_drawdown = 0.0
    trades = []

    for row in rows:
        probability = row.get("probability")
        target_return = row.get("target_return")
        if probability is None or target_return is None:
            continue
        if float(probability) < cfg.threshold:
            continue

        allocation = capital * cfg.position_fraction
        entry_cost = allocation * cfg.fee_rate
        effective_return = float(target_return) - cfg.slippage_rate * 2
        gross_pnl = allocation * effective_return
        exit_cost = max(0.0, allocation + gross_pnl) * cfg.fee_rate
        capital += gross_pnl - entry_cost - exit_cost
        trades.append({"return": effective_return, "pnl": gross_pnl - entry_cost - exit_cost})
        equity_peak = max(equity_peak, capital)
        drawdown = (equity_peak - capital) / equity_peak if equity_peak else 0.0
        max_drawdown = max(max_drawdown, drawdown)

    pnl = capital - cfg.initial_capital
    wins = sum(1 for trade in trades if trade["pnl"] > 0)
    losses = sum(1 for trade in trades if trade["pnl"] < 0)
    gross_profit = sum(trade["pnl"] for trade in trades if trade["pnl"] > 0)
    gross_loss = -sum(trade["pnl"] for trade in trades if trade["pnl"] < 0)

    return {
        "initial_capital": cfg.initial_capital,
        "final_capital": capital,
        "roi": pnl / cfg.initial_capital,
        "trades": len(trades),
        "win_rate": wins / len(trades) if trades else 0.0,
        "max_drawdown": max_drawdown,
        "profit_factor": gross_profit / gross_loss if gross_loss else (float("inf") if gross_profit else 0.0),
        "wins": wins,
        "losses": losses,
    }
