from datetime import datetime, timezone

from brainchain.domain import MarketSnapshot
from brainchain.scoring import baseline_score


def test_baseline_score_is_bounded():
    snapshot = MarketSnapshot(
        token_id="demo",
        observed_at=datetime.now(timezone.utc),
        price_usd=0.00031,
        market_cap_usd=500_000,
        volume_24h_usd=2_000_000,
        liquidity_usd=200_000,
        buy_count=800,
        sell_count=200,
        holder_count=20_000,
    )

    score = baseline_score(snapshot)
    assert 0 <= score <= 100
    assert score > 50
