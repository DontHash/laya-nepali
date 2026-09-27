"""Deterministic minimal-pair rows for known intent boundaries.

Kernel runs have repeatedly surfaced high-confidence confusions between
neighbouring intents (refund_status vs order_status, allergy vs details,
manager presence vs availability, unclear fragments vs menu). Batches 7 and 8
were built with throwaway scripts; this module keeps the boundary banks and
builder in the repo so every future confusion can be taught with controlled
minimal pairs in both directions.

Rows are built through ``templates.build_case`` so gold labels, probabilities
and provenance match the generator pipeline, then reviewed like any batch.
"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .templates import (
    FAMILY_BY_ID,
    TRAINING_BUSINESSES,
    GenerationTask,
    build_case,
    build_prompt,
)

DEFAULT_OUT = Path(__file__).resolve().parents[2] / "data" / "generated" / "ne-contrastive.jsonl"
DEFAULT_ID_PREFIX = "ne-ct"
GENERATOR = "deterministic:contrastive"


@dataclass(frozen=True)
class Boundary:
    """One confusable boundary: messages for a single family at a time."""

    name: str
    family_id: str
    messages: tuple[str, ...]


BOUNDARIES: tuple[Boundary, ...] = (
    Boundary(
        "menu_vs_recommend",
        "show_menu",
        (
            "मेनु देखाउनु",
            "मेनु हेर्नु छ",
            "के के छ त?",
            "मेनु हेर्न मिल्छ?",
            "के के पाइन्छ होला नि?",
            "तपाईंहरूको मेनु चाहियो",
            "मेनुको फोटो पठाउनु न",
        ),
    ),
    Boundary(
        "menu_vs_recommend",
        "recommend",
        (
            "के राम्रो हुन्छ?",
            "कुन राम्रो छ?",
            "भेस्ट सेलर कुन हो?",
            "तपाईंको सिफारिस के हो?",
            "के खाने सुझाव दिनुहुन्छ?",
            "सबैभन्दा मिठो कुन हो?",
            "नयाँ आउँदै छ, के सुझाव दिनुहुन्छ?",
        ),
    ),
    Boundary(
        "hours_vs_delivery",
        "ask_hours",
        (
            "कति बेला खुल्छ?",
            "बिहान कति बजेदेखि शुरू हुन्छ?",
            "अहिले खुलेको छ?",
            "बन्द कति बेला हुन्छ?",
            "आइतबार बन्द हुन्छ कि खुल्छ?",
            "बेलुका कति सम्म खुला हुन्छ?",
            "आज खुला छ नि?",
        ),
    ),
    Boundary(
        "hours_vs_delivery",
        "ask_delivery",
        (
            "डेलिभरी कहाँ हुन्छ?",
            "डेलिभरी चार्ज कति?",
            "कति टाढासम्म पठाउनुहुन्छ?",
            "डेलिभरी कति समयमा आउँछ?",
            "बाहिर पठाइदिनुहुन्छ?",
            "जावलाखेल पुग्छ डेलिभरी?",
            "डेलिभरी फ्री छ कि?",
        ),
    ),
    Boundary(
        "status_family",
        "order_status",
        (
            "अर्डर कहाँ छ?",
            "मेरो अर्डर कता सम्म पुग्यो?",
            "अर्डर पठाइसक्नु भयो?",
            "कति बेरमा आउँछ?",
            "मेरो अर्डर नम्बर के हो?",
            "ट्र्याक गर्न मिल्छ?",
            "अर्डर बनेको छ कि?",
        ),
    ),
    Boundary(
        "status_family",
        "refund",
        (
            "पैसा त फिर्ता गरिदिनु",
            "रिफन्ड गर्नु पर्छ",
            "रकम फिर्ता हुनुपर्छ",
            "गलत बिल आएको छ, हेर्नु न",
            "डबल कटेको पैसा फिर्ता गर्नु",
        ),
    ),
    Boundary(
        "status_family",
        "refund_status",
        (
            "रिफन्ड कति दिनमा हुन्छ?",
            "पैसा अझै आएको छैन",
            "रिफन्ड प्रोसेस भयो कि?",
            "फिर्ता कहिले हुन्छ नि?",
            "रिफन्ड पेन्डिङ देखिन्छ किन?",
            "पैसा फिर्ता भएको छ कि छैन?",
        ),
    ),
    Boundary(
        "status_family",
        "late_delivery",
        (
            "ढिलो आयो नि अर्डर",
            "कति ढिलो भयो त",
            "समयमा आएन नि",
            "अर्डर आउन धेरै ढिलो भयो",
            "एक घण्टा भयो अझै आएको छैन",
        ),
    ),
    Boundary(
        "status_family",
        "complaint",
        (
            "खाना चिसो भएर आयो",
            "गलत परेको छ अर्डर",
            "मःम पोलेको छ",
            "झोल बगेको छ",
            "पराठा काँचो छ नि",
        ),
    ),
    Boundary(
        "cart_mutations",
        "view_cart",
        (
            "कार्ट देखाउनु",
            "मेरो कार्टमा के छ?",
            "कार्ट खोल्नु न",
            "के के राखेको छु?",
            "अहिलेको अर्डर हेर्नु",
        ),
    ),
    Boundary(
        "cart_mutations",
        "request_checkout",
        (
            "अर्डर गरिदिनु",
            "अहिले अर्डर गर्नु",
            "कन्फर्म गरिदिनु",
            "चेकआउट गर्नु",
            "बिल गरिदिनु",
            "अर्डर पक्का गर्नु",
        ),
    ),
    Boundary(
        "cart_mutations",
        "repeat_order",
        (
            "अघिको जस्तै अर्डर गर्नु",
            "फेरि त्यही पठाउनु",
            "पहिलेको अर्डर दोहोर्याउनु",
            "यही अर्डर फेरि गर्नु",
            "हिजोको अर्डर फेरि",
        ),
    ),
    Boundary(
        "cart_mutations",
        "use_saved_address",
        (
            "घरको ठेगाना प्रयोग गर्नु",
            "सेव गरेको ठेगानामा पठाउनु",
            "पुरानै ठेगानामा पठाउनु",
            "घरको ठेगाना नै ठीक छ",
        ),
    ),
    Boundary(
        "social_vs_none",
        "greet",
        (
            "नमस्ते दाजु",
            "नमस्कार हजुर है",
            "हेलो दाइ",
            "दाइ नमस्ते",
            "शुभ बिहानी",
            "नमस्ते नि दाइ",
        ),
    ),
    Boundary(
        "social_vs_none",
        "thanks",
        (
            "धन्यवाद हजुर",
            "धन्यवाद दाइ",
            "एकदमै धन्यवाद",
            "सहयोगको लागि धन्यवाद",
        ),
    ),
    Boundary(
        "social_vs_none",
        "goodbye",
        (
            "बिदा दाइ",
            "अनि भेटौंला",
            "ठीक छ, बिदा",
            "ल त जाउँ है",
        ),
    ),
    Boundary(
        "social_vs_none",
        "yes_no",
        (
            "हुन्छ हुन्छ",
            "हो नि",
            "ठीक छ",
            "होइन",
            "पर्दैन हजुर",
            "ठीक छ दाइ",
        ),
    ),
    Boundary(
        "social_vs_none",
        "gibberish",
        (
            "ख्ख्ख्ख",
            "हाहाहा",
            "नननन",
            "ज्ज्ज",
        ),
    ),
    Boundary(
        "human_vs_availability",
        "human",
        (
            "स्टाफ छ कि?",
            "कर्मचारी हुनुहुन्छ?",
            "साहुजी हुनुहुन्छ कि?",
            "म्यानेजर छ कि नाई?",
            "म्यानेजरलाई बोलाउनु",
        ),
    ),
    Boundary(
        "unclear_vs_discovery",
        "unclear",
        (
            "त्यो के रैछ?",
            "कता गयो त?",
            "को हौ है?",
            "के भन्न खोज्नु भएको?",
            "होइन कि नाई?",
            "अनि भने नि?",
            "यो किन?",
        ),
    ),
    Boundary(
        "unclear_vs_discovery",
        "show_menu",
        (
            "तपाईंहरुको मेनु छ?",
        ),
    ),
    Boundary(
        "unclear_vs_discovery",
        "ask_delivery",
        (
            "कता पुग्छ डेलिभरी?",
        ),
    ),
    Boundary(
        "bare_order_vs_checkout",
        "bare_order",
        (
            "मोमो",
            "चिया",
            "थाली प्लिज",
            "एक मःम",
            "पिज्जा मात्र",
        ),
    ),
    Boundary(
        "bare_order_vs_checkout",
        "request_checkout",
        (
            "मोमो अर्डर गरिदिनु",
            "चिया थपेर अर्डर गर्नु",
            "थाली अर्डर गर्नु",
            "पिज्जा कन्फर्म गर्नु",
        ),
    ),
    Boundary(
        "allergy_statement",
        "allergy",
        (
            "मलाई बदामले एलर्जी छ",
            "मलाई बदामले एलर्जी छ, के खानु हुन्छ?",
            "मलाई दूधले एलर्जी छ",
            "मलाई दूधले एलर्जी छ, कुन ठीक होला?",
            "बदामले एलर्जी छ मलाई",
            "मलाई एलर्जी छ बदामले",
            "मलाई दूध हुँदैन, एलर्जी छ",
            "ग्लुटेनले एलर्जी छ मलाई",
            "मलाई अण्डाले एलर्जी छ, कुन ठीक होला?",
            "दूधले समस्या हुन्छ मलाई",
            "बदाम खान मिल्छ मलाई?",
            "मलाई एलर्जी छ, के खान सक्छु?",
            "अण्डाले एलर्जी छ, के खान मिल्छ नि?",
        ),
    ),
    Boundary(
        "allergy_statement",
        "recommend",
        (
            "के राम्रो हुन्छ नि मलाई?",
            "मलाई के खान सुझाव दिनुहुन्छ?",
            "कुन परिकार राम्रो होला?",
            "नयाँ के खानु राम्रो होला?",
            "कुन खाना राम्रो छ?",
            "तपाईंको फेभरिट कुन हो?",
        ),
    ),
    Boundary(
        "lateness_shapes",
        "late_delivery",
        (
            "अर्डर एक घण्टापछि पो आयो",
            "अर्डर एक घण्टा लगाएर आयो",
            "खाना ढिलो आयो नि",
            "एक घण्टा लगायो अर्डर आउन",
            "धेरै बेर पो लाग्यो",
            "कति बेर लगाउनु भयो त",
            "अर्डर आउँदा धेरै ढिलो भयो",
            "समयमा आएन खाना",
            "ढिलो गरेर आयो",
        ),
    ),
    Boundary(
        "lateness_shapes",
        "order_status",
        (
            "अर्डर कति बेरमा आउँछ?",
            "अर्डर आउन अझै कति बेर?",
            "कति बेर पर्छ अर्डर आउन?",
            "अर्डर कहाँ सम्म पुग्यो नि?",
        ),
    ),
    Boundary(
        "repeat_language",
        "unclear_repeat",
        (
            "फेरि भन्नु त",
            "फेरि भन्नु न दाइ",
            "दोहोर्याउनु न",
            "फेरि भन त",
            "फेरि भन्नुस् न",
            "फेरि भनिदिनु न",
        ),
    ),
    Boundary(
        "repeat_language",
        "repeat_order",
        (
            "फेरि त्यही अर्डर गरिदिनु",
            "अघिको अर्डर दोहोर्याइदिनु",
            "फेरि अर्डर गरिदिनु",
            "उही अर्डर फेरि",
        ),
    ),
    Boundary(
        "cart_shapes",
        "view_cart",
        (
            "कार्ट हेर्नु न",
            "मेरो कार्ट हेर्नु न",
            "कार्ट खोल्नु न दाइ",
            "अहिले कार्टमा के छ?",
        ),
    ),
    Boundary(
        "cart_shapes",
        "request_checkout",
        (
            "अहिले नै अर्डर गरिदिनु",
            "कन्फर्म गरेर पठाउनु",
        ),
    ),
    Boundary(
        "cart_shapes",
        "order_status",
        (
            "अर्डर कहाँ पुग्यो नि?",
        ),
    ),
    Boundary(
        "allergy_negatives",
        "allergy",
        (
            "कुन परिकारमा दूध हुँदैन?",
            "कुन परिकारमा बदाम हुँदैन?",
            "चियामा ल्याक्टोज हुन्छ कि?",
            "ल्याक्टोज नभएको खाना कुन हो?",
            "दूध नभएको परिकार कुन छ?",
            "कुन परिकारमा अण्डा छैन?",
            "ग्लुटेन नभएको के पाइन्छ?",
            "बदाम नहाल्ने खाना कुन?",
            "दूध पर्दैन मलाई, कुन ठीक हो?",
            "ल्याक्टोज छ कि छैन कसरी थाहा हुन्छ?",
        ),
    ),
    Boundary(
        "allergy_negatives",
        "query_details",
        (
            "कुन खानामा के पर्छ?",
            "कुन परिकारमा के हालिन्छ?",
            "चियामा के के हुन्छ?",
            "थालीमा के के हालिन्छ?",
            "मःमभित्र के हुन्छ?",
            "पराठामा के हालिन्छ?",
        ),
    ),
    Boundary(
        "same_order_vs_repeat",
        "request_checkout",
        (
            "यही अर्डर पठाउनु",
            "यो अर्डर अगाडि बढाउनु",
            "हालको अर्डर कन्फर्म गर्नु",
            "यो अर्डर पक्का गरिदिनु",
            "अहिलेको अर्डर पठाउनु",
        ),
    ),
    Boundary(
        "same_order_vs_repeat",
        "repeat_order",
        (
            "अघिल्लो पटक जस्तै पठाउनु",
            "हिजोको जस्तै अर्डर दिनु",
            "अघिल्लो जस्तै फेरि पठाउनु",
            "पहिलेको जस्तै मगाउनु",
            "अघिको अर्डर जस्तै गरिदिनु",
        ),
    ),
    Boundary(
        "thanks_with_praise",
        "thanks",
        (
            "सेकुवा राम्रो थियो, धन्यवाद",
            "पुरी तरकारी मिठो थियो, थ्याङ्क्यु",
            "खाना मिठो थियो धन्यवाद",
            "मःम एकदम राम्रो, धन्यवाद",
            "खाना स्वादिलो थियो है, धन्यवाद",
        ),
    ),
    Boundary(
        "thanks_with_praise",
        "recommend",
        (
            "कुन खाना राम्रो हुन्छ?",
            "सेकुवा राम्रो छ?",
            "कुन परिकार मिठो हुन्छ?",
        ),
    ),
    Boundary(
        "short_discovery_forms",
        "query_price",
        (
            "दहीको दाम कति?",
            "चिया कतिको?",
            "लस्सी कतिको?",
            "थाली कतिको?",
        ),
    ),
    Boundary(
        "short_discovery_forms",
        "query_availability",
        (
            "दही छ कि दिदी?",
            "आज छोइला पाइन्छ नि?",
            "सोमबार छोइला पाइन्छ?",
            "थाली अहिले पाइन्छ?",
        ),
    ),
    Boundary(
        "short_discovery_forms",
        "query_details",
        (
            "दही घरमै बनाएको हो?",
            "लेमन चियामा चिनी हुन्छ?",
            "पराठामा अण्डा हालिन्छ?",
            "सेल रोटीमा चिनी हालिन्छ?",
            "चिउरा भुटेको कि कच्चा?",
        ),
    ),
    Boundary(
        "short_discovery_forms",
        "show_menu",
        (
            "के के पाइन्छ होला नि?",
            "के के खाने कुरा छ?",
            "के के पाइन्छ होला?",
        ),
    ),
    Boundary(
        "availability_vs_hours",
        "query_availability",
        (
            "बिहानको खाना अहिले पाइन्छ कि?",
            "अहिले खाना पाइन्छ?",
            "अहिले नै पाइन्छ?",
        ),
    ),
    Boundary(
        "availability_vs_hours",
        "ask_hours",
        (
            "बिहान खाना कति बेला पाइन्छ?",
            "खाना कति बेलादेखि पाइन्छ?",
        ),
    ),
    Boundary(
        "delivery_localities",
        "ask_delivery",
        (
            "जोरपाटी पुर्याउनुहुन्छ कि?",
            "लगनखेल सम्म पुर्याउनुहुन्छ?",
            "घर सम्म पठाउनुहुन्छ?",
            "बौद्ध बाहिर पठाउनुहुन्छ कि?",
            "पाटन बाहिर पनि पठाउनुहुन्छ?",
        ),
    ),
    Boundary(
        "delivery_localities",
        "use_saved_address",
        (
            "अघिको ठेगाना प्रयोग गर्नुहोस्",
            "पहिले दिएको ठेगाना राख्नुहोस्",
            "पहिलेको ठेगानामा पठाउनु",
            "त्यही ठेगाना दोहोर्याउनु",
        ),
    ),
    Boundary(
        "status_short_forms",
        "order_status",
        (
            "अर्डर कसले ल्याउँदै हुनुहुन्छ?",
            "अर्डर किन आएको छैन?",
            "अर्डर कहाँ सम्म आयो?",
            "कति बेरमा पुग्छ अर्डर?",
        ),
    ),
    Boundary(
        "status_short_forms",
        "view_cart",
        (
            "अर्डर लिस्ट देखाउनु",
            "कार्टको लिस्ट दिनु",
        ),
    ),
    Boundary(
        "allergy_ingredient_forms",
        "allergy",
        (
            "माल्पुवामा दुध हाल्छन् कि नाइँ?",
            "चिकेन चिलीमा काजु हाल्छन् दाइ?",
            "चिकन चिल्लीमा हरियो खुर्सानी हाल्छन् कि?",
            "योमरीमा खुर्सानी हाल्छन् नि?",
            "पिज्जामा चिज हाल्छन् कि नाइँ?",
            "मःमको अचारमा बदाम हाल्छन्?",
            "थुक्पामा मैदा हाल्छन्?",
            "समय बजीमा अण्डा हाल्छन् कि?",
            "चटामरीमा दुध हाल्छन् नि?",
            "करीमा नरिवल हाल्छन्?",
        ),
    ),
    Boundary(
        "allergy_ingredient_forms",
        "query_details",
        (
            "माल्पुवामा के के हाल्छन्?",
            "चिकेन चिलीमा के हाल्छन्?",
            "योमरीमा के हाल्छन् नि?",
            "पिज्जामा के के हाल्छन्?",
            "मःमको अचारमा के पर्छ?",
            "थुक्पा बनाउँदा के हाल्छन्?",
        ),
    ),
    Boundary(
        "wallet_refund",
        "refund",
        (
            "मेरो पैसा वालेटमा पठाउनुहोस्",
            "पैसा वालेटमा फिर्ता गरिदिनु",
            "वालेटमा पैसा आएन नि",
            "पैसा वालेटमा हालिदिनुस्",
            "फिर्ता पैसा वालेटमा राख्नु",
        ),
    ),
    Boundary(
        "wallet_refund",
        "order_status",
        (
            "पैसा तिरिसकेँ, अर्डर कता पुग्यो?",
            "अर्डर कहाँ पुग्यो भन्नु न",
        ),
    ),
    Boundary(
        "attention_unclear",
        "unclear",
        (
            "यता हेर न के छ",
            "उता हेर त",
            "यता आउ न हेर",
            "हेर त यता",
        ),
    ),
    Boundary(
        "attention_unclear",
        "greet",
        (
            "दाइ के छ खबर?",
            "के छ खबर नि?",
            "हेलो, के छ?",
        ),
    ),
)

ITEM_WORDS = ("मःम", "थाली", "चिया", "पिज्जा", "कोल्ड ड्रिंक", "लस्सी")
ITEM_PHRASES: dict[str, tuple[str, ...]] = {
    "query_price": ("{} कति पर्छ?", "{} को दाम कति?"),
    "query_availability": ("{} छ त?", "{} पाइन्छ?"),
    "query_details": ("{} मा के हुन्छ?", "{} भित्र के छ?"),
}


def _item_boundaries() -> tuple[Boundary, ...]:
    boundaries = []
    for family_id, phrases in ITEM_PHRASES.items():
        messages = tuple(phrase.format(item) for item in ITEM_WORDS for phrase in phrases)
        boundaries.append(Boundary("item_query_triangle", family_id, messages))
    return tuple(boundaries)


def build_rows(
    *,
    boundaries: Sequence[Boundary] = BOUNDARIES + _item_boundaries(),
    businesses: Sequence = TRAINING_BUSINESSES,
    id_prefix: str = DEFAULT_ID_PREFIX,
    seed: int = 0,
) -> list[dict]:
    rows: list[dict] = []
    for boundary in boundaries:
        family = FAMILY_BY_ID[boundary.family_id]
        for index, message in enumerate(boundary.messages):
            case_id = f"{id_prefix}-{len(rows) + 1:04d}"
            business = businesses[(len(rows) + index) % len(businesses)]
            task = GenerationTask(
                id=case_id,
                family=family,
                language="ne",
                business=business,
                variant=0,
                prompt=build_prompt(business, family, "ne"),
            )
            rng = random.Random(f"{case_id}:{seed}")
            rows.append(build_case(task, message, rng, generator=GENERATOR).to_row())
    return rows


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="build deterministic minimal-pair rows")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--id-prefix", default=DEFAULT_ID_PREFIX)
    parser.add_argument("--boundaries", default="", help="comma-separated boundary names (default: all)")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)

    all_boundaries = BOUNDARIES + _item_boundaries()
    selected = all_boundaries
    if args.boundaries:
        wanted = {name.strip() for name in args.boundaries.split(",") if name.strip()}
        selected = tuple(boundary for boundary in all_boundaries if boundary.name in wanted)
        missing = wanted - {boundary.name for boundary in selected}
        if missing:
            parser.error(f"unknown boundaries: {', '.join(sorted(missing))}")

    rows = build_rows(boundaries=selected, id_prefix=args.id_prefix, seed=args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    counts: dict[str, int] = {}
    for boundary in selected:
        counts[boundary.name] = counts.get(boundary.name, 0) + len(boundary.messages)
    print(f"wrote {args.out} | {len(rows)} rows")
    for name, count in counts.items():
        print(f"  {name:24} {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
