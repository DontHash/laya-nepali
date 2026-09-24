"""Pinned upstream versions for reproducibility.

``MODEL_REVISION`` is the Hugging Face snapshot commit downloaded for the seed
probe; every benchmark run pins it so numbers stay comparable across time.
"""

from __future__ import annotations

LAYA_VERSION = "0.3.20"
MODEL_REPO = "convaiinnovations/laya"
MODEL_REVISION = "55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851"
ENGLISH_SUBFOLDER: str | None = None
MULTILINGUAL_SUBFOLDER = "multilingual"
