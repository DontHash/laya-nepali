"""Training templates for clothing businesses: products, families, prompts, and gold.

Mirrors ``templates.py`` (restaurant domain).  Benchmark products are held out
from generation; the training states use fictional businesses.  Gold is
constructed from the family that requested the message, not sampled.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Sequence

from .clothing_questions import (
    CLOTHING_COMMAND_CRITERIA,
    CLOTHING_QUERY_FIELD_DESCRIPTIONS,
    CLOTHING_QUERY_FIELDS,
    clothing_questions,
)
from .reference import REGISTER_RULES
from .schema import ABSTAIN_KEY, Case, Gold

GENERATOR_WORKFLOW = "clothing_command_lu"
LANGUAGES = ("ne", "ne-rom", "en")

LANGUAGE_INSTRUCTIONS = {
    "ne": "Nepali in Devanagari script",
    "ne-rom": "Nepali typed in Latin script (Romanized Nepali, the way people type without a Nepali keyboard)",
    "en": "English (Nepali clothing words allowed)",
}


@dataclass(frozen=True)
class Product:
    name: str
    price_npr: int
    sizes: tuple[str, ...] = ("free",)
    colors: tuple[str, ...] = ()
    material: str = ""
    in_stock: bool = True

    def to_state(self) -> dict:
        item: dict = {"name": self.name, "price_npr": self.price_npr, "in_stock": self.in_stock}
        if self.sizes:
            item["sizes"] = list(self.sizes)
        if self.colors:
            item["colors"] = list(self.colors)
        if self.material:
            item["material"] = self.material
        return item


@dataclass(frozen=True)
class ClothingBusiness:
    id: str
    name: str
    area: str
    hours: str
    delivery_area: str
    delivery_fee_npr: int
    cod_available: bool
    catalog: tuple[Product, ...]

    def state_base(self) -> dict:
        return {
            "business": {
                "name": self.name,
                "area": self.area,
                "hours": self.hours,
                "delivery_area": self.delivery_area,
                "delivery_fee_npr": self.delivery_fee_npr,
                "cod_available": self.cod_available,
            },
            "catalog": [item.to_state() for item in self.catalog],
        }


TRAINING_BUSINESSES: tuple[ClothingBusiness, ...] = (
    ClothingBusiness(
        id="thamel-threads",
        name="Thamel Threads",
        area="Thamel, Kathmandu",
        hours="10 AM - 8 PM daily",
        delivery_area="Kathmandu Valley",
        delivery_fee_npr=150,
        cod_available=True,
        catalog=(
            Product("Cotton Kurta", 1800, sizes=("S", "M", "L", "XL"), colors=("white", "blue", "black"), material="cotton"),
            Product("Denim Jeans", 2500, sizes=("28", "30", "32", "34"), colors=("blue", "black"), material="denim"),
            Product("Pashmina Shawl", 3500, sizes=("free",), colors=("red", "maroon", "grey"), material="pashmina wool"),
            Product("T-Shirt", 800, sizes=("S", "M", "L", "XL", "XXL"), colors=("white", "black", "navy"), material="cotton blend"),
        ),
    ),
    ClothingBusiness(
        id="pokhara-boutique",
        name="Pokhara Style Boutique",
        area="Lakeside, Pokhara",
        hours="10 AM - 7 PM (closed Saturdays)",
        delivery_area="Pokhara and Lekhnath",
        delivery_fee_npr=100,
        cod_available=True,
        catalog=(
            Product("Dhaka Topi", 450, sizes=("M", "L"), colors=("traditional",), material="dhaka cotton"),
            Product("Daura Suruwal", 4500, sizes=("S", "M", "L", "XL"), colors=("white", "cream"), material="cotton silk"),
            Product("Gunyu Cholo", 5500, sizes=("S", "M", "L"), colors=("red", "maroon", "green"), material="silk"),
            Product("Cotton Saree", 3200, sizes=("free",), colors=("red", "blue", "green", "yellow"), material="cotton"),
        ),
    ),
    ClothingBusiness(
        id="bhaktapur-stitch",
        name="Bhaktapur Custom Stitch",
        area="Bhaktapur",
        hours="9 AM - 6 PM daily",
        delivery_area="Bhaktapur and Thimi",
        delivery_fee_npr=80,
        cod_available=False,
        catalog=(
            Product("Custom Kurti", 2200, sizes=("custom",), colors=("any",), material="cotton/silk"),
            Product("Blouse Stitching", 1500, sizes=("custom",), colors=("any",), material="cotton"),
            Product("Salwar Set", 3000, sizes=("custom",), colors=("any",), material="cotton blend"),
        ),
    ),
    ClothingBusiness(
        id="birgunj-saree",
        name="Birgunj Saree House",
        area="Birgunj",
        hours="9 AM - 7 PM daily",
        delivery_area="Birgunj and Parsa",
        delivery_fee_npr=60,
        cod_available=True,
        catalog=(
            Product("Banarasi Saree", 8500, sizes=("free",), colors=("red", "gold", "green"), material="silk"),
            Product("Chiffon Saree", 3200, sizes=("free",), colors=("pink", "blue", "peach"), material="chiffon"),
            Product("Cotton Saree", 1800, sizes=("free",), colors=("white", "yellow", "blue"), material="cotton"),
            Product("Blouse Piece", 500, sizes=("free",), colors=("matching",), material="silk/cotton"),
        ),
    ),
    ClothingBusiness(
        id="lalitpur-kids",
        name="Little Lalitpur Kids Wear",
        area="Jhamsikhel, Lalitpur",
        hours="10 AM - 6 PM (closed Sundays)",
        delivery_area="Lalitpur and Patan",
        delivery_fee_npr=100,
        cod_available=True,
        catalog=(
            Product("Kids T-Shirt", 500, sizes=("2Y", "4Y", "6Y", "8Y"), colors=("red", "blue", "yellow"), material="cotton"),
            Product("Kids Jeans", 900, sizes=("2Y", "4Y", "6Y", "8Y"), colors=("blue", "black"), material="denim"),
            Product("School Uniform Set", 1200, sizes=("4Y", "6Y", "8Y", "10Y"), colors=("white/navy",), material="polyester blend"),
            Product("Baby Romper", 650, sizes=("0-6M", "6-12M", "12-18M"), colors=("pink", "blue", "white"), material="cotton"),
        ),
    ),
    ClothingBusiness(
        id="chitwan-sports",
        name="Chitwan Sports Corner",
        area="Bharatpur, Chitwan",
        hours="8 AM - 8 PM daily",
        delivery_area="Bharatpur and Ratnanagar",
        delivery_fee_npr=80,
        cod_available=True,
        catalog=(
            Product("Track Pants", 1200, sizes=("S", "M", "L", "XL", "XXL"), colors=("black", "grey", "navy"), material="polyester"),
            Product("Sports T-Shirt", 900, sizes=("S", "M", "L", "XL"), colors=("white", "red", "blue"), material="dry-fit"),
            Product("Running Shoes", 3500, sizes=("7", "8", "9", "10", "11"), colors=("black", "white"), material="mesh/rubber"),
            Product("Yoga Pants", 1500, sizes=("S", "M", "L"), colors=("black", "grey"), material="spandex blend"),
        ),
    ),
    ClothingBusiness(
        id="biratnagar-fashion",
        name="Biratnagar Fashion Hub",
        area="Biratnagar",
        hours="10 AM - 8 PM daily",
        delivery_area="Biratnagar and Dharan",
        delivery_fee_npr=120,
        cod_available=True,
        catalog=(
            Product("Men's Formal Shirt", 1800, sizes=("38", "40", "42", "44"), colors=("white", "blue", "pink"), material="cotton"),
            Product("Formal Trousers", 2200, sizes=("30", "32", "34", "36"), colors=("black", "grey", "navy"), material="polyester blend"),
            Product("Ladies Kurti", 1500, sizes=("S", "M", "L", "XL"), colors=("red", "green", "blue", "yellow"), material="rayon"),
            Product("Jacket", 3500, sizes=("M", "L", "XL", "XXL"), colors=("black", "brown", "olive"), material="polyester/nylon"),
        ),
    ),
    ClothingBusiness(
        id="newari-heritage",
        name="Newa Heritage Clothing",
        area="Patan, Lalitpur",
        hours="10 AM - 6 PM (closed Saturdays)",
        delivery_area="Patan and Mangal Bazaar",
        delivery_fee_npr=80,
        cod_available=False,
        catalog=(
            Product("Haku Patasi", 6500, sizes=("S", "M", "L"), colors=("black/red",), material="handloom cotton"),
            Product("Tapalan", 4500, sizes=("free",), colors=("red", "maroon"), material="handloom"),
            Product("Bhoto", 3500, sizes=("S", "M", "L", "XL"), colors=("gold", "red"), material="brocade"),
            Product("Newari Topi", 800, sizes=("M", "L"), colors=("traditional",), material="cotton"),
        ),
    ),
)


# ---------------------------------------------------------------------------
# Intent families — one per intended outcome
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ClothingFamily:
    """One intended intent for the clothing domain."""

    id: str
    command: str
    instruction: str
    query_field: str = ABSTAIN_KEY
    order_intent: bool = False
    needs_staff: bool = False
    abstain: bool = False
    confusable: str | None = None
    mentions_product: bool = False


FAMILIES: tuple[ClothingFamily, ...] = (
    # --- social ---
    ClothingFamily("greet", "greet", "a greeting to the store (hello, namaste, good morning)"),
    ClothingFamily("thanks", "thanks", "thanking the store (thank you, dhanyabad)"),
    ClothingFamily("goodbye", "goodbye", "saying goodbye or ending the conversation (bye, see you)"),
    # --- discovery ---
    ClothingFamily("show_catalog", "catalog", "asking to see products, new arrivals or the catalog", confusable="greet"),
    ClothingFamily("recommend", "recommend", "asking for a recommendation, best seller or trending item", confusable="catalog"),
    ClothingFamily(
        "query_price", "price",
        "asking how much a specific product costs",
        query_field="price", mentions_product=True,
    ),
    ClothingFamily(
        "query_size", "size",
        "asking about available sizes or requesting a size chart for a product",
        query_field="size", mentions_product=True, confusable="stock",
    ),
    ClothingFamily(
        "query_color", "color",
        "asking about available colors for a product",
        query_field="color", mentions_product=True, confusable="size",
    ),
    ClothingFamily(
        "query_material", "material",
        "asking what fabric or material a product is made of",
        query_field="material", mentions_product=True, confusable="stock",
    ),
    ClothingFamily(
        "query_stock", "stock",
        "asking whether a product is available or in stock (without asking about a specific size or color)",
        query_field="stock", mentions_product=True, confusable="size",
    ),
    # --- fulfillment ---
    ClothingFamily(
        "ask_delivery", "delivery",
        "asking about the delivery area, fee or time",
        confusable="cod",
    ),
    ClothingFamily(
        "ask_cod", "cod",
        "asking whether cash on delivery is available or accepted",
        confusable="delivery",
    ),
    ClothingFamily(
        "order_status", "order_status",
        "asking about the status of an existing order",
        confusable="delivery",
    ),
    # --- ordering ---
    ClothingFamily("view_cart", "cart", "asking to see the current cart or order", confusable="order_status"),
    ClothingFamily("request_checkout", "checkout", "asking to place an order or buy a product", confusable="cart"),
    ClothingFamily(
        "request_exchange", "exchange",
        "asking to exchange or return an item (wrong size, wrong color, defective)",
        order_intent=True, confusable="order_status",
    ),
    ClothingFamily(
        "custom_order", "custom_order",
        "asking for custom stitching, tailoring or alteration of a garment",
        order_intent=True, confusable="checkout",
    ),
    ClothingFamily(
        "use_saved_address", "saved_address",
        "asking to use a saved delivery address",
        confusable="delivery",
    ),
    # --- safety / abstain ---
    ClothingFamily(
        "bare_order", "none",
        "a bare purchase attempt without size or confirmation (like 'yo chaiyo')",
        order_intent=True, abstain=True, confusable="checkout", mentions_product=True,
    ),
    ClothingFamily(
        "yes_no", "none",
        "a plain yes or no answer to a previous question",
        abstain=True, confusable="thanks",
    ),
    ClothingFamily(
        "skin_sensitivity", "none",
        "asking whether fabric will irritate skin or cause an allergy (sensitive skin, rash, itching)",
        needs_staff=True, abstain=True, confusable="material",
    ),
    ClothingFamily(
        "counterfeit_concern", "none",
        "questioning whether a product is genuine, original or branded (copy, duplicate, fake)",
        needs_staff=True, abstain=True, confusable="material",
    ),
    ClothingFamily(
        "sizing_dispute", "none",
        "complaining that a received item does not fit the stated size",
        needs_staff=True, abstain=True, confusable="exchange",
    ),
    ClothingFamily(
        "refund_demand", "none",
        "demanding a refund or complaining about a payment",
        needs_staff=True, abstain=True, confusable="exchange",
    ),
    ClothingFamily(
        "complaint", "none",
        "complaining that the product was damaged, wrong or delivered late",
        needs_staff=True, abstain=True, confusable="order_status",
    ),
    ClothingFamily(
        "human", "none",
        "asking to talk to a staff member or the owner",
        needs_staff=True, abstain=True, confusable="greet",
    ),
    ClothingFamily(
        "gibberish", "none",
        "keyboard gibberish or symbols with no meaning",
        abstain=True, confusable="greet",
    ),
    ClothingFamily(
        "unclear", "none",
        "an unclear or off-topic message that does not express any request",
        abstain=True, confusable="greet",
    ),
)

FAMILY_BY_ID = {family.id: family for family in FAMILIES}


# ---------------------------------------------------------------------------
# Prompt and gold builders
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ClothingGenerationTask:
    id: str
    family: ClothingFamily
    language: str
    business: ClothingBusiness
    variant: int
    prompt: str


def build_prompt(business: ClothingBusiness, family: ClothingFamily, language: str, variant: int = 0) -> str:
    catalog_lines = []
    for item in business.catalog:
        line = f"- {item.name} (NPR {item.price_npr})"
        if item.sizes and item.sizes != ("free",):
            line += f", sizes: {', '.join(item.sizes)}"
        if item.colors:
            line += f", colors: {', '.join(item.colors)}"
        if item.material:
            line += f", material: {item.material}"
        catalog_lines.append(line)
    catalog_text = "\n".join(catalog_lines)

    rules = [
        "- The customer is writing to the store; never write as the store.",
        "- Express exactly one intent and nothing else; do not add a second request or order.",
        "- Do not put the store's name in the message.",
    ]
    if family.mentions_product:
        rules.append("- Name one specific product from the catalog.")
    if variant:
        rules.append(f"- Variation {variant + 1}: use a clearly different wording, length and tone.")
    rules.extend(
        ["- " + rule for rule in REGISTER_RULES[:-1]]
        + [
            "- Natural, the way real customers type on WhatsApp/Instagram; 2 to 15 words.",
            "- No names, phone numbers, addresses, emails, URLs, emojis or line breaks.",
            "- Return only the message text, with no quotes and no explanation.",
        ]
    )
    cod_note = " COD available." if business.cod_available else " No COD (online payment only)."
    return (
        "You write realistic WhatsApp/Instagram messages that customers send to a Nepali clothing store.\n"
        f"Scenario: a customer is chatting with {business.name} ({business.area}).{cod_note}\n"
        f"Products the store sells:\n{catalog_text}\n\n"
        f"Intent to express: {family.instruction}.\n"
        f"The customer writes one short message in {LANGUAGE_INSTRUCTIONS[language]}.\n"
        "Rules:\n" + "\n".join(rules)
    )


def build_plan(
    *,
    businesses: Sequence[ClothingBusiness] = TRAINING_BUSINESSES,
    families: Sequence[ClothingFamily] = FAMILIES,
    languages: Sequence[str] = LANGUAGES,
    kind_cases: int | None = None,
    safety_cases: int | None = None,
    limit: int | None = None,
    id_prefix: str = "cl-gen",
) -> list[ClothingGenerationTask]:
    """Plan clothing generation tasks (budget mode only)."""
    combos = [(business, language) for language in languages for business in businesses]
    tasks: list[ClothingGenerationTask] = []
    if not combos:
        return tasks
    kc = kind_cases or 0
    sc = safety_cases or 0
    max_budget = max(kc, sc)
    for index in range(max_budget):
        for position, family in enumerate(families):
            budget = kc if family.command != ABSTAIN_KEY else sc
            if index >= budget:
                continue
            combo_index = index + position
            business, language = combos[combo_index % len(combos)]
            variant = combo_index // len(combos)
            tasks.append(
                ClothingGenerationTask(
                    id=f"{id_prefix}-{len(tasks) + 1:04d}",
                    family=family,
                    language=language,
                    business=business,
                    variant=variant,
                    prompt=build_prompt(business, family, language, variant),
                )
            )
            if limit is not None and len(tasks) >= limit:
                return tasks
    return tasks


def _categorical(rng: random.Random, keys: Sequence[str], primary: str, low: float, high: float) -> dict[str, float]:
    probability = rng.uniform(low, high)
    rest = (1.0 - probability) / (len(keys) - 1)
    distribution = {key: (probability if key == primary else rest) for key in keys}
    total = sum(distribution.values())
    return {key: round(value / total, 6) for key, value in distribution.items()}


def _command_distribution(rng: random.Random, family: ClothingFamily) -> dict[str, float]:
    """Soft command targets, with no mass on ``none`` for command families.

    Mirrors the restaurant template logic: kind messages are commands by
    definition, so residual probability must not leak onto the abstain key.
    """
    keys = list(CLOTHING_COMMAND_CRITERIA)
    distribution = dict.fromkeys(keys, 0.0)
    distribution[family.command] = rng.uniform(0.88, 0.95)
    rest = 1.0 - distribution[family.command]
    if family.command == ABSTAIN_KEY:
        secondary = family.confusable or "greet"
        distribution[secondary] += rest
    elif family.command in CLOTHING_QUERY_FIELDS:
        others = [other for other in CLOTHING_QUERY_FIELDS if other != family.command]
        for other in others:
            distribution[other] = rest / len(others)
    elif family.confusable:
        distribution[family.confusable] += rest
    else:
        others = [key for key in keys if key not in (family.command, ABSTAIN_KEY)][:3]
        for key in others:
            distribution[key] = rest / len(others)
    total = sum(distribution.values())
    return {key: round(value / total, 6) for key, value in distribution.items()}


def derive_gold(family: ClothingFamily, rng: random.Random) -> dict[str, Gold]:
    def noul(intended: bool) -> Gold:
        primary = "true" if intended else "false"
        probabilities = _categorical(rng, ("true", "false"), primary, 0.90, 0.96)
        return Gold(label=primary, probabilities=probabilities)

    return {
        "command": Gold(label=family.command, probabilities=_command_distribution(rng, family)),
        "query_field": Gold(
            label=family.query_field,
            probabilities=_categorical(
                rng, list(CLOTHING_QUERY_FIELD_DESCRIPTIONS), family.query_field, 0.86, 0.94
            ),
        ),
        "order_intent": noul(family.order_intent),
        "needs_staff": noul(family.needs_staff),
        "abstain": noul(family.abstain),
    }


def build_case(task: ClothingGenerationTask, message: str, rng: random.Random, *, generator: str) -> Case:
    state = task.business.state_base()
    state["customer_message"] = message
    state["language"] = task.language
    return Case(
        id=task.id,
        workflow=GENERATOR_WORKFLOW,
        state=state,
        questions=clothing_questions(task.business.name),
        gold=derive_gold(task.family, rng),
        provenance={
            "source": "synthetic",
            "generator": generator,
            "license": "CC-BY-4.0",
            "family": task.family.id,
            "language": task.language,
            "business": task.business.id,
            "variant": task.variant,
            "reviewed_by": None,
        },
    )
