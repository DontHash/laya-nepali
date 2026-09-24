"""Frozen Nepali benchmark corpus (P1).

The benchmark is versioned separately from the training export so that no
benchmark step can leak into training. Steps carry a message, language
(``en`` | ``ne-rom`` | ``ne``) and the expected decision, mirroring the
``lu-probe-v1`` shape from OrderWorkFlow. Populated in P1.
"""

from __future__ import annotations

BENCHMARK_REVISION = "ne-benchmark-v0"
