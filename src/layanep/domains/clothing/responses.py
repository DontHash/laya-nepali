"""Nepali response templates for the clothing domain.

Each template corresponds to a command criteria key from ``questions.py``.
Templates use Python ``str.format`` placeholders filled from the business
state (catalog, delivery info, etc.). The fill/fallback engine lives in
``responses_core.py``.

Placeholder conventions:
- ``{business_name}`` — store name (always available)
- ``{products}`` — comma-separated product name list
- ``{product}`` — the specific product asked about
- ``{price}`` — price string with "रु." prefix
- ``{sizes}`` — available sizes for a product
- ``{colors}`` — available colours for a product
- ``{material_desc}`` — material / fabric description
- ``{areas}`` — delivery area list
- ``{fee}`` — delivery fee
- ``{open_time}`` / ``{close_time}`` — business hours
- ``{cart_items}`` — current cart summary
"""

from __future__ import annotations

from typing import Any, Mapping

from ...responses_core import (
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
    "catalog": (
        "हाम्रो क्याटलगमा {products} छ। के हेर्नुहुन्छ?",
        "हाम्रो क्याटलग हेर्न चाहनुभएको हो? म पठाउँछु।",
    ),
    "recommend": (
        "हाम्रो लोकप्रिय कपडा {products} हो। के ट्राई गर्नुहुन्छ?",
        "हाम्रो सबैभन्दा लोकप्रिय कपडा सिफारिस गर्छु। के ट्राई गर्नुहुन्छ?",
    ),
    "price": (
        "{product} को मूल्य रु. {price} हो।",
        "मूल्य जान्न चाहनुभएको हो? कुन कपडाको?",
    ),
    "size": (
        "{product} मा {sizes} साइज उपलब्ध छ।",
        "साइज जान्न चाहनुभएको हो? कुन कपडाको?",
    ),
    "color": (
        "{product} मा {colors} रङ उपलब्ध छ।",
        "रङ जान्न चाहनुभएको हो? कुन कपडाको?",
    ),
    "material": (
        "{product} {material_desc} को बनेको हो।",
        "कपडाको सामग्री जान्न चाहनुभएको हो? कुन कपडाको?",
    ),
    "stock": (
        "{product} अहिले स्टकमा उपलब्ध छ।",
        "स्टक जान्न चाहनुभएको हो? कुन कपडाको?",
    ),
    "delivery": (
        "हामी {areas} मा डेलिभरी गर्छौं। डेलिभरी चार्ज रु. {fee} हो।",
        "डेलिभरीको बारेमा जान्न चाहनुभएको हो? कुर्नुहोस्, जानकारी दिन्छु।",
    ),
    "cod": (
        "{business_name} मा क्यास अन डेलिभरी उपलब्ध छ।",
        "क्यास अन डेलिभरीको बारेमा जान्न चाहनुभएको हो? कुर्नुहोस्।",
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
    - ``{"business": {"name": "...", "cod_available": ..., "delivery": {...}}, ...}``
    - ``{"body": "...", "catalog": [...], ...}``
    """
    flat = flatten_business(state)
    business = state.get("business", {})
    if isinstance(business, dict) and business.get("cod_available"):
        flat["cod_available"] = "true"

    catalog = state.get("catalog", business.get("catalog", []))
    if isinstance(catalog, list):
        flat["products"] = join_names(catalog)

    for key in ("product", "price", "cart_items"):
        if key in state:
            flat[key] = str(state[key])

    # Per-product attributes from catalog or direct state keys.
    for key in ("sizes", "colors", "material_desc"):
        if key in state:
            val = state[key]
            flat[key] = ", ".join(str(v) for v in val) if isinstance(val, list) else str(val)

    return flat
