# Data Acquisition V1

## CoinMarketCap

The collector uses `GET /v3/cryptocurrency/listings/latest`. CMC documents this as the current listings endpoint for active cryptocurrencies. The collector can use `CMC_API_KEY` when available; without a key it falls back to CMC's documented no-key trial endpoint.

The first snapshot schema intentionally captures the fields needed for future feature engineering:

- stable CMC ID
- name/symbol/slug
- date added
- capture timestamp
- CMC rank
- price and market cap
- 24h volume
- 1h/24h/7d percentage changes
- supply metrics
- number of market pairs
- original raw CMC record

The raw record is preserved because future features may require fields that are not yet modeled explicitly.

## Firebase

Firebase Realtime Database is an optional persistence target for the acquisition layer. Credentials are injected through environment variables or GitHub Actions secrets. No service-account JSON is committed to the repository.

Snapshots are written under:

```text
snapshots/<coinmarketcap-id>/<captured-timestamp>
```

This preserves the temporal observation needed for later label generation and backtesting.

## Manual GitHub Actions run

The workflow `.github/workflows/collect-market.yml` is intentionally **manual in V1**. This prevents unexpected API consumption or database writes while credentials and retention rules are being validated.

Required GitHub repository secrets:

- `CMC_API_KEY` (optional while using the documented trial endpoint)
- `FIREBASE_DATABASE_URL`
- `FIREBASE_CREDENTIALS_JSON`

Once the pipeline has been validated, we can add a scheduled trigger and define collection frequency based on API quotas and the granularity needed for the model.
