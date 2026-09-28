"""Dataset export (P1c).

Reads the reviewed rows, splits them deterministically into train/calibration,
checks that no training message coincides with a benchmark step, and writes the
frozen export plus a manifest to ``data/export``.

The benchmark corpora stay separate: benchmark steps never enter a training
split (AGENTS.md), and the leakage check below enforces it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .benchmark.corpus import load_corpus
from .normalize import normalize_text
from .schema import DATASET_REVISION, Case
from .validate import load_cases, validate_dataset

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REVIEWED = REPO_ROOT / "data" / "reviewed" / "ne-decisions-v1.jsonl"
DEFAULT_EXPORT_DIR = REPO_ROOT / "data" / "export"
DEFAULT_BENCHMARK_PATHS = (
    REPO_ROOT / "data" / "benchmark" / "ne-probe-v1.json",
    REPO_ROOT / "data" / "benchmark" / "ne-bench-deva-v2.json",
)
CALIBRATION_SHARE = 0.1


@dataclass
class ExportReport:
    train: int
    calibration: int
    manifest: Path

    def summary(self) -> str:
        return f"export {DATASET_REVISION}: train {self.train} | calibration {self.calibration}"


def split_for(case_id: str, calibration_share: float = CALIBRATION_SHARE) -> str:
    digest = hashlib.sha1(case_id.encode("utf-8")).hexdigest()
    return "calibration" if int(digest, 16) % 1000 < calibration_share * 1000 else "train"


def split_cases(cases: Sequence[Case], *, calibration_share: float = CALIBRATION_SHARE) -> dict[str, list[Case]]:
    splits = {"train": [], "calibration": []}
    for case in cases:
        splits[split_for(case.id, calibration_share)].append(case)
    return splits


def benchmark_texts(paths: Sequence[Path] = DEFAULT_BENCHMARK_PATHS) -> set[str]:
    texts: set[str] = set()
    for path in paths:
        if not path.exists():
            continue
        for step in load_corpus(path).steps:
            texts.add(normalize_text(step.text).lower())
    return texts


def leakage_failures(cases: Sequence[Case], texts: set[str]) -> list[str]:
    failures: list[str] = []
    for case in cases:
        message = normalize_text(str(case.state.get("customer_message", ""))).lower()
        if message and message in texts:
            failures.append(f"{case.id}: message matches a benchmark step")
    return failures


def _count_by(cases: Sequence[Case], key: str, default: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for case in cases:
        value = str(case.provenance.get(key, default))
        counts[value] = counts.get(value, 0) + 1
    return counts


def _display_path(path: Path | None) -> str | None:
    """Record repo-relative paths in manifests so they stay machine-neutral."""
    if path is None:
        return None
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def write_export(
    cases: Sequence[Case],
    export_dir: Path = DEFAULT_EXPORT_DIR,
    *,
    calibration_share: float = CALIBRATION_SHARE,
    reviewed_from: Path | None = None,
) -> ExportReport:
    splits = split_cases(cases, calibration_share=calibration_share)
    export_dir.mkdir(parents=True, exist_ok=True)
    for name, split in splits.items():
        path = export_dir / f"{DATASET_REVISION}-{name}.jsonl"
        with path.open("w", encoding="utf-8") as sink:
            for case in split:
                sink.write(json.dumps(case.to_row(), ensure_ascii=False) + "\n")

    manifest = {
        "revision": DATASET_REVISION,
        "generated_from": _display_path(reviewed_from),
        "calibration_share": calibration_share,
        "splits": {name: len(split) for name, split in splits.items()},
        "review_modes": _count_by(cases, "review_mode", "human"),
        "sources": _count_by(cases, "source", "unknown"),
    }
    manifest_path = export_dir / f"{DATASET_REVISION}.manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ExportReport(train=len(splits["train"]), calibration=len(splits["calibration"]), manifest=manifest_path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Freeze the reviewed dataset into data/export.")
    parser.add_argument("--reviewed", type=Path, default=DEFAULT_REVIEWED)
    parser.add_argument("--out", type=Path, default=DEFAULT_EXPORT_DIR)
    parser.add_argument("--calibration-share", type=float, default=CALIBRATION_SHARE)
    args = parser.parse_args(argv)

    if not args.reviewed.exists():
        print(f"no reviewed dataset at {args.reviewed}")
        return 1
    cases = load_cases(args.reviewed)
    failures = validate_dataset(cases, require_reviewed=True)
    failures.extend(leakage_failures(cases, benchmark_texts()))
    if failures:
        print(f"export FAIL: {len(failures)} problem(s), nothing written")
        for failure in failures[:20]:
            print(f"  - {failure}")
        return 1

    report = write_export(
        cases,
        args.out,
        calibration_share=args.calibration_share,
        reviewed_from=args.reviewed,
    )
    print(report.summary())
    print(f"wrote {report.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
