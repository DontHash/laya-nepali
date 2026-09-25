"""Benchmark report builder: markdown + JSON pair in Laya's report style."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from .runner import ProbeScore


def _rate(correct: int, total: int) -> str:
    return "n/a" if total == 0 else f"{correct / total * 100:.1f}%"


def _ms(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1f} ms"


def build_report_markdown(meta: Mapping[str, Any], score: "ProbeScore") -> str:
    lines = [
        f"# Nepali probe report - {score.classifier}",
        "",
        f"- Generated: {meta['generated_at']}",
        f"- Corpus revision: {score.revision}",
        f"- Commit: {meta.get('commit') or 'unknown'}",
        f"- Steps: {score.total}",
        f"- Model correct: {score.correct}/{score.total} ({_rate(score.correct, score.total)})",
        f"- Abstain: {score.abstain_correct}/{score.abstain_total}",
        f"- Latency: p50 {_ms(score.latency_p50)} | p95 {_ms(score.latency_p95)}",
        f"- Classifier errors: {score.errors}",
        f"- Config: classifier={meta['classifier']}, device={meta.get('device', 'auto')}, "
        f"threshold={meta.get('threshold', 'n/a')}",
        "",
        "## Per kind",
        "",
        "| kind | expected | correct | predicted | false positives |",
        "|---|---|---|---|---|",
    ]
    for kind, stats in score.per_kind.items():
        lines.append(f"| {kind} | {stats.expected} | {stats.correct} | {stats.predicted} | {stats.false_positive} |")

    misses = [result for result in score.results if result.predicted != result.expected]
    lines.extend(["", "## Misses", ""])
    if not misses:
        lines.append("- none")
    for result in misses:
        expected = result.expected or "abstain"
        got = f"error: {result.error}" if result.error else (result.predicted or "abstain")
        lines.append(
            f'- `{result.case_id}/{result.step_id}` ({result.language}) "{result.text}" '
            f"- expected `{expected}`, got `{got}`"
        )

    lines.extend(
        [
            "",
            "## Method",
            "",
            "- Corpus: `data/benchmark/ne-probe-v1.json` (ported from OrderWorkFlow `lu-probe-v1`).",
            "- The Laya classifier runs in-process (`Agent.system_one`) with a single 16-option `choice` "
            "question; Devanagari routes to `multilingual`, Latin text to `english`.",
            "- Metrics are model-only; composite/gap metrics from OrderWorkFlow need the deterministic "
            "dialogue classifier and are out of scope here.",
            "- Pinned upstream: see `src/layanep/pins.py`.",
            "",
        ]
    )
    return "\n".join(lines)


def build_report_json(meta: Mapping[str, Any], score: "ProbeScore") -> str:
    payload = {
        "meta": dict(meta),
        "score": {
            "classifier": score.classifier,
            "revision": score.revision,
            "total": score.total,
            "correct": score.correct,
            "abstain_total": score.abstain_total,
            "abstain_correct": score.abstain_correct,
            "per_kind": {kind: stats.__dict__ for kind, stats in score.per_kind.items()},
            "latency_p50": score.latency_p50,
            "latency_p95": score.latency_p95,
            "errors": score.errors,
            "results": [result.__dict__ for result in score.results],
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
