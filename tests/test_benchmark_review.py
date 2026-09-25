"""Benchmark step review: sheet, decisions, apply/freeze, and the CLI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from layanep.benchmark.corpus import load_corpus, validate_corpus
from layanep.benchmark.review import (
    apply_sheet,
    build_sheet,
    format_record,
    load_sheet,
    main,
    run_review,
    save_sheet,
    set_decision,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
V2_CORPUS = REPO_ROOT / "data" / "benchmark" / "ne-bench-deva-v2.json"

TINY_CORPUS = {
    "revision": "ne-bench-deva-v2",
    "source": "test fixture",
    "businesses": {"t": {"id": "t", "name": "Test Kitchen", "menu": []}},
    "cases": [
        {
            "id": "t-social",
            "category": "social",
            "description": "fixture",
            "menuId": "t",
            "steps": [
                {"id": "t-greet", "language": "ne", "text": "नमस्ते", "expected": "social.greet"},
                {"id": "t-goodbye", "language": "ne", "text": "बाई", "expected": "social.goodbye"},
                {"id": "t-yesno", "language": "ne", "text": "हुन्छ", "expected": None},
            ],
        }
    ],
}


def write_tiny(tmp_path: Path) -> Path:
    path = tmp_path / "tiny.json"
    path.write_text(json.dumps(TINY_CORPUS, ensure_ascii=False), encoding="utf-8")
    return path


def test_build_sheet_and_decisions(tmp_path: Path) -> None:
    corpus = write_tiny(tmp_path)
    sheet = tmp_path / "sheet.jsonl"
    records = build_sheet(corpus, sheet)
    assert [record.step_id for record in records] == ["t-greet", "t-goodbye", "t-yesno"]
    assert all(record.status == "pending" for record in records)

    set_decision(records[0], "accept", reviewer="tester")
    set_decision(records[1], "edit", reviewer="tester", text="  बाई   बाई ")
    set_decision(records[2], "reject", reviewer="tester", note="noise")

    assert records[0].status == "accepted"
    assert records[1].status == "edited"
    assert records[1].text == "बाई बाई"
    assert records[2].status == "rejected"

    save_sheet(sheet, records)
    reloaded = load_sheet(sheet)
    assert [record.status for record in reloaded] == ["accepted", "edited", "rejected"]


def test_relabel_changes_expected(tmp_path: Path) -> None:
    corpus = write_tiny(tmp_path)
    records = build_sheet(corpus, tmp_path / "sheet.jsonl")
    set_decision(records[2], "relabel", reviewer="tester", expected="social.thanks")
    assert records[2].expected == "social.thanks"
    assert records[2].status == "edited"

    set_decision(records[1], "relabel", reviewer="tester", expected="none")
    assert records[1].expected is None

    with pytest.raises(ValueError, match="kind"):
        set_decision(records[0], "relabel", reviewer="tester", expected="not.a.kind")


def test_apply_requires_full_review(tmp_path: Path) -> None:
    corpus = write_tiny(tmp_path)
    records = build_sheet(corpus, tmp_path / "sheet.jsonl")
    set_decision(records[0], "accept", reviewer="tester")
    with pytest.raises(ValueError, match="pending"):
        apply_sheet(corpus, records)


def test_apply_freezes_the_v2_corpus(tmp_path: Path) -> None:
    corpus = tmp_path / "v2.json"
    corpus.write_text(V2_CORPUS.read_text(encoding="utf-8"), encoding="utf-8")
    records = build_sheet(corpus, tmp_path / "sheet.jsonl")
    assert len(records) == 272

    overrides = {
        "bb-menu-1": lambda record: set_decision(record, "edit", reviewer="tester", text="मेनु पठाइदिनु है"),
        "bb-unclear-4": lambda record: set_decision(record, "relabel", reviewer="tester", expected="discovery.query"),
        "pb-unclear-4": lambda record: set_decision(record, "reject", reviewer="tester", note="ambiguous"),
    }
    for record in records:
        override = overrides.get(record.step_id)
        if override:
            override(record)
        else:
            set_decision(record, "accept", reviewer="tester")

    message = apply_sheet(corpus, records)
    assert "269 accepted" in message
    assert "2 edited" in message
    assert "1 rejected" in message

    frozen = json.loads(corpus.read_text(encoding="utf-8"))
    assert frozen["review"]["rejected"] == 1
    steps = {step["id"]: step for case in frozen["cases"] for step in case["steps"]}
    assert "pb-unclear-4" not in steps
    assert steps["bb-menu-1"]["text"] == "मेनु पठाइदिनु है"
    assert steps["bb-menu-1"]["reviewed"] is True
    assert steps["bb-unclear-4"]["expected"] == "discovery.query"

    reloaded = load_corpus(corpus)
    assert validate_corpus(reloaded) == []
    assert len(reloaded.steps) == 271


def test_run_review_interactive(tmp_path: Path, monkeypatch) -> None:
    corpus = write_tiny(tmp_path)
    sheet = tmp_path / "sheet.jsonl"
    records = build_sheet(corpus, sheet)

    answers = iter(["a", "l", "social.thanks", "r", "off topic"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    assert run_review(records, sheet, "tester", None) == 0

    persisted = {record.step_id: record for record in load_sheet(sheet)}
    assert persisted["t-greet"].status == "accepted"
    assert persisted["t-goodbye"].expected == "social.thanks"
    assert persisted["t-yesno"].status == "rejected"
    assert persisted["t-yesno"].note == "off topic"


def test_format_record_marks_changes(tmp_path: Path) -> None:
    corpus = write_tiny(tmp_path)
    records = build_sheet(corpus, tmp_path / "sheet.jsonl")
    set_decision(records[1], "relabel", reviewer="tester", expected="social.greet")
    rendered = format_record(records[1], index=1, total=3)
    assert "[1/3]" in rendered
    assert "expected: social.greet" in rendered
    assert "was:" in rendered


def test_cli_build_list_show_set(tmp_path: Path, capsys) -> None:
    corpus = write_tiny(tmp_path)
    sheet = tmp_path / "sheet.jsonl"

    assert main(["--corpus", str(corpus), "--sheet", str(sheet), "build"]) == 0
    assert "3 records (3 pending)" in capsys.readouterr().out

    assert main(["--corpus", str(corpus), "--sheet", str(sheet), "list"]) == 0
    assert "t-greet" in capsys.readouterr().out

    assert main(["--corpus", str(corpus), "--sheet", str(sheet), "show", "--id", "t-greet"]) == 0
    assert "expected: social.greet" in capsys.readouterr().out

    assert main(["--corpus", str(corpus), "--sheet", str(sheet), "set", "--id", "t-greet", "--action", "accept"]) == 0
    assert main(["--corpus", str(corpus), "--sheet", str(sheet), "set", "--id", "t-greet", "--action", "accept"]) == 1
