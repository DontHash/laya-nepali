"""Clothing dataset export and stratified splitting.

Reads the canonical clothing cases (``data/generated/cl-cases-v1.jsonl``),
performs a deterministic stratified split across (family, language) into:
- 80% train
- 10% calibration (for temperature fitting and tau/p_none threshold search)
- 10% test (held-out benchmark evaluation)

Enforces zero leakage between train, calibration, and test splits.
Outputs to ``data/clothing_export`` and generates ``data/benchmark/cl-bench-v1.json``.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from .clothing_questions import clothing_label_to_kind
from .normalize import normalize_text
from .schema import Case, validate_case

CLOTHING_DATASET_REVISION = "cl-decisions-v1"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = REPO_ROOT / "data" / "generated" / "cl-cases-v1.jsonl"
DEFAULT_EXPORT_DIR = REPO_ROOT / "data" / "clothing_export"
DEFAULT_BENCHMARK_PATH = REPO_ROOT / "data" / "benchmark" / "cl-bench-v1.json"
DEFAULT_SEED = 20260927


@dataclass
class ClothingExportReport:
    total: int
    train: int
    calibration: int
    test: int
    manifest_path: Path
    benchmark_path: Path

    def summary(self) -> str:
        return (
            f"export {CLOTHING_DATASET_REVISION}: total {self.total} | "
            f"train {self.train} (80%) | calibration {self.calibration} (10%) | "
            f"test {self.test} (10%)"
        )


def stratify_cases(
    cases: Sequence[Case],
    *,
    train_ratio: float = 0.8,
    cal_ratio: float = 0.1,
    test_ratio: float = 0.1,
    seed: int = DEFAULT_SEED,
) -> dict[str, list[Case]]:
    """Deterministically stratify cases by (family, language)."""
    groups: dict[tuple[str, str], list[Case]] = defaultdict(list)
    for case in cases:
        fam = str(case.provenance.get("family", "unknown"))
        lang = str(case.provenance.get("language", "unknown"))
        groups[(fam, lang)].append(case)

    rng = random.Random(seed)
    splits: dict[str, list[Case]] = {"train": [], "calibration": [], "test": []}

    for key in sorted(groups.keys()):
        group = list(groups[key])
        rng.shuffle(group)
        n = len(group)
        n_cal = max(1, round(n * cal_ratio)) if n >= 3 else 0
        n_test = max(1, round(n * test_ratio)) if n >= 3 else 0
        n_train = n - n_cal - n_test

        if n_train <= 0:
            n_train = n
            n_cal = 0
            n_test = 0

        splits["train"].extend(group[:n_train])
        splits["calibration"].extend(group[n_train : n_train + n_cal])
        splits["test"].extend(group[n_train + n_cal :])

    return splits


def check_leakage(splits: Mapping[str, Sequence[Case]]) -> list[str]:
    """Ensure zero overlap between train, calibration, and test messages."""
    train_msgs = {
        normalize_text(str(c.state.get("customer_message", ""))).lower()
        for c in splits["train"]
    }
    cal_msgs = {
        normalize_text(str(c.state.get("customer_message", ""))).lower()
        for c in splits["calibration"]
    }
    test_msgs = {
        normalize_text(str(c.state.get("customer_message", ""))).lower()
        for c in splits["test"]
    }

    failures = []
    tc_overlap = train_msgs & cal_msgs
    if tc_overlap:
        failures.append(f"{len(tc_overlap)} messages overlap between train and calibration")
    tt_overlap = train_msgs & test_msgs
    if tt_overlap:
        failures.append(f"{len(tt_overlap)} messages overlap between train and test")
    ct_overlap = cal_msgs & test_msgs
    if ct_overlap:
        failures.append(f"{len(ct_overlap)} messages overlap between calibration and test")
    return failures


def build_benchmark_corpus(test_cases: Sequence[Case]) -> dict:
    """Format the held-out test split into a ProbeCorpus JSON structure."""
    cases_by_biz: dict[str, list[Case]] = defaultdict(list)
    businesses = {}

    for c in test_cases:
        biz = c.state.get("business", {})
        biz_name = biz.get("name", "Clothing Store")
        biz_id = str(c.provenance.get("business", "store-1"))
        businesses[biz_id] = {
            "name": biz_name,
            "area": biz.get("area", ""),
            "hours": biz.get("hours", ""),
            "delivery_area": biz.get("delivery_area", ""),
            "delivery_fee_npr": biz.get("delivery_fee_npr", 100),
        }
        cases_by_biz[biz_id].append(c)

    probe_cases = []
    for biz_id, b_cases in sorted(cases_by_biz.items()):
        steps = []
        for i, c in enumerate(b_cases, start=1):
            cmd_label = c.gold["command"].label
            expected_kind = clothing_label_to_kind(cmd_label) if cmd_label != "none" else None
            steps.append({
                "id": f"{c.id}-step1",
                "language": c.provenance.get("language", "ne"),
                "text": c.state.get("customer_message", ""),
                "expected": expected_kind,
                "note": f"family:{c.provenance.get('family', '')}",
            })
        probe_cases.append({
            "id": f"bench-case-{biz_id}",
            "category": "clothing",
            "description": f"Customer dialog steps for {businesses[biz_id]['name']}",
            "menu_id": biz_id,
            "steps": steps,
        })

    return {
        "revision": "cl-bench-v1",
        "source": "cl-decisions-v1 held-out test split (10%)",
        "businesses": businesses,
        "cases": probe_cases,
    }


def write_clothing_export(
    cases: Sequence[Case],
    export_dir: Path = DEFAULT_EXPORT_DIR,
    benchmark_path: Path = DEFAULT_BENCHMARK_PATH,
    *,
    reviewer: str = "DontHash",
    seed: int = DEFAULT_SEED,
) -> ClothingExportReport:
    """Write train, calibration, test splits, manifest, and benchmark corpus."""
    # Attribute review metadata
    for c in cases:
        c.provenance["reviewed_by"] = reviewer
        c.provenance["review_mode"] = "human:bank-import"
        c.provenance["license"] = "CC-BY-4.0"
        validate_case(c)

    splits = stratify_cases(cases, seed=seed)
    leakage = check_leakage(splits)
    if leakage:
        raise ValueError(f"Leakage check failed: {leakage}")

    export_dir.mkdir(parents=True, exist_ok=True)
    benchmark_path.parent.mkdir(parents=True, exist_ok=True)

    for name in ("train", "calibration", "test"):
        out_path = export_dir / f"{CLOTHING_DATASET_REVISION}-{name}.jsonl"
        with out_path.open("w", encoding="utf-8") as sink:
            for case in splits[name]:
                sink.write(json.dumps(case.to_row(), ensure_ascii=False) + "\n")

    # Manifest
    def _count_field(subset: Sequence[Case], field: str) -> dict[str, int]:
        c: dict[str, int] = defaultdict(int)
        for case in subset:
            c[str(case.provenance.get(field, "unknown"))] += 1
        return dict(c)

    manifest = {
        "revision": CLOTHING_DATASET_REVISION,
        "domain": "clothing",
        "total_cases": len(cases),
        "total_decisions": len(cases) * 5,
        "splits": {name: len(split) for name, split in splits.items()},
        "languages": {name: _count_field(split, "language") for name, split in splits.items()},
        "families": {name: _count_field(split, "family") for name, split in splits.items()},
        "reviewed_by": reviewer,
        "license": "CC-BY-4.0",
    }
    manifest_path = export_dir / f"{CLOTHING_DATASET_REVISION}.manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Benchmark Corpus
    bench_corpus = build_benchmark_corpus(splits["test"])
    benchmark_path.write_text(json.dumps(bench_corpus, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return ClothingExportReport(
        total=len(cases),
        train=len(splits["train"]),
        calibration=len(splits["calibration"]),
        test=len(splits["test"]),
        manifest_path=manifest_path,
        benchmark_path=benchmark_path,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export clothing dataset splits and benchmark.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_EXPORT_DIR)
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK_PATH)
    parser.add_argument("--reviewer", default="DontHash")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args(argv)

    if not args.source.exists():
        print(f"source file not found: {args.source}")
        return 1

    cases = []
    for line in args.source.read_text(encoding="utf-8").splitlines():
        if line.strip():
            cases.append(Case.from_row(json.loads(line)))

    report = write_clothing_export(
        cases,
        export_dir=args.out,
        benchmark_path=args.benchmark,
        reviewer=args.reviewer,
        seed=args.seed,
    )
    print(report.summary())
    print(f"wrote manifest:  {report.manifest_path}")
    print(f"wrote benchmark: {report.benchmark_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
