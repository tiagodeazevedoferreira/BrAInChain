"""Build a deterministic training-ready view from Firebase snapshots."""
from __future__ import annotations

from typing import Any, Mapping

from brainchain.firebase_dataset import prepare_dataset


def build_training_rows(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Read the snapshot map and keep chronological observations per asset.

    This stage intentionally does not invent labels. Future-return labels require
    a defined horizon and price field and are added by the label engine later.
    """
    return prepare_dataset(payload)
