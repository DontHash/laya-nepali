"""Domain registry: discovery, contract surface, and lookup errors."""

from __future__ import annotations

import pytest

from layanep.domains import available_domains, get_domain

REQUIRED_SURFACE = (
    "DOMAIN_NAME",
    "WORKFLOW",
    "questions",
    "T0_READ_ONLY",
    "T1_MUTATIONS",
    "DEFAULT_CONFIDENCE_TAU",
    "DEFAULT_P_NONE_MAX",
    "classify_tier",
    "extract_signals",
    "RESPONSE_TEMPLATES",
    "fill_template",
    "escalation_message",
    "generator",
)

REQUIRED_GENERATOR_SURFACE = (
    "GENERATOR_WORKFLOW",
    "LANGUAGES",
    "LANGUAGE_INSTRUCTIONS",
    "FAMILIES",
    "FAMILY_BY_ID",
    "TRAINING_BUSINESSES",
    "SPEC",
    "build_prompt",
    "build_plan",
    "derive_gold",
    "build_case",
)


def test_available_domains_lists_installed_packages() -> None:
    names = available_domains()
    assert "restaurant" in names
    assert "clothing" in names
    assert names == sorted(names)


def test_every_domain_binds_the_full_surface() -> None:
    for name in available_domains():
        domain = get_domain(name)
        for attr in REQUIRED_SURFACE:
            assert hasattr(domain, attr), f"{name} is missing {attr}"
        for attr in REQUIRED_GENERATOR_SURFACE:
            assert hasattr(domain.generator, attr), f"{name}.generator is missing {attr}"
        assert domain.DOMAIN_NAME == name
        assert domain.WORKFLOW == domain.generator.GENERATOR_WORKFLOW
        assert set(domain.questions("Test Shop")) == {
            "command",
            "query_field",
            "order_intent",
            "needs_staff",
            "abstain",
        }
        assert domain.T0_READ_ONLY <= set(domain.RESPONSE_TEMPLATES)


def test_domains_share_one_generation_engine() -> None:
    from layanep.domains.clothing import generator as clothing
    from layanep.domains.restaurant import generator as restaurant
    from layanep.generation_core import GenerationFamily, GenerationTask

    assert restaurant.Family is GenerationFamily
    assert clothing.ClothingFamily is GenerationFamily
    assert restaurant.GenerationTask is GenerationTask
    assert clothing.ClothingGenerationTask is GenerationTask


def test_get_domain_caches_and_rejects_unknown_names() -> None:
    assert get_domain("restaurant") is get_domain("restaurant")
    with pytest.raises(KeyError, match="unknown domain"):
        get_domain("no-such-domain")


def test_workflow_map_covers_every_domain() -> None:
    from layanep.domains import workflow_map

    mapped = workflow_map()
    for name in available_domains():
        domain = get_domain(name)
        assert mapped[domain.WORKFLOW] is domain
