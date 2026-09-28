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
        assert domain.DOMAIN_NAME == name
        assert set(domain.questions("Test Shop")) == {
            "command",
            "query_field",
            "order_intent",
            "needs_staff",
            "abstain",
        }
        assert domain.T0_READ_ONLY <= set(domain.RESPONSE_TEMPLATES)


def test_get_domain_caches_and_rejects_unknown_names() -> None:
    assert get_domain("restaurant") is get_domain("restaurant")
    with pytest.raises(KeyError, match="unknown domain"):
        get_domain("no-such-domain")
