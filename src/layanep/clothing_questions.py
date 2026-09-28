"""Canonical question set for one clothing-domain case.

Mirrors ``questions.py`` (restaurant domain) with command kinds specific to
clothing businesses on WhatsApp and Instagram.  The five-question structure
is identical — command, query_field, order_intent, needs_staff, abstain — so
the same ``schema.py`` contract, export gate and training loop apply.

The command vocabulary here is the single source of truth for the clothing
domain.  Natural-language criteria keys are used (matching the restaurant
domain's probe result: 55/79 natural vs 16/79 dotted).
"""

from __future__ import annotations

from .schema import ABSTAIN_KEY, Question

# ---------------------------------------------------------------------------
# Clothing LU command kinds (dotted notation for wire format)
# ---------------------------------------------------------------------------

CLOTHING_LU_COMMAND_KINDS = (
    "social.greet",
    "social.thanks",
    "social.goodbye",
    "discovery.show_catalog",
    "discovery.recommend",
    "discovery.query",         # price, size, color, material, stock
    "fulfillment.ask_delivery",
    "fulfillment.ask_cod",
    "fulfillment.order_status",
    "ordering.view_cart",
    "ordering.request_checkout",
    "ordering.request_exchange",
    "ordering.custom_order",
    "ordering.use_saved_address",
)

# ---------------------------------------------------------------------------
# Command criteria — natural-language keys (18 + abstain)
# ---------------------------------------------------------------------------

NE_CLOTHING_QUESTION_IDS = ("command", "query_field", "order_intent", "needs_staff", "abstain")

CLOTHING_COMMAND_CRITERIA = {
    "greet": "hello or greeting",
    "thanks": "thanks",
    "goodbye": "goodbye",
    "catalog": "see products, new arrivals or the catalog",
    "recommend": "recommendation or best seller",
    "price": "asking how much an item costs",
    "size": "asking about available sizes or size chart",
    "color": "asking about available colors",
    "material": "asking what fabric or material an item is made of",
    "stock": "asking whether an item is in stock",
    "delivery": "delivery area, fee or time",
    "cod": "asking about cash on delivery",
    "order_status": "status of an existing order",
    "cart": "see current cart or order",
    "checkout": "place order or buy",
    "exchange": "exchange or return an item",
    "custom_order": "custom stitching or tailoring request",
    "saved_address": "use a saved delivery address",
    ABSTAIN_KEY: "none of these",
}

CLOTHING_COMMAND_LABEL_TO_KIND = {
    "greet": "social.greet",
    "thanks": "social.thanks",
    "goodbye": "social.goodbye",
    "catalog": "discovery.show_catalog",
    "recommend": "discovery.recommend",
    "price": "discovery.query",
    "size": "discovery.query",
    "color": "discovery.query",
    "material": "discovery.query",
    "stock": "discovery.query",
    "delivery": "fulfillment.ask_delivery",
    "cod": "fulfillment.ask_cod",
    "order_status": "fulfillment.order_status",
    "cart": "ordering.view_cart",
    "checkout": "ordering.request_checkout",
    "exchange": "ordering.request_exchange",
    "custom_order": "ordering.custom_order",
    "saved_address": "ordering.use_saved_address",
}

CLOTHING_QUERY_FIELDS = ("price", "size", "color", "material", "stock")

CLOTHING_COMMAND_GUIDANCE = (
    "Only choose a command when the message clearly expresses it. Choose none for: "
    "bare item requests like 'yo chaiyo', plain yes/no, requests for a human or staff, "
    "skin sensitivity or allergy questions, refund demands, counterfeit concerns, "
    "and unclear text. A question like 'kati ho?' is a price question, not an order. "
    "order_status means tracking an existing order; exchange means swapping a received item. "
    "custom_order is for tailoring or stitching requests, not buying a ready-made item."
)

CLOTHING_COMMAND_INSTRUCTIONS_TEMPLATE = (
    "Classify the customer's message for {business_name} (clothing store). " + CLOTHING_COMMAND_GUIDANCE
)

CLOTHING_QUERY_FIELD_DESCRIPTIONS = {
    "price": "asking how much an item costs",
    "size": "asking about available sizes",
    "color": "asking about available colors",
    "material": "asking what fabric or material",
    "stock": "asking whether an item is in stock",
    ABSTAIN_KEY: "not a product query",
}


def clothing_command_question(business_name: str | None = None) -> Question:
    return Question(
        type="choice",
        instructions=CLOTHING_COMMAND_INSTRUCTIONS_TEMPLATE.format(
            business_name=business_name or "the store"
        ),
        criteria=dict(CLOTHING_COMMAND_CRITERIA),
    )


def clothing_questions(business_name: str | None = None) -> dict[str, Question]:
    """Return all 5 canonical typed questions for a clothing case."""
    return {
        "command": clothing_command_question(business_name),
        "query_field": Question(
            type="choice",
            instructions=(
                "If the message asks about a product, which detail does it ask about? "
                "Choose none when the message is not a product query."
            ),
            criteria=dict(CLOTHING_QUERY_FIELD_DESCRIPTIONS),
        ),
        "order_intent": Question(
            type="noul",
            instructions=(
                "Does the customer message attempt to buy, exchange or customize "
                "a clothing item (a purchase or post-purchase mutation)?"
            ),
        ),
        "needs_staff": Question(
            type="noul",
            instructions=(
                "Does this message need a human staff member (skin sensitivity or allergy "
                "questions about fabric, refund demands, counterfeit concerns, sizing disputes "
                "after purchase, or a direct request for a human)?"
            ),
        ),
        "abstain": Question(
            type="noul",
            instructions=(
                "Must the assistant refuse to map this message to any command (bare item "
                "requests, plain yes/no, gibberish, or unclear text)?"
            ),
        ),
    }


def clothing_label_to_kind(label: str) -> str | None:
    """Map a ``command`` criteria key onto its clothing LU kind (``none`` -> None)."""
    return CLOTHING_COMMAND_LABEL_TO_KIND.get(label)


def assert_clothing_vocabulary() -> None:
    """Integrity check: every LU kind is reachable, every criteria key maps somewhere."""
    missing_kinds = [
        kind for kind in CLOTHING_LU_COMMAND_KINDS
        if kind not in set(CLOTHING_COMMAND_LABEL_TO_KIND.values())
    ]
    if missing_kinds:
        raise AssertionError(f"CLOTHING_COMMAND_LABEL_TO_KIND misses LU kinds: {missing_kinds}")
    unmapped = sorted(set(CLOTHING_COMMAND_CRITERIA) - set(CLOTHING_COMMAND_LABEL_TO_KIND) - {ABSTAIN_KEY})
    if unmapped:
        raise AssertionError(f"clothing command criteria keys with no LU kind: {unmapped}")
    missing_fields = [field for field in CLOTHING_QUERY_FIELDS if field not in CLOTHING_QUERY_FIELD_DESCRIPTIONS]
    if missing_fields:
        raise AssertionError(f"clothing query_field criteria are missing fields: {missing_fields}")
