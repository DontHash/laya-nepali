"""Response templates: fill logic, escalation messages, and Devanagari content."""

from __future__ import annotations

import re

from layanep.policy import T0_READ_ONLY
from layanep.responses import (
    ESCALATION_TEMPLATES,
    RESPONSE_TEMPLATES,
    escalation_message,
    fill_template,
)

DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")

FULL_STATE: dict = {
    "business": {
        "name": "Sherpa Kitchen",
        "hours": {"open": "10:00", "close": "22:00"},
        "delivery": {"areas": ["Thamel", "Lazimpat"], "fee": "100"},
        "menu": [{"name": "मःम"}, {"name": "थुक्पा"}],
    },
    "item": "मःम",
    "price": "250",
    "ingredients": "भैंसीको मासु, पिठो",
    "cart_items": "मःम x2",
}


def test_fill_template_full_state() -> None:
    result = fill_template("greet", FULL_STATE)
    assert "Sherpa Kitchen" in result


def test_fill_template_missing_state_falls_back() -> None:
    result = fill_template("price", {})
    # generic fallback should not contain placeholders
    assert "{" not in result
    assert DEVANAGARI_RE.search(result)


def test_fill_template_unknown_label_returns_escalation() -> None:
    result = fill_template("unknown_xyz", {})
    assert result == ESCALATION_TEMPLATES[3]


def test_all_templates_have_both_strings() -> None:
    for label, pair in RESPONSE_TEMPLATES.items():
        assert isinstance(pair, tuple) and len(pair) == 2, f"{label} pair shape"
        specific, generic = pair
        assert isinstance(specific, str) and len(specific) > 0, f"{label} specific"
        assert isinstance(generic, str) and len(generic) > 0, f"{label} generic"


def test_escalation_message_tiers() -> None:
    for tier in (1, 2, 3):
        msg = escalation_message(tier)
        assert isinstance(msg, str) and len(msg) > 0
        assert msg == ESCALATION_TEMPLATES[tier]


def test_escalation_message_unknown_tier_falls_back() -> None:
    assert escalation_message(99) == ESCALATION_TEMPLATES[3]


def test_fill_template_greet_contains_business_name() -> None:
    result = fill_template("greet", {"business": {"name": "Sherpa Kitchen"}})
    assert "Sherpa Kitchen" in result


def test_fill_template_hours_contains_times() -> None:
    result = fill_template(
        "hours",
        {"business": {"hours": {"open": "10:00", "close": "22:00"}}},
    )
    assert "10:00" in result
    assert "22:00" in result


def test_all_templates_contain_devanagari() -> None:
    for label, (specific, generic) in RESPONSE_TEMPLATES.items():
        assert DEVANAGARI_RE.search(specific), f"{label} specific lacks Devanagari"
        assert DEVANAGARI_RE.search(generic), f"{label} generic lacks Devanagari"
    for tier, text in ESCALATION_TEMPLATES.items():
        assert DEVANAGARI_RE.search(text), f"escalation tier {tier} lacks Devanagari"


def test_response_templates_cover_t0_labels() -> None:
    assert T0_READ_ONLY <= set(RESPONSE_TEMPLATES), (
        f"missing: {T0_READ_ONLY - set(RESPONSE_TEMPLATES)}"
    )
