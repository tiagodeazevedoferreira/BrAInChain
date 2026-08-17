# BrAInChain

Crypto AI research and automation platform.

## Vision

BrAInChain is being built as a research-first platform for discovering patterns associated with extreme cryptocurrency price movements. The system will collect historical and near-real-time market data, transform observations into features, train and validate machine-learning models, and eventually support paper trading before any real-money execution is considered.

**Important:** Version 1 is intentionally research-only. It does not place real-money trades.

## V1 scope

- Project architecture and documentation
- Data ingestion interfaces
- Normalized crypto market snapshot model
- Feature-engineering foundation
- Deterministic baseline scoring model
- Backtesting/labeling foundation
- Configuration through environment variables
- Automated quality checks with GitHub Actions
- Clear separation between research, prediction, risk, and execution layers

## Architecture

```text
Data Sources
    |
    v
Ingestion -> Normalization -> Storage
                              |
                              v
                       Feature Engineering
                              |
                              v
                       Model / Baseline
                              |
                    +---------+---------+
                    |                   |
                    v                   v
                Evaluation          Risk Gate
                    |                   |
                    +---------+---------+
                              v
                       Paper Trading
                              |
                              v
                       Future Execution
```

## Development principles

1. No real-money trading in the initial versions.
2. Historical snapshots must represent only information available at the prediction timestamp to avoid data leakage.
3. Models are versioned and evaluated before promotion.
4. The risk layer can veto a model recommendation.
5. Raw data should be preserved whenever possible so features can be regenerated later.
6. Secrets are never committed to the repository.

## Planned evolution

- [x] Repository foundation
- [x] V1 research architecture
- [x] Data contracts
- [x] Baseline scoring engine
- [x] Initial tests and CI
- [x] CoinMarketCap acquisition client
- [x] Snapshot normalization
- [x] Firebase persistence adapter
- [x] Manual GitHub Actions collection workflow
- [ ] Scheduled market collection
- [ ] CoinGecko connector
- [ ] Historical dataset builder
- [ ] 2x/5x/10x outcome labeling
- [ ] Gradient-boosting model
- [ ] Walk-forward backtesting
- [ ] Paper trading engine
- [ ] Model registry and promotion rules
- [ ] Real-time monitoring
- [ ] Exchange execution adapter

## Local development

The research/ML layer uses Python. CoinMarketCap collection and Firebase persistence are implemented as independent adapters so additional data sources and storage backends can be added without coupling the model to an API.

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
# source .venv/bin/activate
pip install -r requirements.txt
pytest
```

For acquisition configuration, copy `.env.example` to `.env` and provide the Firebase database URL and service-account JSON when persistence is required. Never commit real credentials.
