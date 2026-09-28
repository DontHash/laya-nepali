"""Clothing templates: businesses, families, plan, case, gold and prompt tests."""

from __future__ import annotations

import random

from layanep.clothing_questions import CLOTHING_COMMAND_CRITERIA
from layanep.clothing_templates import (
    FAMILIES,
    FAMILY_BY_ID,
    GENERATOR_WORKFLOW,
    TRAINING_BUSINESSES,
    Product,
    build_case,
    build_plan,
    build_prompt,
    derive_gold,
)
from layanep.schema import ABSTAIN_KEY, validate_case


def test_training_businesses_has_eight_entries() -> None:
    assert len(TRAINING_BUSINESSES) == 8


def test_every_business_has_nonempty_catalog() -> None:
    for business in TRAINING_BUSINESSES:
        assert len(business.catalog) > 0, f"{business.id} has an empty catalog"


def test_families_has_28_entries() -> None:
    assert len(FAMILIES) == 28


def test_family_by_id_matches_families_count() -> None:
    assert len(FAMILY_BY_ID) == len(FAMILIES)


def test_build_plan_with_budget_produces_tasks() -> None:
    plan = build_plan(kind_cases=2, safety_cases=1)
    assert len(plan) > 0


def test_build_case_produces_valid_case() -> None:
    rng = random.Random(42)
    task = build_plan(kind_cases=1, safety_cases=1, limit=1)[0]
    case = build_case(task, "कति पर्छ?", rng, generator="test@unit")
    validate_case(case)


def test_derive_gold_probabilities_sum_to_one() -> None:
    rng = random.Random(7)
    for family in FAMILIES:
        gold = derive_gold(family, rng)
        for question_id, entry in gold.items():
            total = sum(entry.probabilities.values())
            assert abs(total - 1.0) <= 1e-3, (
                f"family={family.id} question={question_id} sum={total}"
            )


def test_build_prompt_contains_business_name_and_intent() -> None:
    business = TRAINING_BUSINESSES[0]
    family = FAMILIES[0]
    prompt = build_prompt(business, family, "ne")
    assert business.name in prompt
    assert family.instruction in prompt


def test_product_to_state_includes_sizes_and_colors() -> None:
    product = Product(
        "Test Kurta", 1500,
        sizes=("S", "M", "L"),
        colors=("red", "blue"),
        material="cotton",
    )
    state = product.to_state()
    assert state["sizes"] == ["S", "M", "L"]
    assert state["colors"] == ["red", "blue"]


def test_clothing_business_state_base_includes_cod() -> None:
    business = TRAINING_BUSINESSES[0]
    state = business.state_base()
    assert "cod_available" in state["business"]


def test_generator_workflow_value() -> None:
    assert GENERATOR_WORKFLOW == "clothing_command_lu"


def test_every_family_command_is_valid_criteria_or_abstain() -> None:
    valid_keys = set(CLOTHING_COMMAND_CRITERIA) | {ABSTAIN_KEY}
    for family in FAMILIES:
        assert family.command in valid_keys, (
            f"family {family.id} has unknown command '{family.command}'"
        )
