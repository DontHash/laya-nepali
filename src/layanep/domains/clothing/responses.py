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
        "हाम्रो क्याटलग हेर्न चाहनुभएको हो? कृपया कुन कपडा चाहिने भन्नुहोस्।",
    ),
    "recommend": (
        "हाम्रो लोकप्रिय कपडा {products} हो। के ट्राई गर्नुहुन्छ?",
        "कुन किसिमको कपडा खोज्दै हुनुहुन्छ? कृपया भन्नुहोस्।",
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
        "डेलिभरीको बारेमा जान्न चाहनुभएको हो? कृपया आफ्नो स्थान लेख्नुहोस्।",
    ),
    "cod": (
        "{business_name} मा क्यास अन डेलिभरी उपलब्ध छ।",
        "क्यास अन डेलिभरीको बारेमा जान्न चाहनुभएको हो? कृपया भन्नुहोस्।",
    ),
    "order_status": (
        "तपाईंको अर्डरको जानकारीका लागि कृपया अर्डर नम्बर वा मिति पठाउनुहोस्।",
        "कुन अर्डरको अवस्था जान्न चाहनुहुन्छ? कृपया अर्डर नम्बर पठाउनुहोस्।",
    ),
    "cart": (
        "तपाईंको कार्टमा अहिले {cart_items} छ।",
        "कार्टको जानकारीका लागि कृपया हाम्रो टोलीलाई सम्पर्क गर्नुहोस्।",
    ),
}


COD_UNAVAILABLE = "हामी क्यास अन डेलिभरी (COD) उपलब्ध गर्दैनौं।"


def _cod_available(state: Mapping[str, Any]) -> bool | None:
    """Read the caller's stated COD flag; ``None`` means "not stated"."""
    business = state.get("business")
    if isinstance(business, dict) and "cod_available" in business:
        value = business.get("cod_available")
    elif "cod_available" in state:
        value = state.get("cod_available")
    else:
        return None
    if value is None:
        return None
    return value is True


def fill_template(label: str, state: Mapping[str, Any]) -> str:
    """Return a Nepali response for the given command label and business state.

    Falls back to the generic template when required placeholders are missing.
    ``cod`` asserts availability only when the caller stated
    ``cod_available: true``; an explicit ``false`` renders the negative form
    and an unstated flag renders the clarifying question.
    """
    if label == "cod":
        available = _cod_available(state)
        if available is False:
            return COD_UNAVAILABLE
        if available is not True:
            return RESPONSE_TEMPLATES["cod"][1]
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
