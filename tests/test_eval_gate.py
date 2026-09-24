"""Deterministic eval gate behaviour."""

from __future__ import annotations

import json
from pathlib import Path

from layanep.eval import FIXTURE_DIR, main, run_gate

FIXTURE = FIXTURE_DIR / "ne_case_golden.json"


def test_gate_passes_on_fixtures() -> None:
    result = run_gate([FIXTURE])
    assert result.passed, result.failures
    assert result.cases == 1
    assert result.decisions == 5


def test_gate_fails_on_invalid_data(tmp_path: Path) -> None:
    rows = json.loads(FIXTURE.read_text(encoding="utf-8"))
    rows[0]["gold"]["command"]["probabilities"]["none"] = 0.9
    bad = tmp_path / "bad.jsonl"
    bad.write_text(json.dumps(rows[0], ensure_ascii=False) + "\n", encoding="utf-8")
    result = run_gate([bad])
    assert not result.passed
    assert any("sum to 1.0" in failure for failure in result.failures)


def test_gate_fails_on_pii(tmp_path: Path) -> None:
    rows = json.loads(FIXTURE.read_text(encoding="utf-8"))
    rows[0]["state"]["customer_message"] = "call me at 9812345678"
    bad = tmp_path / "pii.jsonl"
    bad.write_text(json.dumps(rows[0], ensure_ascii=False) + "\n", encoding="utf-8")
    result = run_gate([bad])
    assert not result.passed
    assert any("PII pattern hit" in failure for failure in result.failures)


def test_gate_cli_exit_codes(capsys) -> None:
    assert main(["--check", "--data", str(FIXTURE)]) == 0
    assert "PASS" in capsys.readouterr().out


def test_gate_finds_nested_export_rows(tmp_path: Path) -> None:
    nested = tmp_path / "batch"
    nested.mkdir()
    row = json.loads(FIXTURE.read_text(encoding="utf-8"))[0]
    (nested / "rows.json").write_text(json.dumps([row], ensure_ascii=False), encoding="utf-8")
    result = run_gate([tmp_path])
    assert result.passed, result.failures
    assert result.cases == 1


def test_gate_fails_on_empty_directory(tmp_path: Path) -> None:
    result = run_gate([tmp_path])
    assert not result.passed
    assert any("no cases found" in failure for failure in result.failures)


def test_gate_fails_on_missing_path(tmp_path: Path) -> None:
    result = run_gate([tmp_path / "missing.jsonl"])
    assert not result.passed
    assert any("no dataset at" in failure for failure in result.failures)


def test_export_directory_requires_reviewed_by(tmp_path: Path, monkeypatch) -> None:
    import layanep.eval as eval_module

    monkeypatch.setattr(eval_module, "DEFAULT_DATA_DIR", tmp_path)
    row = json.loads(FIXTURE.read_text(encoding="utf-8"))[0]
    row["provenance"]["reviewed_by"] = None
    (tmp_path / "rows.jsonl").write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    result = eval_module.run_gate(None)
    assert not result.passed
    assert any("reviewed_by" in failure for failure in result.failures)
