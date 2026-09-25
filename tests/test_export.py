"""Export splits, manifest, and the benchmark leakage gate."""

from __future__ import annotations

import json
from pathlib import Path

from layanep.export import (
    benchmark_texts,
    leakage_failures,
    main,
    split_for,
    write_export,
)
from layanep.schema import Case
from layanep.validate import load_cases

REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEWED = REPO_ROOT / "data" / "reviewed" / "ne-decisions-v1.jsonl"


def test_split_for_is_deterministic() -> None:
    assert split_for("ne-gen-0001", 0.1) == split_for("ne-gen-0001", 0.1)
    ids = [f"ne-gen-{index:04d}" for index in range(2000)]
    calibration = [case_id for case_id in ids if split_for(case_id, 0.1) == "calibration"]
    assert 150 <= len(calibration) <= 250


def test_write_export_writes_splits_and_manifest(tmp_path: Path) -> None:
    cases = load_cases(REVIEWED)
    report = write_export(cases, tmp_path, reviewed_from=REVIEWED)
    assert report.train + report.calibration == len(cases)

    rows = []
    for name in ("train", "calibration"):
        path = tmp_path / f"ne-decisions-v1-{name}.jsonl"
        assert path.exists()
        rows.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines())
    assert len(rows) == len(cases)

    manifest = json.loads(report.manifest.read_text(encoding="utf-8"))
    assert manifest["splits"]["train"] == report.train
    assert manifest["review_modes"].get("human") == len(cases)
    assert manifest["sources"]["synthetic"] == len(cases)


def test_leakage_flags_benchmark_messages() -> None:
    cases = load_cases(REVIEWED)
    texts = benchmark_texts()
    assert texts
    assert leakage_failures(cases, texts) == []

    leaked = Case.from_row(cases[0].to_row())
    leaked.state["customer_message"] = "नमस्ते हजुर"
    failures = leakage_failures([leaked], texts)
    assert any("benchmark" in failure for failure in failures)


def test_cli_export_and_gate(tmp_path: Path, capsys) -> None:
    assert main(["--reviewed", str(REVIEWED), "--out", str(tmp_path)]) == 0
    assert "train" in capsys.readouterr().out
    assert (tmp_path / "ne-decisions-v1.manifest.json").exists()


def test_cli_fails_without_reviewed(tmp_path: Path, capsys) -> None:
    assert main(["--reviewed", str(tmp_path / "missing.jsonl"), "--out", str(tmp_path / "out")]) == 1
    assert "no reviewed dataset" in capsys.readouterr().out
