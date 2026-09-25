"""Review sheet: build, decisions, interactive loop, and apply."""

from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from layanep.review import (
    ReviewRecord,
    apply_sheet,
    build_sheet,
    filter_records,
    format_record,
    load_sheet,
    main,
    run_review,
    save_sheet,
    set_decision,
)
from layanep.schema import Case, validate_case
from layanep.templates import build_case, build_plan

MESSAGES = {"ne": "नमस्ते", "ne-rom": "dhanyabad", "en": "how much is the momo?"}


def task_for(family_id: str, language: str):
    plan = build_plan()
    return next(task for task in plan if task.family.id == family_id and task.language == language)


def make_candidates(tmp_path: Path) -> tuple[Path, list[str]]:
    tasks = [task_for("greet", "ne"), task_for("thanks", "ne-rom"), task_for("query_price", "en")]
    rng = random.Random(1)
    rows = [build_case(task, MESSAGES[task.language], rng, generator="fake@unit").to_row() for task in tasks]
    path = tmp_path / "candidates.jsonl"
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    return path, [row["id"] for row in rows]


def test_build_preserves_existing_decisions(tmp_path: Path) -> None:
    candidates, ids = make_candidates(tmp_path)
    sheet = tmp_path / "sheet.jsonl"
    records = build_sheet(candidates, sheet)
    assert [record.status for record in records] == ["pending"] * 3

    set_decision(records[0], "accept", reviewer="tester")
    save_sheet(sheet, records)

    rebuilt = build_sheet(candidates, sheet)
    assert rebuilt[0].status == "accepted"
    assert rebuilt[0].reviewed_by == "tester"
    assert [record.id for record in rebuilt] == ids


def test_set_decision_actions(tmp_path: Path) -> None:
    candidates, _ = make_candidates(tmp_path)
    records = build_sheet(candidates, tmp_path / "sheet.jsonl")

    set_decision(records[0], "accept", reviewer="tester", note="")
    assert records[0].status == "accepted"
    assert records[0].reviewed_at

    set_decision(records[1], "edit", reviewer="tester", text="  धेरै   धन्यवाद है ")
    assert records[1].status == "edited"
    assert records[1].text == "धेरै धन्यवाद है"

    set_decision(records[2], "reject", reviewer="tester", note="not a price question")
    assert records[2].status == "rejected"

    with pytest.raises(ValueError, match="already"):
        set_decision(records[0], "reject", reviewer="tester")
    with pytest.raises(ValueError, match="requires"):
        set_decision(ReviewRecord(id="x"), "edit", reviewer="tester", text="  ")


def test_apply_writes_only_reviewed_rows(tmp_path: Path) -> None:
    candidates, _ = make_candidates(tmp_path)
    sheet = tmp_path / "sheet.jsonl"
    records = build_sheet(candidates, sheet)
    set_decision(records[0], "accept", reviewer="tester")
    set_decision(records[1], "edit", reviewer="tester", text="धेरै धन्यवाद है")
    set_decision(records[2], "reject", reviewer="tester", note="bad")

    out = tmp_path / "applied.jsonl"
    report = apply_sheet(records, out)
    assert report.written == 2
    assert report.skipped_rejected == 1
    assert report.failures == []

    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 2
    edited = rows[1]
    assert edited["provenance"]["reviewed_by"] == "tester"
    assert edited["provenance"]["review"] == "edited"
    assert json.loads(edited["state"])["customer_message"] == "धेरै धन्यवाद है"
    for row in rows:
        validate_case(Case.from_row(row))


def test_apply_reports_unreviewed_rows(tmp_path: Path) -> None:
    candidates, _ = make_candidates(tmp_path)
    records = build_sheet(candidates, tmp_path / "sheet.jsonl")
    records[0].status = "accepted"
    records[0].reviewed_by = None

    report = apply_sheet(records, tmp_path / "applied.jsonl")
    assert report.written == 0
    assert report.failures and "reviewed_by" in report.failures[0][1][0]


def test_run_review_interactive(tmp_path: Path, monkeypatch) -> None:
    candidates, ids = make_candidates(tmp_path)
    sheet = tmp_path / "sheet.jsonl"
    records = build_sheet(candidates, sheet)

    answers = iter(["a", "e", "धेरै धन्यवाद", "r", "not natural"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    assert run_review(records, sheet, "tester", None) == 0

    persisted = {record.id: record for record in load_sheet(sheet)}
    assert persisted[ids[0]].status == "accepted"
    assert persisted[ids[1]].status == "edited"
    assert persisted[ids[1]].text == "धेरै धन्यवाद"
    assert persisted[ids[2]].status == "rejected"
    assert persisted[ids[2]].note == "not natural"


def test_filter_and_format(tmp_path: Path) -> None:
    candidates, ids = make_candidates(tmp_path)
    records = build_sheet(candidates, tmp_path / "sheet.jsonl")
    set_decision(records[0], "accept", reviewer="tester")

    assert [record.id for record in filter_records(records, status="pending")] == ids[1:]
    assert [record.id for record in filter_records(records, family="thanks")] == [ids[1]]
    assert [record.id for record in filter_records(records, language="en")] == [ids[2]]

    rendered = format_record(records[0], index=1, total=3)
    assert "[1/3]" in rendered
    assert "should express:" in rendered
    assert "command=greet" in rendered
    assert "fake@unit" in rendered


def test_cli_build_list_show_apply(tmp_path: Path, capsys) -> None:
    candidates, ids = make_candidates(tmp_path)
    sheet = tmp_path / "sheet.jsonl"

    assert main(["build", "--input", str(candidates), "--sheet", str(sheet)]) == 0
    assert "3 records (3 pending)" in capsys.readouterr().out

    assert main(["list", "--sheet", str(sheet)]) == 0
    assert ids[0] in capsys.readouterr().out

    assert main(["show", "--sheet", str(sheet), "--id", ids[0]]) == 0
    assert "expected:" in capsys.readouterr().out

    assert main(["set", "--sheet", str(sheet), "--id", ids[0], "--action", "accept", "--reviewer", "tester"]) == 0
    assert main(["set", "--sheet", str(sheet), "--id", ids[0], "--action", "accept"]) == 1

    out = tmp_path / "applied.jsonl"
    assert main(["apply", "--sheet", str(sheet), "--out", str(out)]) == 0
    assert "written 1" in capsys.readouterr().out
    assert out.exists()
