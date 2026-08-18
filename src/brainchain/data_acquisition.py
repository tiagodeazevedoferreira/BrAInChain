"""CoinMarketCap data acquisition primitives.

Fetching, normalization, and persistence are deliberately separated so the
same collector can feed Firebase, local files, tests, or another backend.
"""

from __future__ import annotations

import os
import time
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
    max_retries: int = 4
    backoff_seconds: float = 2.0

    @classmethod
    def from_environment(cls) -> "CMCConfig":
        return cls(
            api_key=os.getenv("CMC_API_KEY"),
            base_url=os.getenv("CMC_BASE_URL"),
            timeout_seconds=float(os.getenv("CMC_TIMEOUT_SECONDS", "15")),
            max_retries=int(os.getenv("CMC_MAX_RETRIES", "4")),
            backoff_seconds=float(os.getenv("CMC_BACKOFF_SECONDS", "2")),
        )

    @property
    def resolved_base_url(self) -> str:
        if self.base_url:
            return self.base_url.rstrip("/")
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
        if self.config.max_retries < 0:
            raise ValueError("max_retries must be >= 0")

        headers = {"Accept": "application/json"}
        if self.config.api_key:
            headers["X-CMC_PRO_API_KEY"] = self.config.api_key

        url = f"{self.config.resolved_base_url}/v3/cryptocurrency/listings/latest"
        attempts = self.config.max_retries + 1

        for attempt in range(attempts):
            try:
                response = self.session.get(
                    url,
                    params={"start": start, "limit": limit, "convert": convert},
                    headers=headers,
                    timeout=self.config.timeout_seconds,
                )
            except requests.RequestException as exc:
                if attempt >= self.config.max_retries:
                    raise DataAcquisitionError(f"CoinMarketCap request failed: {exc}") from exc
                time.sleep(self.config.backoff_seconds * (2**attempt))
                continue

            if response.status_code == 429:
                if attempt >= self.config.max_retries:
                    raise DataAcquisitionError(
                        f"CoinMarketCap rate limit exceeded after {attempts} attempts (HTTP 429)"
                    )
                retry_after = response.headers.get("Retry-After")
                try:
                    delay = float(retry_after) if retry_after is not None else self.config.backoff_seconds * (2**attempt)
                except ValueError:
                    delay = self.config.backoff_seconds * (2**attempt)
                time.sleep(max(0.0, delay))
                continue

            try:
                response.raise_for_status()
                payload = response.json()
            except (requests.RequestException, ValueError) as exc:
                raise DataAcquisitionError(f"CoinMarketCap request failed: {exc}") from exc

            if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
                raise DataAcquisitionError("CoinMarketCap returned an unexpected response shape")
            return payload

        raise DataAcquisitionError("CoinMarketCap request failed unexpectedly")


def _usd_quote(record: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return the USD quote from CMC's current response shape.

    CMC V3 returns ``quote`` as a list of currency quote objects. Older
    integrations may still provide the legacy mapping shape ``quote.USD``.
    Invalid quote shapes are rejected rather than silently converted to an
    empty quote, preventing corrupt snapshots from entering the dataset.
    """
    quote = record.get("quote")

    if isinstance(quote, Mapping):
        usd = quote.get("USD")
        if usd is None:
            raise ValueError("listing quote mapping does not contain USD")
        if not isinstance(usd, Mapping):
            raise ValueError("listing USD quote must be a mapping")
        return usd

    if isinstance(quote, list):
        for item in quote:
            if isinstance(item, Mapping) and str(item.get("symbol", "")).upper() == "USD":
                return item
        raise ValueError("listing quote list does not contain USD")

    raise ValueError("listing quote must be a mapping or list")


def normalize_listing(record: Mapping[str, Any], *, captured_at: datetime | None = None) -> dict[str, Any]:
    """Convert a CMC listing into a stable, storage-friendly snapshot."""
    quote = _usd_quote(record)
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
    data = payload.get("data")
    if not isinstance(data, list):
        raise DataAcquisitionError("CoinMarketCap response data must be a list")

    captured = captured_at or datetime.now(timezone.utc)
    return [normalize_listing(item, captured_at=captured) for item in data]
