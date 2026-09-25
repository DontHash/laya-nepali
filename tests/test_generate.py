"""Generation pipeline: plan, prompts, derived gold, validation and the client."""

from __future__ import annotations

import json
import os
import random
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from layanep.generate import (
    GeminiGenerator,
    GenerationError,
    generate_candidates,
    load_env_file,
    normalize_message,
    validate_message,
)
from layanep.schema import Case, validate_case
from layanep.templates import FAMILIES, LANGUAGES, TRAINING_BUSINESSES, build_case, build_plan, derive_gold


class FakeGenerator:
    def __init__(self, messages: list) -> None:
        self._messages = list(messages)
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        value = self._messages.pop(0) if self._messages else "ok"
        if isinstance(value, Exception):
            raise value
        return value


def task_for(family_id: str, language: str):
    plan = build_plan()
    return next(task for task in plan if task.family.id == family_id and task.language == language)


def test_plan_is_deterministic_and_covers_families() -> None:
    plan = build_plan(businesses=TRAINING_BUSINESSES[:1])
    again = build_plan(businesses=TRAINING_BUSINESSES[:1])
    assert [task.id for task in plan] == [task.id for task in again]
    assert len({task.id for task in plan}) == len(plan)
    assert {task.family.id for task in plan} == {family.id for family in FAMILIES}
    assert {task.language for task in plan} == set(LANGUAGES)
    assert len(plan) == len(FAMILIES) * len(LANGUAGES)


def test_plan_limit_takes_a_prefix() -> None:
    full = build_plan()
    limited = build_plan(limit=5)
    assert len(limited) == 5
    assert [task.id for task in limited] == [task.id for task in full[:5]]


def test_prompt_carries_business_menu_and_intent() -> None:
    task = build_plan(limit=1)[0]
    assert task.business.name in task.prompt
    assert task.business.menu[0].name in task.prompt
    assert task.family.instruction in task.prompt
    assert "Return only the message text" in task.prompt


def test_prompt_item_rule_is_conditional() -> None:
    plan = build_plan()
    greet = next(task for task in plan if task.family.id == "greet")
    price = next(task for task in plan if task.family.id == "query_price")
    assert "Name one specific item" not in greet.prompt
    assert "Name one specific item" in price.prompt
    assert "Express exactly one intent" in greet.prompt


def test_gold_is_valid_for_every_family() -> None:
    rng = random.Random(7)
    for family in FAMILIES:
        task = build_plan(families=[family], languages=["en"], variants=1, limit=1)[0]
        case = build_case(task, "how much is the momo?", rng, generator="test@unit")
        validate_case(case)
        assert case.gold["command"].label == family.command
        assert case.gold["query_field"].label == family.query_field
        assert case.gold["order_intent"].label == ("true" if family.order_intent else "false")
        assert case.gold["needs_staff"].label == ("true" if family.needs_staff else "false")
        assert case.gold["abstain"].label == ("true" if family.abstain else "false")
        assert abs(sum(case.gold["command"].probabilities.values()) - 1.0) <= 1e-3


def test_boolean_noul_keeps_the_intended_direction() -> None:
    rng = random.Random(3)
    for family in FAMILIES:
        gold = derive_gold(family, rng)
        assert (gold["order_intent"].probabilities["true"] > 0.5) == family.order_intent
        assert (gold["needs_staff"].probabilities["true"] > 0.5) == family.needs_staff
        assert (gold["abstain"].probabilities["true"] > 0.5) == family.abstain


def test_generate_candidates_writes_schema_valid_rows(tmp_path: Path) -> None:
    selected = [task_for("greet", language) for language in LANGUAGES]
    messages = ["नमस्ते", "namaste", "hello"]
    generator = FakeGenerator(messages)
    out = tmp_path / "candidates.jsonl"

    report = generate_candidates(selected, generator, generator_name="fake@unit", out_path=out)

    assert report.accepted == 3
    assert report.rejected == []
    assert report.failed == []
    assert generator.prompts == [task.prompt for task in selected]
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 3
    for row in rows:
        case = Case.from_row(row)
        validate_case(case)
        assert case.provenance["generator"] == "fake@unit"
        assert case.provenance["license"] == "CC-BY-4.0"


