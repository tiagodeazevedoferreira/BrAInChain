"""Collect a CMC market snapshot batch and optionally persist it to Firebase."""

from __future__ import annotations

import argparse
import logging

from brainchain.data_acquisition import CoinMarketCapClient, CMCConfig, normalize_listings
from brainchain.firebase_store import FirebaseStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--dry-run", action="store_true", help="Fetch and normalize without writing Firebase")
    args = parser.parse_args()

    client = CoinMarketCapClient(CMCConfig.from_environment())
    payload = client.listings_latest(limit=args.limit)
    snapshots = normalize_listings(payload)

    logger.info("Collected %d CMC listings", len(snapshots))
    if snapshots:
        logger.info("First snapshot: %s %s USD", snapshots[0]["symbol"], snapshots[0]["price_usd"])

    if not args.dry_run:
        count = FirebaseStore().write_snapshots(snapshots)
        logger.info("Persisted %d snapshots to Firebase", count)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
