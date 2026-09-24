"""Provenance lanes, full-case PII scan, duplicates, and nested loading."""

from __future__ import annotations

import json
from pathlib import Path

from layanep.schema import Case
from layanep.validate import load_rows, validate_dataset

FIXTURE = Path(__file__).parent / "fixtures" / "ne_case_golden.json"


def golden_case() -> Case:
    return Case.from_row(json.loads(FIXTURE.read_text(encoding="utf-8"))[0])


def test_golden_fixture_passes_dataset_validation() -> None:
    assert validate_dataset([golden_case()]) == []


def test_missing_provenance_fails() -> None:
    case = golden_case()
    case.provenance = {}
    failures = validate_dataset([case])
    assert any("provenance is required" in failure for failure in failures)


def test_blocked_source_fails() -> None:
    case = golden_case()
    case.provenance["source"] = "OpenSLR54 transcripts"
    assert any("blocked lane" in failure for failure in validate_dataset([case]))


def test_pending_source_fails() -> None:
    case = golden_case()
    case.provenance["source"] = "kshitizgajurel/customer-care"
    assert any("pending license verification" in failure for failure in validate_dataset([case]))


def test_disallowed_license_fails() -> None:
    case = golden_case()
    case.provenance["license"] = "CC-BY-SA-4.0"
    assert any("not an allowed lane" in failure for failure in validate_dataset([case]))


def test_export_requires_reviewed_by() -> None:
    case = golden_case()
    case.provenance["reviewed_by"] = None
    failures = validate_dataset([case], require_reviewed=True)
    assert any("reviewed_by" in failure for failure in failures)

    case.provenance["reviewed_by"] = "praka"
    assert validate_dataset([case], require_reviewed=True) == []


def test_pii_in_criteria_and_id_is_scanned() -> None:
    case = golden_case()
    case.questions["command"].criteria["social.greet"] = "contact me at a@b.com"
    assert any("criteria command:email" in failure for failure in validate_dataset([case]))

    case = golden_case()
    case.id = "9812345678"
    assert any("id:phone_np" in failure for failure in validate_dataset([case]))


def test_duplicate_ids_fail() -> None:
    cases = [golden_case(), golden_case()]
    assert any("duplicate case ids" in failure for failure in validate_dataset(cases))


def test_load_rows_finds_nested_files(tmp_path: Path) -> None:
    nested = tmp_path / "batch-01"
    nested.mkdir()
    row = json.loads(FIXTURE.read_text(encoding="utf-8"))[0]
    (nested / "rows.jsonl").write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    assert len(load_rows(tmp_path)) == 1
