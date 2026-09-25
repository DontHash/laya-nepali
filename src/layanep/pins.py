"""Pinned upstream versions for reproducibility.

``MODEL_REVISION`` is the Hugging Face snapshot commit downloaded for the seed
probe. ``laya.load`` does not accept a ``revision`` argument, so the pin is
enforced by loading the cached snapshot directory when it exists (see
``benchmark.runner._pinned_model_path``); otherwise the loader falls back to
the hub's current main.
"""

from __future__ import annotations

LAYA_VERSION = "0.3.20"
MODEL_REPO = "convaiinnovations/laya"
MODEL_REVISION = "55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851"
ENGLISH_SUBFOLDER: str | None = None
MULTILINGUAL_SUBFOLDER = "multilingual"
