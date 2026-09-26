"""Tests for the external message-bank importer."""

from __future__ import annotations

import json
from pathlib import Path

from layanep.import_bank import import_entries, load_corpus_messages, main
from layanep.schema import Case, validate_case


def entry(message: str, family: str) -> dict:
    return {"message": message, "family": family}


def test_import_derives_cases_and_skips_bad_rows() -> None:
    entries = [
        entry("नमस्ते दाइ", "greet"),
        entry("नमस्ते दाइ", "greet"),
        entry("मःम कति पर्छ?", "query_price"),
        entry("hello", "greet"),
        entry("बदाम " * 16, "allergy"),
        entry("नमस्ते", "not_a_family"),
        entry("नमस्ते", "greet"),
    ]
    rows, report = import_entries(entries, forbidden={"नमस्ते"}, existing=set())
    assert report.total == 7
    assert report.imported == 2
    assert report.skipped["duplicate"] == 1
    assert report.skipped["benchmark collision"] == 1
    assert report.skipped["invalid entry"] == 1
    assert report.skipped["invalid message"] == 2
    assert [row["id"] for row in rows] == ["ne-bank-0001", "ne-bank-0002"]
    for row in rows:
        case = Case.from_row(row)
        validate_case(case)
        assert case.provenance["generator"] == "external-llm:bank"
        assert case.provenance["license"] == "CC-BY-4.0"
    gold = json.loads(rows[1]["gold"])
    assert gold["command"]["label"] == "price"
    assert gold["query_field"]["label"] == "price"


def test_import_respects_existing_corpus(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus.jsonl"
    state = json.dumps({"customer_message": "नमस्ते दाइ"})
    corpus.write_text(json.dumps({"state": state}) + "\n", encoding="utf-8")
    existing = load_corpus_messages((corpus,))
    assert "नमस्ते दाइ" in existing

    rows, report = import_entries([entry("नमस्ते दाइ", "greet")], existing=existing)
    assert rows == []
    assert report.skipped["duplicate"] == 1


def test_cli_imports_a_bank_file(tmp_path: Path) -> None:
    bank = tmp_path / "bank.jsonl"
    bank.write_text(
        "// part 1\n"
        + json.dumps(entry("नमस्कार साथी", "greet"), ensure_ascii=False)
        + "\n"
        + json.dumps(entry("मःम छ त?", "query_availability"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    corpus = tmp_path / "corpus.jsonl"
    corpus.write_text("", encoding="utf-8")
    benchmark = tmp_path / "benchmark.json"
    benchmark.write_text(
        json.dumps({"revision": "test", "source": "test", "businesses": {}, "cases": []}), encoding="utf-8"
    )
    out = tmp_path / "out.jsonl"

    rc = main(
        [
            "--input",
            str(bank),
            "--out",
            str(out),
            "--id-prefix",
            "ne-cli",
            "--corpus",
            str(corpus),
            "--benchmark",
            str(benchmark),
        ]
    )
    assert rc == 0
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert [row["id"] for row in rows] == ["ne-cli-0001", "ne-cli-0002"]
    assert {row["provenance"]["family"] for row in rows} == {"greet", "query_availability"}
