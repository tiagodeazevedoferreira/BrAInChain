from datetime import datetime, timezone

import pytest

from brainchain.data_acquisition import CMCConfig, CoinMarketCapClient, DataAcquisitionError, normalize_listing, normalize_listings


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("HTTP error")

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.response


def sample_record():
    return {
        "id": 123,
        "name": "Example Coin",
        "symbol": "EXM",
        "slug": "example-coin",
        "date_added": "2026-08-17T00:00:00.000Z",
        "cmc_rank": 999,
        "circulating_supply": 1000000,
        "total_supply": 2000000,
        "max_supply": 3000000,
        "num_market_pairs": 12,
        "quote": {"USD": {"price": 0.00031, "market_cap": 310, "volume_24h": 100, "percent_change_1h": 5, "percent_change_24h": 25, "percent_change_7d": 80}},
    }


def sample_record_list_quote():
    record = sample_record()
    record["quote"] = [
        {"symbol": "USD", "price": 0.00031, "market_cap": 310, "volume_24h": 100, "percent_change_1h": 5, "percent_change_24h": 25, "percent_change_7d": 80}
    ]
    return record


def test_normalize_listing_creates_stable_snapshot():
    captured = datetime(2026, 8, 17, tzinfo=timezone.utc)
    snapshot = normalize_listing(sample_record(), captured_at=captured)
    assert snapshot["source"] == "coinmarketcap"
    assert snapshot["source_id"] == 123
    assert snapshot["price_usd"] == 0.00031
    assert snapshot["captured_at"] == "2026-08-17T00:00:00+00:00"
    assert snapshot["raw"]["symbol"] == "EXM"


def test_normalize_listing_accepts_current_list_quote_shape():
    captured = datetime(2026, 8, 17, tzinfo=timezone.utc)
    snapshot = normalize_listing(sample_record_list_quote(), captured_at=captured)
    assert snapshot["price_usd"] == 0.00031
    assert snapshot["market_cap_usd"] == 310
    assert snapshot["percent_change_24h"] == 25


def test_normalize_listing_rejects_invalid_quote_shape():
    record = sample_record()
    record["quote"] = "invalid"
    with pytest.raises(ValueError):
        normalize_listing(record)


def test_normalize_listings_uses_one_capture_timestamp():
    captured = datetime(2026, 8, 17, tzinfo=timezone.utc)
    payload = {"data": [sample_record(), {**sample_record(), "id": 124}]}
    snapshots = normalize_listings(payload, captured_at=captured)
    assert len(snapshots) == 2
    assert snapshots[0]["captured_at"] == snapshots[1]["captured_at"]


def test_client_adds_api_key_when_configured():
    session = FakeSession(FakeResponse({"data": []}))
    config = CMCConfig(api_key="test-key", base_url="https://example.test")
    client = CoinMarketCapClient(config, session=session)
    client.listings_latest(limit=10)
    _, kwargs = session.calls[0]
    assert kwargs["headers"]["X-CMC_PRO_API_KEY"] == "test-key"
    assert kwargs["params"]["limit"] == 10


def test_client_rejects_invalid_limit():
    client = CoinMarketCapClient(session=FakeSession(FakeResponse({"data": []})))
    with pytest.raises(ValueError):
        client.listings_latest(limit=0)


def test_client_rejects_invalid_response_shape():
    client = CoinMarketCapClient(session=FakeSession(FakeResponse({"status": {}})))
    with pytest.raises(DataAcquisitionError):
        client.listings_latest()
