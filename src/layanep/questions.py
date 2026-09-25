"""Canonical five-question set for one Nepali case.

One case asks five typed decisions over the same state, matching the
typed-decisions benchmark shape:

1. ``command``      choice over the 13 LU command kinds plus an abstain key
2. ``query_field``  choice over price / availability / details / none
3. ``order_intent`` noul: does the message attempt an order mutation?
4. ``needs_staff``  noul: allergy/ingredient/refund/complaint/human handoff?
5. ``abstain``      noul: must the assistant refuse to map any command?

The command vocabulary here is the single source of truth shared by the
training dataset and the frozen ``ne-probe-v1`` benchmark: natural-language
criteria keys (``price``, ``order_status``, ...) mapped onto the dotted LU
kinds by ``COMMAND_LABEL_TO_KIND``. The zero-shot probe measured natural keys
at 55/79 against 16/79 for dotted keys, so training and evaluation must use the
same keys and the same instructions.
"""

from __future__ import annotations

from .schema import ABSTAIN_KEY, LU_COMMAND_KINDS, QUERY_FIELDS, Question

NE_QUESTION_IDS = ("command", "query_field", "order_intent", "needs_staff", "abstain")

COMMAND_CRITERIA = {
    "greet": "hello or greeting",
    "thanks": "thanks",
    "goodbye": "goodbye",
    "menu": "see the menu",
    "recommend": "recommendation",
    "price": "asking how much an item costs",
    "availability": "asking whether an item is available",
    "details": "asking what an item contains",
    "hours": "opening hours",
    "delivery": "delivery area or fee",
    "order_status": "status of an existing order",
    "cart": "see current cart",
    "checkout": "checkout or place order",
    "repeat_order": "repeat a previous order",
    "saved_address": "use a saved address",
    ABSTAIN_KEY: "none of these",
}

COMMAND_LABEL_TO_KIND = {
    "greet": "social.greet",
    "thanks": "social.thanks",
    "goodbye": "social.goodbye",
    "menu": "discovery.show_menu",
    "recommend": "discovery.recommend",
    "price": "discovery.query",
    "availability": "discovery.query",
    "details": "discovery.query",
    "hours": "fulfillment.ask_hours",
    "delivery": "fulfillment.ask_delivery",
    "order_status": "fulfillment.order_status",
    "cart": "ordering.view_cart",
    "checkout": "ordering.request_checkout",
    "repeat_order": "ordering.repeat_order",
    "saved_address": "ordering.use_saved_address",
}

COMMAND_GUIDANCE = (
    "Only choose a command when the message clearly expresses it. Choose none for: bare item "
    "orders like 'momos please', plain yes/no, requests for a human or staff, allergy, refund or "
    "complaint issues, and unclear text. A question like 'how much is X' is a price question, not "
    "an order. order_status means tracking an existing order; cart means seeing the current draft "
    "order."
)

COMMAND_INSTRUCTIONS_TEMPLATE = (
    "Classify the customer's WhatsApp message for {business_name}. " + COMMAND_GUIDANCE
)

QUERY_FIELD_DESCRIPTIONS = {
    "price": "asking how much an item costs",
    "availability": "asking whether an item is available",
    "details": "asking what an item contains",
    ABSTAIN_KEY: "not a discovery.query message",
}


def command_question(business_name: str | None = None) -> Question:
    return Question(
        type="choice",
        instructions=COMMAND_INSTRUCTIONS_TEMPLATE.format(business_name=business_name or "the restaurant"),
        criteria=dict(COMMAND_CRITERIA),
    )


def ne_questions(business_name: str | None = None) -> dict[str, Question]:
    return {
        "command": command_question(business_name),
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


def label_to_kind(label: str) -> str | None:
    """Map a ``command`` criteria key onto its LU kind (``none`` -> None)."""
    return COMMAND_LABEL_TO_KIND.get(label)


def assert_full_vocabulary() -> None:
    missing_kinds = [kind for kind in LU_COMMAND_KINDS if kind not in set(COMMAND_LABEL_TO_KIND.values())]
    if missing_kinds:
        raise AssertionError(f"COMMAND_LABEL_TO_KIND misses LU kinds: {missing_kinds}")
    unmapped = sorted(set(COMMAND_CRITERIA) - set(COMMAND_LABEL_TO_KIND) - {ABSTAIN_KEY})
    if unmapped:
        raise AssertionError(f"command criteria keys with no LU kind: {unmapped}")
    missing_fields = [field for field in QUERY_FIELDS if field not in QUERY_FIELD_DESCRIPTIONS]
    if missing_fields:
        raise AssertionError(f"query_field criteria are missing fields: {missing_fields}")
