"""Shared response engine for the domain response templates.

Domain modules own their ``RESPONSE_TEMPLATES`` tables and state flatteners
(``responses.py`` for restaurant, ``clothing_responses.py`` for clothing); the
fill/fallback logic and the tier escalation wording live here once.

When a placeholder is missing from the state, the specific template is tried
first, then its generic fallback, and finally the text before the first
placeholder — so a reply never leaks a ``{placeholder}``.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence

# Escalation templates — used when auto-serve is off and a human is needed.
ESCALATION_TEMPLATES: dict[int, str] = {
    # Tier 0: the model saw a T0 label but could not confirm it. Never claim an
    # action; hand the customer to the human path.
    0: "यो जानकारी पुष्टि गर्न सकिएन। कृपया हाम्रो टोलीलाई सम्पर्क गर्नुहोस्।",
    1: "तपाईंको अनुरोध हाम्रो टोलीलाई पठाइएको छ। केही बेरमा जवाफ दिन्छौं।",
    2: "यो विषयमा हाम्रो स्टाफसँग कुरा गर्नुपर्छ। तुरुन्तै सम्पर्क गर्छौं।",
    3: "माफ गर्नुहोस्, तपाईंको सन्देश बुझ्न सकिएन। कृपया फेरि लेख्नुहोस्।",
}

ESCALATION_FALLBACK = "कृपया पर्खनुहोस्।"

Flattener = Callable[[Mapping[str, Any]], dict[str, str]]


def fill_template(
    label: str,
    state: Mapping[str, Any],
    templates: Mapping[str, tuple[str, str]],
    flatten: Flattener,
) -> str:
    """Return a Nepali response for the given command label and business state.

    Falls back to the generic template when required placeholders are missing.
    """
    if label not in templates:
        return ESCALATION_TEMPLATES.get(3, ESCALATION_FALLBACK)

    specific, generic = templates[label]
    flat = flatten(state)
    try:
        return specific.format_map(flat)
    except KeyError:
        try:
            return generic.format_map(flat)
        except KeyError:
            return generic.split("{")[0].rstrip() + "।" if "{" in generic else generic


def escalation_message(tier: int) -> str:
    """Return the customer-facing escalation message for the given tier."""
    return ESCALATION_TEMPLATES.get(tier, ESCALATION_TEMPLATES[3])


def flatten_business(state: Mapping[str, Any]) -> dict[str, str]:
    """Flatten the shared business fields (name, hours, delivery) for templates."""
    flat: dict[str, str] = {}
    business = state.get("business", {})
    if isinstance(business, dict):
        flat["business_name"] = str(business.get("name", ""))
        hours = business.get("hours", {})
        if isinstance(hours, dict):
            flat["open_time"] = str(hours.get("open", ""))
            flat["close_time"] = str(hours.get("close", ""))
        delivery = business.get("delivery", {})
        if isinstance(delivery, dict):
            areas = delivery.get("areas", [])
            flat["areas"] = ", ".join(str(a) for a in areas) if isinstance(areas, list) else str(areas)
            flat["fee"] = str(delivery.get("fee", ""))
    return flat


def join_names(items: Sequence[Any]) -> str:
    """Join up to ten item names (dicts or strings) for template use."""
    names = [str(item.get("name", item) if isinstance(item, dict) else item) for item in items[:10]]
    return ", ".join(names)
