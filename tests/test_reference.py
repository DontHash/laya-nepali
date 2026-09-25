"""Register profiling from reference sources."""

from __future__ import annotations

import json
from pathlib import Path

from layanep.reference import (
    REGISTER_RULES,
    load_source,
    main,
    messages_from_rows,
    profile_texts,
    render_register_markdown,
)

FIXTURE = Path(__file__).parent / "fixtures" / "ne_case_golden.json"


def test_profile_texts_counts() -> None:
    profile = profile_texts(["नमस्ते हजुर", "hello there", "मोमोको मूल्य कति हो?"], label="t")
    assert profile.messages == 3
    assert profile.words == 8
    assert profile.latin_token_share == 0.25
    assert profile.particles_per_100_words == 12.5
    assert profile.question_share == 0.333
    assert profile.devanagari_messages == 2
    assert profile.words_p50 == 2.0
    assert profile.words_p90 == 4.0


def test_profile_ignores_blank_texts() -> None:
    profile = profile_texts(["", "   ", "नमस्ते"], label="t")
    assert profile.messages == 1


def test_messages_from_rows_handles_objects_and_strings() -> None:
    rows = [
        {"state": {"customer_message": "नमस्ते"}},
        {"state": '{"customer_message": "बाई"}'},
        {"state": {}},
        {"state": "not json"},
    ]
    assert messages_from_rows(rows) == ["नमस्ते", "बाई"]


def test_load_source_jsonl_and_directory(tmp_path: Path) -> None:
    row = json.loads(FIXTURE.read_text(encoding="utf-8"))[0]
    jsonl = tmp_path / "rows.jsonl"
    jsonl.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    label, texts = load_source(f"ours={jsonl}")
    assert label == "ours"
    assert texts == ["मोमोको मूल्य कति हो?"]

    transcripts = tmp_path / "transcripts"
    transcripts.mkdir()
    (transcripts / "a.txt").write_text("नमस्ते हजुर\nhello there\n", encoding="utf-8")
    label, texts = load_source(str(transcripts))
    assert label == "transcripts"
    assert texts == ["नमस्ते हजुर", "hello there"]


def test_render_contains_rules_and_labels() -> None:
    profile = profile_texts(["नमस्ते"], label="ours")
    markdown = render_register_markdown([profile])
    assert "# Nepali register profile" in markdown
    assert "| ours |" in markdown
    assert REGISTER_RULES[0] in markdown
    assert "reference-only" in markdown


def test_cli_writes_markdown(tmp_path: Path) -> None:
    row = json.loads(FIXTURE.read_text(encoding="utf-8"))[0]
    jsonl = tmp_path / "rows.jsonl"
    jsonl.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    out = tmp_path / "register.md"

    assert main(["--source", f"ours={jsonl}", "--out", str(out)]) == 0
    assert "Nepali register profile" in out.read_text(encoding="utf-8")
