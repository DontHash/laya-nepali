"""Schema pin: golden fixture, round-trip, and rejection cases."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from layanep.questions import (
    COMMAND_CRITERIA,
    COMMAND_LABEL_TO_KIND,
    NE_QUESTION_IDS,
    assert_full_vocabulary,
    ne_questions,
)
from layanep.schema import (
    ABSTAIN_KEY,
    LU_COMMAND_KINDS,
    MAX_CHOICE_OPTIONS,
    Case,
    Question,
    SchemaError,
    validate_case,
    validate_question,
)

FIXTURE = Path(__file__).parent / "fixtures" / "ne_case_golden.json"


def load_fixture() -> list[dict]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def golden_case() -> Case:
    return Case.from_row(load_fixture()[0])


def test_golden_case_valid() -> None:
    case = golden_case()
    validate_case(case)
    assert set(case.questions) == set(NE_QUESTION_IDS)
    assert len(case.questions) == 5


def test_question_template_matches_fixture_shape() -> None:
    template = ne_questions("Sherpa Kitchen")
    assert set(template) == set(NE_QUESTION_IDS)
    for question in template.values():
        validate_question("template", question)
    assert_full_vocabulary()


def test_command_vocabulary_is_shared_and_maps_to_kinds() -> None:
    assert set(COMMAND_CRITERIA) == set(COMMAND_LABEL_TO_KIND) | {ABSTAIN_KEY}
    assert set(COMMAND_LABEL_TO_KIND.values()) == set(LU_COMMAND_KINDS)
    assert len(COMMAND_CRITERIA) <= MAX_CHOICE_OPTIONS


def test_fixture_uses_shared_command_criteria() -> None:
    case = golden_case()
    assert case.questions["command"].criteria == COMMAND_CRITERIA
    assert case.gold["command"].label in COMMAND_LABEL_TO_KIND


def test_row_round_trip() -> None:
    case = golden_case()
    row = case.to_row()
    for column in ("state", "questions", "gold"):
        assert isinstance(row[column], str)
    assert Case.from_row(row).to_dict() == case.to_dict()


def test_probability_sum_rejected() -> None:
    case = golden_case()
    case.gold["command"].probabilities["none"] = 0.5
    with pytest.raises(SchemaError, match="sum to 1.0"):
        validate_case(case)


def test_unknown_label_rejected() -> None:
    case = golden_case()
    case.gold["command"].label = "ordering.add_item"
    with pytest.raises(SchemaError, match="not one of the choice options"):
        validate_case(case)


def test_probability_key_outside_options_rejected() -> None:
    case = golden_case()
    case.gold["query_field"].probabilities["delivery"] = 0.0
    with pytest.raises(SchemaError, match="outside the option set"):
        validate_case(case)


def test_gold_key_mismatch_rejected() -> None:
    case = golden_case()
    del case.gold["abstain"]
    with pytest.raises(SchemaError, match="gold keys must match question keys"):
        validate_case(case)


def test_too_many_choice_options_rejected() -> None:
    question = Question(
        type="choice",
        instructions="pick one",
        criteria={f"k{i}": f"option {i}" for i in range(21)},
    )
    with pytest.raises(SchemaError, match="exceed the Laya limit"):
        validate_question("command", question)


def test_noul_with_criteria_rejected() -> None:
    question = Question(type="noul", instructions="yes or no?", criteria={"true": "yes"})
    with pytest.raises(SchemaError, match="must not carry criteria"):
        validate_question("order_intent", question)


def test_missing_probabilities_rejected() -> None:
    case = golden_case()
    case.gold["needs_staff"].probabilities = {}
    with pytest.raises(SchemaError, match="probabilities must be a non-empty map"):
        validate_case(case)
