# BrAInChain Roadmap

## Phase 1 — Research foundation

- [x] Repository structure
- [x] Point-in-time market data contract
- [x] Prediction contract
- [x] Deterministic baseline scorer
- [x] Automated tests
- [x] CI workflow

## Phase 2 — Data acquisition

- [ ] CoinMarketCap connector
- [ ] CoinGecko connector
- [ ] DEX/on-chain connector
- [ ] Raw snapshot persistence
- [ ] Firebase Realtime Database adapter

## Phase 3 — Learning dataset

- [ ] Snapshot resampling
- [ ] Feature engineering
- [ ] 2x/5x/10x/50x/100x outcome labels
- [ ] Leakage checks
- [ ] Train/validation/test split by time

## Phase 4 — ML

- [ ] Logistic regression baseline
- [ ] Gradient boosting
- [ ] Probability calibration
- [ ] Growth model
- [ ] Risk model
- [ ] Scam/contract risk model
- [ ] Model registry

## Phase 5 — Simulation

- [ ] Historical backtester
- [ ] Walk-forward evaluation
- [ ] Fees and slippage model
- [ ] Liquidity constraints
- [ ] Paper trading

## Phase 6 — Automation

- [ ] Real-time scoring
- [ ] Monitoring dashboard
- [ ] Alerts
- [ ] Automatic retraining pipeline
- [ ] Model promotion gates

## Phase 7 — Execution

Only after extensive paper-trading validation:

- [ ] Exchange adapter
- [ ] Risk engine
- [ ] Position sizing
- [ ] Circuit breakers
- [ ] Manual kill switch
- [ ] Small-capital live pilot
