"""CoinMarketCap data acquisition primitives.

Fetching, normalization, and persistence are deliberately separated so the
same collector can feed Firebase, local files, tests, or another backend.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

import requests


CMC_BASE_URL = "https://pro-api.coinmarketcap.com"
CMC_TRIAL_BASE_URL = "https://pro-api.coinmarketcap.com/trial-pro-api"


class DataAcquisitionError(RuntimeError):
    """Raised when an upstream data source cannot be consumed safely."""


@dataclass(frozen=True)
class CMCConfig:
    api_key: str | None = None
    base_url: str | None = None
    timeout_seconds: float = 15.0

    @classmethod
    def from_environment(cls) -> "CMCConfig":
        return cls(
            api_key=os.getenv("CMC_API_KEY"),
            base_url=os.getenv("CMC_BASE_URL"),
            timeout_seconds=float(os.getenv("CMC_TIMEOUT_SECONDS", "15")),
        )

    @property
    def resolved_base_url(self) -> str:
        if self.base_url:
            return self.base_url.rstrip("/")
        # Keep local development possible without putting an API secret in code.
        # A configured key uses the normal production API; otherwise use CMC's
        # documented no-key trial endpoint.
        return (CMC_BASE_URL if self.api_key else CMC_TRIAL_BASE_URL).rstrip("/")


class CoinMarketCapClient:
    """Small client for CMC's current v3 listings endpoint."""

    def __init__(self, config: CMCConfig | None = None, session: requests.Session | None = None):
        self.config = config or CMCConfig.from_environment()
        self.session = session or requests.Session()

    def listings_latest(self, *, start: int = 1, limit: int = 100, convert: str = "USD") -> Mapping[str, Any]:
        if not 1 <= limit <= 5000:
            raise ValueError("limit must be between 1 and 5000")
        if start < 1:
            raise ValueError("start must be >= 1")

        headers = {"Accept": "application/json"}
        if self.config.api_key:
            headers["X-CMC_PRO_API_KEY"] = self.config.api_key

        url = f"{self.config.resolved_base_url}/v3/cryptocurrency/listings/latest"
        try:
            response = self.session.get(
                url,
                params={"start": start, "limit": limit, "convert": convert},
                headers=headers,
                timeout=self.config.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise DataAcquisitionError(f"CoinMarketCap request failed: {exc}") from exc

        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            raise DataAcquisitionError("CoinMarketCap returned an unexpected response shape")
        return payload


def normalize_listing(record: Mapping[str, Any], *, captured_at: datetime | None = None) -> dict[str, Any]:
    """Convert a CMC listing into a stable, storage-friendly snapshot."""
    quote = record.get("quote", {}).get("USD", {})
    captured = captured_at or datetime.now(timezone.utc)

    return {
        "source": "coinmarketcap",
        "source_id": record.get("id"),
        "symbol": record.get("symbol"),
        "name": record.get("name"),
        "slug": record.get("slug"),
        "date_added": record.get("date_added"),
        "captured_at": captured.isoformat(),
        "cmc_rank": record.get("cmc_rank"),
        "price_usd": quote.get("price"),
        "market_cap_usd": quote.get("market_cap"),
        "volume_24h_usd": quote.get("volume_24h"),
        "percent_change_1h": quote.get("percent_change_1h"),
        "percent_change_24h": quote.get("percent_change_24h"),
        "percent_change_7d": quote.get("percent_change_7d"),
        "circulating_supply": record.get("circulating_supply"),
        "total_supply": record.get("total_supply"),
        "max_supply": record.get("max_supply"),
        "num_market_pairs": record.get("num_market_pairs"),
        "raw": dict(record),
    }


def normalize_listings(payload: Mapping[str, Any], *, captured_at: datetime | None = None) -> list[dict[str, Any]]:
    """Normalize all listings from one CMC response using one capture timestamp."""
    captured = captured_at or datetime.now(timezone.utc)
    return [normalize_listing(item, captured_at=captured) for item in payload["data"]]
