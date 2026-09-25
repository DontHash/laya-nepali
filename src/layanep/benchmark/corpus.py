"""Frozen Nepali benchmark corpus (ne-probe-v1).

The benchmark is versioned separately from the training export so that no
benchmark step can leak into training. Steps carry a message, language
(``en`` | ``ne-rom`` | ``ne``) and the expected decision, mirroring the
``lu-probe-v1`` shape from OrderWorkFlow.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from ..schema import LU_COMMAND_KINDS

BENCHMARK_REVISION = "ne-probe-v1"
BENCHMARK_REVISIONS = ("ne-probe-v1", "ne-bench-deva-v2")
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CORPUS_PATH = REPO_ROOT / "data" / "benchmark" / "ne-probe-v1.json"
LANGUAGES = ("en", "ne-rom", "ne")


@dataclass(frozen=True)
class ProbeStep:
    id: str
    language: str
    text: str
    expected: str | None
    note: str | None = None


@dataclass(frozen=True)
class ProbeCase:
    id: str
    category: str
    description: str
    menu_id: str
    steps: tuple[ProbeStep, ...]


@dataclass(frozen=True)
class ProbeCorpus:
    revision: str
    source: str
    businesses: Mapping[str, Any]
    cases: tuple[ProbeCase, ...]

    @property
    def steps(self) -> tuple[ProbeStep, ...]:
        return tuple(step for case in self.cases for step in case.steps)

    def business(self, menu_id: str) -> Mapping[str, Any]:
        return self.businesses[menu_id]


def load_corpus(path: Path | None = None) -> ProbeCorpus:
    corpus_path = path or DEFAULT_CORPUS_PATH
    data = json.loads(corpus_path.read_text(encoding="utf-8"))
    cases = tuple(
        ProbeCase(
            id=str(case["id"]),
            category=str(case["category"]),
            description=str(case["description"]),
            menu_id=str(case["menuId"]),
            steps=tuple(
                ProbeStep(
                    id=str(step["id"]),
                    language=str(step["language"]),
                    text=str(step["text"]),
                    expected=step.get("expected"),
                    note=step.get("note"),
                )
                for step in case["steps"]
            ),
        )
        for case in data["cases"]
    )
    return ProbeCorpus(
        revision=str(data["revision"]),
        source=str(data["source"]),
        businesses=dict(data["businesses"]),
        cases=cases,
    )


def validate_corpus(corpus: ProbeCorpus) -> list[str]:
    failures: list[str] = []
    if corpus.revision not in BENCHMARK_REVISIONS:
        failures.append(
            f"unknown revision {corpus.revision!r} (known: {', '.join(BENCHMARK_REVISIONS)})"
        )

    step_ids: set[str] = set()
    for case in corpus.cases:
        if case.menu_id not in corpus.businesses:
            failures.append(f"{case.id}: unknown menuId {case.menu_id!r}")
        for step in case.steps:
            if step.id in step_ids:
                failures.append(f"duplicate step id {step.id!r}")
            step_ids.add(step.id)
            if step.language not in LANGUAGES:
                failures.append(f"{case.id}/{step.id}: unknown language {step.language!r}")
            if step.expected is not None and step.expected not in LU_COMMAND_KINDS:
                failures.append(f"{case.id}/{step.id}: unknown expected kind {step.expected!r}")

    steps = corpus.steps
    covered = {step.expected for step in steps if step.expected}
    missing = [kind for kind in LU_COMMAND_KINDS if kind not in covered]
    if missing:
        failures.append(f"corpus misses LU kinds: {missing}")
    abstain = [step for step in steps if step.expected is None]
    if len(abstain) < 12:
        failures.append(f"abstain set too small ({len(abstain)} < 12)")
    if len(steps) < 60:
        failures.append(f"corpus too small ({len(steps)} < 60)")
    return failures
