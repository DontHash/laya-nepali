"""Benchmark runner (P2).

Scores a Laya checkpoint against the frozen corpus: per-kind accuracy, abstain
accuracy, safety false commands, ECE after temperature fitting, and latency
p50/p95. Populated in P2.
"""

from __future__ import annotations
