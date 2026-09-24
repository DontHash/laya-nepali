"""Deterministic eval gate: schema, duplicates, PII, and the frozen revision.

Runs without network or model weights so CI can execute it on every push.
By default it loads ``data/export`` when that directory has dataset files and
falls back to the golden fixtures, which keeps the gate meaningful from P0
onward.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .schema import DATASET_REVISION
from .validate import load_cases, validate_dataset

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPO_ROOT / "data" / "export"
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures"


@dataclass
class GateResult:
    paths: list[Path]
    cases: int
    decisions: int
    failures: list[str]
    revision: str = DATASET_REVISION

    @property
    def passed(self) -> bool:
        return not self.failures


def resolve_paths(paths: Sequence[Path] | None) -> list[Path]:
    if paths:
        return [Path(p) for p in paths]
    if DEFAULT_DATA_DIR.exists() and any(DEFAULT_DATA_DIR.glob("*.json*")):
        return [DEFAULT_DATA_DIR]
    return [FIXTURE_DIR]


def run_gate(paths: Sequence[Path] | None = None) -> GateResult:
    resolved = resolve_paths(paths)
    cases = []
    failures: list[str] = []
    for path in resolved:
        try:
            cases.extend(load_cases(path))
        except Exception as exc:  # noqa: BLE001 - the gate reports every load problem as a failure
            failures.append(f"{path}: {exc}")
    if not cases and not failures:
        failures.append(f"no cases found under {[str(p) for p in resolved]}")
    failures.extend(validate_dataset(cases))
    return GateResult(
        paths=resolved,
        cases=len(cases),
        decisions=sum(len(case.questions) for case in cases),
        failures=failures,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic dataset gate for laya-nepali.")
    parser.add_argument("--check", action="store_true", help="run the gate (default action)")
    parser.add_argument("--data", type=Path, action="append", help="dataset file or directory (repeatable)")
    args = parser.parse_args(argv)

    result = run_gate(args.data)
    sources = ", ".join(str(path) for path in result.paths)
    if result.passed:
        print(f"{result.revision} gate: {result.cases} cases, {result.decisions} decisions, PASS ({sources})")
        return 0
    print(f"{result.revision} gate: FAIL ({sources})")
    for failure in result.failures:
        print(f"  - {failure}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
