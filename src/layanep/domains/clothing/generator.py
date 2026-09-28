"""Training templates for clothing businesses: products, families, prompts, and gold.

Mirrors the restaurant generator on the shared ``generation_core`` engine.
Benchmark products are held out from generation; the training states use
fictional businesses. Gold is constructed from the family that requested the
message, not sampled.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Sequence

from .questions import (
    CLOTHING_COMMAND_CRITERIA,
    CLOTHING_QUERY_FIELD_DESCRIPTIONS,
    CLOTHING_QUERY_FIELDS,
    clothing_questions,
)
from ...generation_core import (
    GenerationFamily,
    GenerationSpec,
    GenerationTask,
    build_budget_plan,
    build_case as _build_case,
    derive_gold as _derive_gold,
    prompt_rules,
)
from ...schema import Case, Gold

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

Family = GenerationFamily

FAMILIES: tuple[Family, ...] = (
    # --- social ---
    Family("greet", "greet", "a greeting to the store (hello, namaste, good morning)"),
    Family("thanks", "thanks", "thanking the store (thank you, dhanyabad)"),
    Family("goodbye", "goodbye", "saying goodbye or ending the conversation (bye, see you)"),
    # --- discovery ---
    Family("show_catalog", "catalog", "asking to see products, new arrivals or the catalog", confusable="greet"),
    Family("recommend", "recommend", "asking for a recommendation, best seller or trending item", confusable="catalog"),
    Family(
        "query_price", "price",
        "asking how much a specific product costs",
        query_field="price", mentions_item=True,
    ),
    Family(
        "query_size", "size",
        "asking about available sizes or requesting a size chart for a product",
        query_field="size", mentions_item=True, confusable="stock",
    ),
    Family(
        "query_color", "color",
        "asking about available colors for a product",
        query_field="color", mentions_item=True, confusable="size",
    ),
    Family(
        "query_material", "material",
        "asking what fabric or material a product is made of",
        query_field="material", mentions_item=True, confusable="stock",
    ),
    Family(
        "query_stock", "stock",
        "asking whether a product is available or in stock (without asking about a specific size or color)",
        query_field="stock", mentions_item=True, confusable="size",
    ),
    # --- fulfillment ---
    Family(
        "ask_delivery", "delivery",
        "asking about the delivery area, fee or time",
        confusable="cod",
    ),
    Family(
        "ask_cod", "cod",
        "asking whether cash on delivery is available or accepted",
        confusable="delivery",
    ),
    Family(
        "order_status", "order_status",
        "asking about the status of an existing order",
        confusable="delivery",
    ),
    # --- ordering ---
    Family("view_cart", "cart", "asking to see the current cart or order", confusable="order_status"),
    Family("request_checkout", "checkout", "asking to place an order or buy a product", confusable="cart"),
    Family(
        "request_exchange", "exchange",
        "asking to exchange or return an item (wrong size, wrong color, defective)",
        order_intent=True, confusable="order_status",
    ),
    Family(
        "custom_order", "custom_order",
        "asking for custom stitching, tailoring or alteration of a garment",
        order_intent=True, confusable="checkout",
    ),
    Family(
        "use_saved_address", "saved_address",
        "asking to use a saved delivery address",
        confusable="delivery",
    ),
    # --- safety / abstain ---
    Family(
        "bare_order", "none",
        "a bare purchase attempt without size or confirmation (like 'yo chaiyo')",
        order_intent=True, abstain=True, confusable="checkout", mentions_item=True,
    ),
    Family(
        "yes_no", "none",
        "a plain yes or no answer to a previous question",
        abstain=True, confusable="thanks",
    ),
    Family(
        "skin_sensitivity", "none",
        "asking whether fabric will irritate skin or cause an allergy (sensitive skin, rash, itching)",
        needs_staff=True, abstain=True, confusable="material",
    ),
    Family(
        "counterfeit_concern", "none",
        "questioning whether a product is genuine, original or branded (copy, duplicate, fake)",
        needs_staff=True, abstain=True, confusable="material",
    ),
    Family(
        "sizing_dispute", "none",
        "complaining that a received item does not fit the stated size",
        needs_staff=True, abstain=True, confusable="exchange",
    ),
    Family(
        "refund_demand", "none",
        "demanding a refund or complaining about a payment",
        needs_staff=True, abstain=True, confusable="exchange",
    ),
    Family(
        "complaint", "none",
        "complaining that the product was damaged, wrong or delivered late",
        needs_staff=True, abstain=True, confusable="order_status",
    ),
    Family(
        "human", "none",
        "asking to talk to a staff member or the owner",
        needs_staff=True, abstain=True, confusable="greet",
    ),
    Family(
        "gibberish", "none",
        "keyboard gibberish or symbols with no meaning",
        abstain=True, confusable="greet",
    ),
    Family(
        "unclear", "none",
        "an unclear or off-topic message that does not express any request",
        abstain=True, confusable="greet",
    ),
)

FAMILY_BY_ID = {family.id: family for family in FAMILIES}

# Backwards-compatible aliases: both domains now share the engine types.
ClothingFamily = GenerationFamily
ClothingGenerationTask = GenerationTask


# ---------------------------------------------------------------------------
# Prompt and gold builders
# ---------------------------------------------------------------------------

def build_prompt(business: ClothingBusiness, family: Family, language: str, variant: int = 0) -> str:
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

    rules = prompt_rules(
        family,
        audience="store",
        item_word="product",
        list_word="catalog",
        register_line="Natural, the way real customers type on WhatsApp/Instagram; 2 to 15 words.",
        variant=variant,
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


SPEC = GenerationSpec(
    workflow=GENERATOR_WORKFLOW,
    command_criteria=CLOTHING_COMMAND_CRITERIA,
    query_fields=CLOTHING_QUERY_FIELDS,
    query_field_descriptions=CLOTHING_QUERY_FIELD_DESCRIPTIONS,
    questions=clothing_questions,
    build_prompt=build_prompt,
)


def build_plan(
    *,
    businesses: Sequence[ClothingBusiness] = TRAINING_BUSINESSES,
    families: Sequence[Family] = FAMILIES,
    languages: Sequence[str] = LANGUAGES,
    kind_cases: int | None = None,
    safety_cases: int | None = None,
    limit: int | None = None,
    id_prefix: str = "cl-gen",
) -> list[GenerationTask]:
    """Plan clothing generation tasks (budget mode only)."""
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


def derive_gold(family: Family, rng: random.Random) -> dict[str, Gold]:
    return _derive_gold(SPEC, family, rng)


def build_case(task: GenerationTask, message: str, rng: random.Random, *, generator: str) -> Case:
    return _build_case(SPEC, task, message, rng, generator=generator)
