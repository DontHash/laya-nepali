"""Nepali response templates for the restaurant domain.

Each template corresponds to a command criteria key from ``questions.py``.
Templates use Python ``str.format`` placeholders filled from the business
state (menu, hours, delivery info, etc.). The fill/fallback engine lives in
``responses_core.py``.

Placeholder conventions:
- ``{business_name}`` — restaurant name (always available)
- ``{items}`` — comma-separated menu item list
- ``{item}`` — the specific item asked about
- ``{price}`` — price string with "रु." prefix
- ``{open_time}`` / ``{close_time}`` — business hours
- ``{areas}`` — delivery area list
- ``{fee}`` — delivery fee

When a placeholder is missing from the state, the template falls back to a
generic response that avoids hallucinating specifics.
"""

from __future__ import annotations

from typing import Any, Mapping

from .responses_core import (
    ESCALATION_TEMPLATES as ESCALATION_TEMPLATES,
    escalation_message as escalation_message,
    fill_template as _fill_template,
    flatten_business,
    join_names,
)

# ---------------------------------------------------------------------------
# Template pairs: (specific template with placeholders, generic fallback)
# ---------------------------------------------------------------------------

RESPONSE_TEMPLATES: dict[str, tuple[str, str]] = {
    "greet": (
        "नमस्ते! {business_name} मा स्वागत छ। कसरी मद्दत गर्न सक्छु?",
        "नमस्ते! कसरी मद्दत गर्न सक्छु?",
    ),
    "thanks": (
        "धन्यवाद! {business_name} मा फेरि आउनुहोस्।",
        "धन्यवाद! फेरि आउनुहोस्।",
    ),
    "goodbye": (
        "नमस्कार! फेरि भेटौंला।",
        "नमस्कार! फेरि भेटौंला।",
    ),
    "menu": (
        "हाम्रो मेनुमा {items} छ। के अर्डर गर्नुहुन्छ?",
        "हाम्रो मेनु हेर्न चाहनुभएको हो? म पठाउँछु।",
    ),
    "recommend": (
        "हाम्रो लोकप्रिय खाना {items} हो। के ट्राई गर्नुहुन्छ?",
        "हाम्रो सबैभन्दा लोकप्रिय खाना सिफारिस गर्छु। के ट्राई गर्नुहुन्छ?",
    ),
    "price": (
        "{item} को मूल्य रु. {price} हो।",
        "मूल्य जान्न चाहनुभएको हो? कुन खानाको?",
    ),
    "availability": (
        "{item} अहिले उपलब्ध छ।",
        "उपलब्धता जान्न चाहनुभएको हो? कुन खानाको?",
    ),
    "details": (
        "{item} मा {ingredients} पर्छ।",
        "विवरण जान्न चाहनुभएको हो? कुन खानाको?",
    ),
    "hours": (
        "हामी {open_time} देखि {close_time} सम्म खुला छौं।",
        "हाम्रो खुल्ने समय जानकारीको लागि कुर्नुहोस्।",
    ),
    "delivery": (
        "हामी {areas} मा डेलिभरी गर्छौं। डेलिभरी चार्ज रु. {fee} हो।",
        "डेलिभरीको बारेमा जान्न चाहनुभएको हो? कुर्नुहोस्, जानकारी दिन्छु।",
    ),
    "order_status": (
        "तपाईंको अर्डरको अवस्था जाँच गर्दैछु।",
        "तपाईंको अर्डरको अवस्था जाँच गर्दैछु।",
    ),
    "cart": (
        "तपाईंको कार्टमा अहिले {cart_items} छ।",
        "तपाईंको कार्ट हेर्दैछु।",
    ),
}


def fill_template(label: str, state: Mapping[str, Any]) -> str:
    """Return a Nepali response for the given command label and business state.

    Falls back to the generic template when required placeholders are missing.
    """
    return _fill_template(label, state, RESPONSE_TEMPLATES, _flatten_state)


def _flatten_state(state: Mapping[str, Any]) -> dict[str, str]:
    """Flatten a nested business state into a string-valued dict for templates.

    Handles the common state shapes:
    - ``{"business": {"name": "...", "hours": {...}, "delivery": {...}}, ...}``
    - ``{"body": "...", "menu": [...], ...}``
    """
    flat = flatten_business(state)
    business = state.get("business", {})
    menu = state.get("menu", business.get("menu", []))
    if isinstance(menu, list):
        flat["items"] = join_names(menu)

    for key in ("item", "price", "ingredients", "cart_items"):
        if key in state:
            flat[key] = str(state[key])

    return flat
