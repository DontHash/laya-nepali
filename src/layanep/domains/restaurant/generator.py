"""Training templates: businesses, intent families, prompts, and derived gold.

Benchmark menus are held out from generation (see AGENTS.md), so the training
states use their own fictional businesses and menus. Gold is constructed by
``generation_core`` from the family that requested the message rather than
sampled from a teacher; the review pass corrects any message that fails to
express its intent.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Sequence

from .questions import COMMAND_CRITERIA, QUERY_FIELD_DESCRIPTIONS, ne_questions
from ...generation_core import (
    GenerationFamily,
    GenerationSpec,
    GenerationTask,
    build_budget_plan,
    build_case as _build_case,
    build_variant_plan,
    derive_gold as _derive_gold,
    prompt_rules,
)
from ...schema import QUERY_FIELDS, Case, Gold

GENERATOR_WORKFLOW = "restaurant_command_lu"
LANGUAGES = ("ne", "ne-rom", "en")

LANGUAGE_INSTRUCTIONS = {
    "ne": "Nepali in Devanagari script",
    "ne-rom": "Nepali typed in Latin script (Romanized Nepali, the way people type without a Nepali keyboard)",
    "en": "English (Nepali food words allowed)",
}


@dataclass(frozen=True)
class MenuItem:
    name: str
    price_npr: int
    available: bool = True
    contains: str | None = None

    def to_state(self) -> dict:
        item: dict = {"name": self.name, "price_npr": self.price_npr, "available": self.available}
        if self.contains:
            item["contains"] = self.contains
        return item


@dataclass(frozen=True)
class TrainingBusiness:
    id: str
    name: str
    area: str
    hours: str
    delivery_area: str
    delivery_fee_npr: int
    menu: tuple[MenuItem, ...]

    def state_base(self) -> dict:
        return {
            "business": {
                "name": self.name,
                "area": self.area,
                "hours": self.hours,
                "delivery_area": self.delivery_area,
                "delivery_fee_npr": self.delivery_fee_npr,
            },
            "menu": [item.to_state() for item in self.menu],
        }


TRAINING_BUSINESSES: tuple[TrainingBusiness, ...] = (
    TrainingBusiness(
        id="thamel-thali",
        name="Thamel Thali House",
        area="Thamel",
        hours="11 AM - 10 PM daily",
        delivery_area="Kathmandu ring road",
        delivery_fee_npr=100,
        menu=(
            MenuItem("Veg Thali", 350, contains="rice, lentils, seasonal vegetables"),
            MenuItem("Chicken Thali", 480, contains="rice, lentils, chicken curry"),
            MenuItem("Masala Tea", 80),
            MenuItem("Mango Lassi", 180, contains="yogurt, milk, mango"),
        ),
    ),
    TrainingBusiness(
        id="lakeside-momo",
        name="Lakeside Momo Corner",
        area="Lakeside, Pokhara",
        hours="10 AM - 9 PM daily",
        delivery_area="Lakeside and Baidam",
        delivery_fee_npr=80,
        menu=(
            MenuItem("Chicken Momo", 250, contains="chicken, flour, onion"),
            MenuItem("Buff Momo", 220, contains="buff, flour, onion"),
            MenuItem("Veg Momo", 200, contains="cabbage, carrot, flour"),
            MenuItem("Chicken Chowmein", 280, contains="noodles, chicken, vegetables"),
        ),
    ),
    TrainingBusiness(
        id="patan-cafe",
        name="Patan Cafe",
        area="Patan",
        hours="8 AM - 8 PM daily",
        delivery_area="Patan and Jawalakhel",
        delivery_fee_npr=120,
        menu=(
            MenuItem("Cappuccino", 220, contains="milk"),
            MenuItem("Veg Sandwich", 250, contains="bread, cheese, tomato"),
            MenuItem("Chocolate Cake", 300, contains="flour, egg, milk, chocolate"),
            MenuItem("Lemon Tea", 100),
        ),
    ),
    TrainingBusiness(
        id="mithila-kitchen",
        name="Mithila Kitchen",
        area="Janakpur",
        hours="7 AM - 9 PM daily",
        delivery_area="Janakpur and Ramanand Chowk",
        delivery_fee_npr=60,
        menu=(
            MenuItem("Fish Curry", 320, contains="fish, mustard oil, spices"),
            MenuItem("Dhikri", 120, contains="rice flour"),
            MenuItem("Bagiya", 100, contains="rice flour, lentils"),
            MenuItem("Malpua", 90, contains="flour, milk, sugar"),
            MenuItem("Chai", 60, contains="milk"),
        ),
    ),
    TrainingBusiness(
        id="pokhara-grill",
        name="Pokhara Grill",
        area="Lakeside, Pokhara",
        hours="11 AM - 10 PM daily",
        delivery_area="Lakeside and Baidam",
        delivery_fee_npr=90,
        menu=(
            MenuItem("Grilled Fish", 550, contains="fish, lemon, herbs"),
            MenuItem("Chicken Chilli", 380, contains="chicken, pepper, onion"),
            MenuItem("Buff Sukuti", 300, contains="buff, spices"),
            MenuItem("French Fries", 180, contains="potato"),
            MenuItem("Lemon Tea", 90),
        ),
    ),
    TrainingBusiness(
        id="lalitpur-pizza",
        name="Lalitpur Pizza",
        area="Jhamsikhel, Lalitpur",
        hours="11 AM - 9 PM daily",
        delivery_area="Jhamsikhel and Sanepa",
        delivery_fee_npr=150,
        menu=(
            MenuItem("Margherita Pizza", 550, contains="flour, cheese, tomato"),
            MenuItem("Chicken Pizza", 750, contains="flour, cheese, chicken"),
            MenuItem("Garlic Bread", 250, contains="bread, butter, garlic"),
            MenuItem("Cola", 120),
            MenuItem("Brownie", 300, contains="flour, cocoa, egg"),
        ),
    ),
    TrainingBusiness(
        id="newa-lahana",
        name="Newa Lahana",
        area="Patan",
        hours="10 AM - 8 PM daily",
        delivery_area="Patan and Mangal Bazaar",
        delivery_fee_npr=80,
        menu=(
            MenuItem("Samay Baji", 350, contains="beaten rice, buff, egg"),
            MenuItem("Chatamari", 150, contains="rice flour, egg, buff"),
            MenuItem("Bara", 80, contains="lentils"),
            MenuItem("Yomari", 120, contains="rice flour, sesame"),
            MenuItem("Chiya", 70, contains="milk"),
        ),
    ),
)


Family = GenerationFamily

FAMILIES: tuple[Family, ...] = (
    Family("greet", "greet", "a greeting to the restaurant (hello, namaste, good morning)"),
    Family("thanks", "thanks", "thanking the restaurant (thank you, dhanyabad)"),
    Family("goodbye", "goodbye", "saying goodbye or ending the conversation (bye, see you)"),
    Family("show_menu", "menu", "asking to see the menu or what the restaurant has", confusable="greet"),
    Family("recommend", "recommend", "asking for a recommendation or the best seller", confusable="menu"),
    Family(
        "query_price",
        "price",
        "asking how much a specific menu item costs",
        query_field="price",
        mentions_item=True,
    ),
    Family(
        "query_availability",
        "availability",
        "asking whether a specific menu item is available",
        query_field="availability",
        mentions_item=True,
    ),
    Family(
        "query_details",
        "details",
        "asking what a specific menu item contains or is made of",
        query_field="details",
        mentions_item=True,
    ),
    Family("ask_hours", "hours", "asking about the restaurant's opening hours", confusable="menu"),
    Family(
        "ask_delivery",
        "delivery",
        "asking about the delivery area, fee or time",
        confusable="order_status",
    ),
    Family("order_status", "order_status", "asking about the status of an existing order", confusable="delivery"),
    Family("view_cart", "cart", "asking to see the current cart or draft order", confusable="order_status"),
    Family("request_checkout", "checkout", "asking to place or check out the current order", confusable="cart"),
    Family("repeat_order", "repeat_order", "asking to repeat a previous order", confusable="checkout"),
    Family(
        "use_saved_address",
        "saved_address",
        "asking to use a saved delivery address",
        confusable="delivery",
    ),
    Family(
        "bare_order",
        "none",
        "a bare order attempt without quantity or confirmation (like 'momos please')",
        order_intent=True,
        abstain=True,
        confusable="checkout",
        mentions_item=True,
    ),
    Family(
        "yes_no",
        "none",
        "a plain yes or no answer to a previous question",
        abstain=True,
        confusable="thanks",
    ),
    Family(
        "allergy",
        "none",
        "asking whether an item contains an allergen or specific ingredient (nuts, dairy, gluten)",
        needs_staff=True,
        abstain=True,
        confusable="details",
    ),
    Family(
        "refund",
        "none",
        "asking for a refund or complaining about a payment",
        needs_staff=True,
        abstain=True,
        confusable="order_status",
    ),
    Family(
        "complaint",
        "none",
        "complaining that the food was cold, wrong or late",
        needs_staff=True,
        abstain=True,
        confusable="order_status",
    ),
    Family(
        "refund_status",
        "none",
        "asking when a refund will arrive or why it is still pending",
        needs_staff=True,
        abstain=True,
        confusable="order_status",
    ),
    Family(
        "late_delivery",
        "none",
        "complaining that the order arrived late or took far longer than promised",
        needs_staff=True,
        abstain=True,
        confusable="order_status",
    ),
    Family(
        "unclear_repeat",
        "none",
        "an unfinished or unclear follow-up that only hints at asking again, "
        "without a clear repeat-order request",
        abstain=True,
        confusable="repeat_order",
    ),
    Family(
        "human",
        "none",
        "asking to talk to a staff member (people say 'staff sanga kura' / 'स्टाफसँग कुरा', "
        "not 'manche' or 'human' sanga kura); also asking whether the manager or owner is "
        "present or available (म्यानेजर, साहुजी, owner)",
        needs_staff=True,
        abstain=True,
        confusable="greet",
    ),
    Family(
        "gibberish",
        "none",
        "keyboard gibberish or symbols with no meaning",
        abstain=True,
        confusable="greet",
    ),
    Family(
        "unclear",
        "none",
        "an unclear or off-topic message that does not express any request",
        abstain=True,
        confusable="greet",
    ),
)

FAMILY_BY_ID = {family.id: family for family in FAMILIES}


def build_prompt(business: TrainingBusiness, family: Family, language: str, variant: int = 0) -> str:
    menu_lines = "\n".join(
        f"- {item.name} (NPR {item.price_npr})" + (f", contains {item.contains}" if item.contains else "")
        for item in business.menu
    )
    rules = prompt_rules(
        family,
        audience="restaurant",
        item_word="item",
        list_word="menu",
        register_line="Natural, the way real customers type; 2 to 15 words.",
        variant=variant,
    )
    return (
        "You write realistic WhatsApp messages that customers send to a Nepali restaurant.\n"
        f"Scenario: a customer is chatting with {business.name} ({business.area}).\n"
        f"Menu the restaurant serves:\n{menu_lines}\n\n"
        f"Intent to express: {family.instruction}.\n"
        f"The customer writes one short message in {LANGUAGE_INSTRUCTIONS[language]}.\n"
        "Rules:\n" + "\n".join(rules)
    )


SPEC = GenerationSpec(
    workflow=GENERATOR_WORKFLOW,
    command_criteria=COMMAND_CRITERIA,
    query_fields=QUERY_FIELDS,
    query_field_descriptions=QUERY_FIELD_DESCRIPTIONS,
    questions=ne_questions,
    build_prompt=build_prompt,
)


def build_plan(
    *,
    businesses: Sequence[TrainingBusiness] = TRAINING_BUSINESSES,
    families: Sequence[Family] = FAMILIES,
    languages: Sequence[str] = LANGUAGES,
    variants: int = 1,
    limit: int | None = None,
    kind_cases: int | None = None,
    safety_cases: int | None = None,
    id_prefix: str = "ne-gen",
) -> list[GenerationTask]:
    """Plan generation tasks.

    Budget mode (``kind_cases``/``safety_cases``) gives every command-kind
    family the same number of cases and every safety/abstain family another,
    cycling businesses and languages; legacy mode multiplies families by
    languages, businesses and ``variants``. ``id_prefix`` keeps ids unique
    across batches so dataset revisions never collide.
    """
    if kind_cases is not None or safety_cases is not None:
        return build_budget_plan(
            SPEC,
            businesses=businesses,
            families=families,
            languages=languages,
            kind_cases=kind_cases or 0,
            safety_cases=safety_cases or 0,
            limit=limit,
            id_prefix=id_prefix,
        )
    return build_variant_plan(
        SPEC,
        businesses=businesses,
        families=families,
        languages=languages,
        variants=variants,
        limit=limit,
        id_prefix=id_prefix,
    )


def derive_gold(family: Family, rng: random.Random) -> dict[str, Gold]:
    return _derive_gold(SPEC, family, rng)


def build_case(task: GenerationTask, message: str, rng: random.Random, *, generator: str) -> Case:
    return _build_case(SPEC, task, message, rng, generator=generator)
