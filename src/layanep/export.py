"""Dataset export (P1/P3).

Serialises the reviewed set into the fine-tune row shape, split by template
family, and writes the deterministic JSONL consumed by the eval gate and the
Kaggle notebook. Populated in P1.
"""

from __future__ import annotations

EXPORT_REVISION = "export-v0"
