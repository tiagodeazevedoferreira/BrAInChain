from __future__ import annotations

from .domain import MarketSnapshot


def baseline_score(snapshot: MarketSnapshot) -> float:
    """Return a deterministic 0-100 research score.

    This is deliberately NOT a trained model. It is a reproducible baseline used
    to validate the data pipeline before machine learning is introduced.
    """

    score = 0.0

    if snapshot.liquidity_usd is not None and snapshot.liquidity_usd >= 100_000:
        score += 25
    elif snapshot.liquidity_usd is not None and snapshot.liquidity_usd >= 25_000:
        score += 15

    if snapshot.volume_24h_usd is not None and snapshot.volume_24h_usd >= 1_000_000:
        score += 25
    elif snapshot.volume_24h_usd is not None and snapshot.volume_24h_usd >= 100_000:
        score += 15

    if snapshot.buy_count is not None and snapshot.sell_count is not None:
        total = snapshot.buy_count + snapshot.sell_count
        if total:
            buy_ratio = snapshot.buy_count / total
            score += max(0.0, min(25.0, (buy_ratio - 0.5) * 100))

    if snapshot.holder_count is not None:
        if snapshot.holder_count >= 10_000:
            score += 25
        elif snapshot.holder_count >= 1_000:
            score += 15
        elif snapshot.holder_count >= 100:
            score += 5

    return round(min(100.0, max(0.0, score)), 2)