def test_rejects_pii_and_wrong_script(tmp_path: Path) -> None:
    tasks = [task_for("greet", "ne"), task_for("greet", "ne-rom")]
    generator = FakeGenerator(["call me at 9812345678", "नमस्ते"])
    report = generate_candidates(tasks, generator, generator_name="fake@unit", out_path=tmp_path / "x.jsonl")

    assert report.accepted == 0
    reasons = dict(report.rejected)
    assert any("pii" in reason for reason in reasons[tasks[0].id])
    assert any("Latin script" in reason for reason in reasons[tasks[1].id])


def test_failed_calls_are_recorded_not_raised(tmp_path: Path) -> None:
    task = task_for("greet", "ne")
    generator = FakeGenerator([GenerationError("quota exhausted")])
    report = generate_candidates([task], generator, generator_name="fake@unit", out_path=tmp_path / "x.jsonl")
    assert report.accepted == 0
    assert report.failed == [(task.id, "quota exhausted")]


def test_normalize_message_strips_noise() -> None:
    assert normalize_message('  "hello   there"  ') == "hello there"
    assert normalize_message("\u201cनमस्ते\u201d") == "नमस्ते"
    assert normalize_message("a\nb") == "a b"


def test_validate_message_language_rules() -> None:
    assert validate_message("नमस्ते", "ne") == []
    assert validate_message("hello", "ne") == ["expected Devanagari script"]
    assert "expected Latin script" in validate_message("नमस्ते", "ne-rom")
    assert "empty" in validate_message("", "en")


def test_validate_message_rejects_mixed_script_and_business_names() -> None:
    assert "mixed-script token" in validate_message("हts त, पछि भेटौला", "ne")
    reasons = validate_message("namaste Thamel, chicken momo cha?", "ne-rom", "Thamel Thali House")
    assert "mentions the restaurant name" in reasons


def test_load_env_file_sets_without_overriding(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / ".env"
    path.write_text('# comment\nGEMINI_API_KEY=abc\nQUOTED="x y"\n', encoding="utf-8")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    values = load_env_file(path)
    assert values["GEMINI_API_KEY"] == "abc"
    assert os.environ["GEMINI_API_KEY"] == "abc"

    monkeypatch.setenv("GEMINI_API_KEY", "keep")
    load_env_file(path)
    assert os.environ["GEMINI_API_KEY"] == "keep"


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args) -> bool:
        return False


def test_gemini_rotates_keys_on_retryable_errors(monkeypatch) -> None:
    calls: list[str] = []

    def fake_urlopen(request, timeout=0):
        calls.append(request.full_url)
        if len(calls) == 1:
            raise urllib.error.HTTPError(request.full_url, 429, "rate limited", None, None)
        return FakeResponse({"candidates": [{"content": {"parts": [{"text": "नमस्ते"}]}}]})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    generator = GeminiGenerator(["key1", "key2"], backoff_seconds=0)
    assert generator.generate("hi") == "नमस्ते"
    assert "key=key1" in calls[0]
    assert "key=key2" in calls[1]


def test_gemini_raises_on_client_errors(monkeypatch) -> None:
    def fail(request, timeout=0):
        raise urllib.error.HTTPError(request.full_url, 400, "bad request", None, None)

    monkeypatch.setattr(urllib.request, "urlopen", fail)
    with pytest.raises(GenerationError, match="HTTP 400"):
        GeminiGenerator(["key1"], backoff_seconds=0).generate("hi")


def test_gemini_extraction_guards() -> None:
    with pytest.raises(GenerationError, match="no Gemini API keys"):
        GeminiGenerator([])
    with pytest.raises(GenerationError, match="blocked"):
        GeminiGenerator._extract_text({"promptFeedback": {"blockReason": "SAFETY"}})
    with pytest.raises(GenerationError, match="no candidates"):
        GeminiGenerator._extract_text({})
    with pytest.raises(GenerationError, match="empty"):
        GeminiGenerator._extract_text({"candidates": [{"content": {"parts": [{"text": " "}]}}]})
