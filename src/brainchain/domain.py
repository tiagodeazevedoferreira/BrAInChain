from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class MarketSnapshot(BaseModel):
    """A point-in-time observation; fields must be knowable at observed_at."""

    token_id: str
    observed_at: datetime
    price_usd: float = Field(ge=0)
    market_cap_usd: float | None = Field(default=None, ge=0)
    volume_24h_usd: float | None = Field(default=None, ge=0)
    liquidity_usd: float | None = Field(default=None, ge=0)
    buy_count: int | None = Field(default=None, ge=0)
    sell_count: int | None = Field(default=None, ge=0)
    holder_count: int | None = Field(default=None, ge=0)


class Prediction(BaseModel):
    token_id: str
    observed_at: datetime
    horizon_minutes: int = Field(gt=0)
    target_multiple: float = Field(gt=1)
    probability: float = Field(ge=0, le=1)
    risk_score: float = Field(ge=0, le=1)
    decision: str
    model_version: str
