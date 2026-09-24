"""Canonical five-question set for one Nepali case.

One case asks five typed decisions over the same state, matching the
typed-decisions benchmark shape:

1. ``command``      choice over the 13 LU command kinds plus an abstain key
2. ``query_field``  choice over price / availability / details / none
3. ``order_intent`` noul: does the message attempt an order mutation?
4. ``needs_staff``  noul: allergy/ingredient/refund/complaint/human handoff?
5. ``abstain``      noul: must the assistant refuse to map any command?

Criteria keys are machine-stable (the dotted LU kinds) while the descriptions
carry the natural-language wording that the zero-shot probe found to be the
strongest accuracy lever for this model family.
"""

from __future__ import annotations

from .schema import ABSTAIN_KEY, LU_COMMAND_KINDS, QUERY_FIELDS, Question

NE_QUESTION_IDS = ("command", "query_field", "order_intent", "needs_staff", "abstain")

KIND_DESCRIPTIONS = {
    "social.greet": "hello or greeting",
    "social.thanks": "thanks",
    "social.goodbye": "goodbye",
    "discovery.show_menu": "see the menu",
    "discovery.recommend": "recommendation",
    "discovery.query": "asking about price, availability or details of an item",
    "fulfillment.ask_hours": "opening hours",
    "fulfillment.ask_delivery": "delivery area or fee",
    "fulfillment.order_status": "status of an existing order",
    "ordering.view_cart": "see current cart",
    "ordering.request_checkout": "checkout or place order",
    "ordering.repeat_order": "repeat a previous order",
    "ordering.use_saved_address": "use a saved address",
    ABSTAIN_KEY: "none of these",
}

QUERY_FIELD_DESCRIPTIONS = {
    "price": "asking how much an item costs",
    "availability": "asking whether an item is available",
    "details": "asking what an item contains",
    ABSTAIN_KEY: "not a discovery.query message",
}


def ne_questions(business_name: str | None = None) -> dict[str, Question]:
    where = f" for {business_name}" if business_name else ""
    return {
        "command": Question(
            type="choice",
            instructions=f"Classify the customer's message into one command kind{where}.",
            criteria=dict(KIND_DESCRIPTIONS),
        ),
        "query_field": Question(
            type="choice",
            instructions=(
                "If the message asks about an item, which detail does it ask about? "
                "Choose none when the message is not a discovery.query."
            ),
            criteria=dict(QUERY_FIELD_DESCRIPTIONS),
        ),
        "order_intent": Question(
            type="noul",
            instructions=(
                "Does the customer message attempt to place, change or remove an order item "
                "(an order mutation)?"
            ),
        ),
        "needs_staff": Question(
            type="noul",
            instructions=(
                "Does this message need a human staff member (allergy or ingredient questions, "
                "refunds, complaints, or a direct request for a human)?"
            ),
        ),
        "abstain": Question(
            type="noul",
            instructions=(
                "Must the assistant refuse to map this message to any command (bare item orders, "
                "plain yes/no, gibberish, or unclear text)?"
            ),
        ),
    }


def assert_full_vocabulary() -> None:
    missing = [kind for kind in LU_COMMAND_KINDS if kind not in KIND_DESCRIPTIONS]
    if missing:
        raise AssertionError(f"command criteria are missing LU kinds: {missing}")
    missing_fields = [field for field in QUERY_FIELDS if field not in QUERY_FIELD_DESCRIPTIONS]
    if missing_fields:
        raise AssertionError(f"query_field criteria are missing fields: {missing_fields}")
