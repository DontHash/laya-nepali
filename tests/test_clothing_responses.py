"""Clothing response templates: fill logic, escalation messages, and Devanagari content."""

from __future__ import annotations

import re

from layanep.clothing_policy import T0_READ_ONLY
from layanep.clothing_responses import (
    ESCALATION_TEMPLATES,
    RESPONSE_TEMPLATES,
    escalation_message,
    fill_template,
)

DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")

CLOTHING_STATE: dict = {
    "business": {
        "name": "Hamro Fashion",
        "hours": {"open": "10:00", "close": "20:00"},
        "delivery": {"areas": ["Kathmandu", "Lalitpur", "Bhaktapur"], "fee": "100"},
        "cod_available": True,
        "catalog": [
            {
                "name": "कुर्था",
                "price": 1500,
                "sizes": ["M", "L", "XL"],
                "colors": ["रातो", "निलो"],
                "material": "कटन",
            },
            {
                "name": "हुडी",
                "price": 2200,
                "sizes": ["L", "XL"],
                "colors": ["कालो"],
                "material": "फ्लीस",
            },
        ],
    },
    "product": "कुर्था",
    "price": "1500",
    "sizes": "M, L, XL",
    "colors": "रातो, निलो",
    "material_desc": "कटन",
    "cart_items": "कुर्था (L) x1",
}


def test_clothing_fill_template_full_state() -> None:
    result = fill_template("greet", CLOTHING_STATE)
    assert "Hamro Fashion" in result


def test_clothing_fill_template_missing_state_falls_back() -> None:
    result = fill_template("price", {})
    assert "{" not in result
    assert DEVANAGARI_RE.search(result)


def test_clothing_fill_template_unknown_label_returns_escalation() -> None:
    result = fill_template("unknown_clothing_xyz", {})
    assert result == ESCALATION_TEMPLATES[3]


def test_clothing_all_templates_have_both_strings() -> None:
    for label, pair in RESPONSE_TEMPLATES.items():
        assert isinstance(pair, tuple) and len(pair) == 2, f"{label} pair shape"
        specific, generic = pair
        assert isinstance(specific, str) and len(specific) > 0, f"{label} specific"
        assert isinstance(generic, str) and len(generic) > 0, f"{label} generic"


def test_clothing_escalation_message_tiers() -> None:
    for tier in (1, 2, 3):
        msg = escalation_message(tier)
        assert isinstance(msg, str) and len(msg) > 0
        assert msg == ESCALATION_TEMPLATES[tier]


def test_clothing_escalation_message_unknown_tier_falls_back() -> None:
    assert escalation_message(99) == ESCALATION_TEMPLATES[3]


def test_clothing_fill_template_price_contains_price() -> None:
    result = fill_template("price", CLOTHING_STATE)
    assert "1500" in result
    assert "कुर्था" in result


def test_clothing_fill_template_size_contains_sizes() -> None:
    result = fill_template("size", CLOTHING_STATE)
    assert "M, L, XL" in result


def test_clothing_all_templates_contain_devanagari() -> None:
    for label, (specific, generic) in RESPONSE_TEMPLATES.items():
        assert DEVANAGARI_RE.search(specific), f"{label} specific lacks Devanagari"
        assert DEVANAGARI_RE.search(generic), f"{label} generic lacks Devanagari"
    for tier, text in ESCALATION_TEMPLATES.items():
        assert DEVANAGARI_RE.search(text), f"escalation tier {tier} lacks Devanagari"


def test_clothing_response_templates_cover_t0_labels() -> None:
    assert T0_READ_ONLY <= set(RESPONSE_TEMPLATES), (
        f"missing: {T0_READ_ONLY - set(RESPONSE_TEMPLATES)}"
    )
