"""Clothing-domain question vocabulary: integrity, counts, and mapping tests."""

from __future__ import annotations

from layanep.clothing_questions import (
    CLOTHING_COMMAND_CRITERIA,
    CLOTHING_COMMAND_LABEL_TO_KIND,
    CLOTHING_LU_COMMAND_KINDS,
    CLOTHING_QUERY_FIELDS,
    NE_CLOTHING_QUESTION_IDS,
    assert_clothing_vocabulary,
    clothing_command_question,
    clothing_label_to_kind,
    clothing_questions,
)
from layanep.questions import COMMAND_CRITERIA
from layanep.schema import ABSTAIN_KEY, MAX_CHOICE_OPTIONS


def test_clothing_vocabulary_integrity() -> None:
    assert_clothing_vocabulary()


def test_clothing_command_criteria_has_19_entries() -> None:
    assert len(CLOTHING_COMMAND_CRITERIA) == 19


def test_clothing_questions_returns_five_questions_with_correct_ids() -> None:
    questions = clothing_questions("Test Store")
    assert set(questions) == set(NE_CLOTHING_QUESTION_IDS)
    assert len(questions) == 5


def test_clothing_command_question_is_choice_with_19_criteria() -> None:
    question = clothing_command_question("Test Store")
    assert question.type == "choice"
    assert len(question.criteria) == 19


def test_clothing_label_to_kind_maps_known_labels() -> None:
    assert clothing_label_to_kind("price") == "discovery.query"
    assert clothing_label_to_kind("checkout") == "ordering.request_checkout"
    assert clothing_label_to_kind("cod") == "fulfillment.ask_cod"


def test_clothing_label_to_kind_returns_none_for_none_and_unknown() -> None:
    assert clothing_label_to_kind("none") is None
    assert clothing_label_to_kind("unknown_label") is None


def test_clothing_query_fields_has_five_entries() -> None:
    assert len(CLOTHING_QUERY_FIELDS) == 5
    assert set(CLOTHING_QUERY_FIELDS) == {"price", "size", "color", "material", "stock"}


def test_all_lu_command_kinds_reachable() -> None:
    reachable = set(CLOTHING_COMMAND_LABEL_TO_KIND.values())
    assert set(CLOTHING_LU_COMMAND_KINDS) == reachable


def test_max_choice_options_not_exceeded() -> None:
    assert len(CLOTHING_COMMAND_CRITERIA) <= MAX_CHOICE_OPTIONS


def test_clothing_criteria_keys_overlap_excludes_domain_specific() -> None:
    shared = set(CLOTHING_COMMAND_CRITERIA) & set(COMMAND_CRITERIA)
    # Social intents are shared by design
    social = {"greet", "thanks", "goodbye", ABSTAIN_KEY}
    assert social <= shared
    # Domain-specific restaurant keys must not appear in clothing
    restaurant_only = {"menu", "availability", "details", "hours", "repeat_order"}
    assert shared & restaurant_only == set()
    # Domain-specific clothing keys must not appear in restaurant
    clothing_only = {"catalog", "size", "color", "material", "stock", "cod", "exchange", "custom_order"}
    assert shared & clothing_only == set()
