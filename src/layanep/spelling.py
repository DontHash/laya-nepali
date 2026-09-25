"""Spelling-variation augmentation for Devanagari messages (P1b).

Real Nepali WhatsApp text has non-standard spellings (vowel length, halant
drops, loanword orthography). The table below is hand-curated from the reviewed
batch and common usage; each entry maps a canonical token to observed
alternatives. A variant applies at most two token substitutions per message so
the intent survives, and augmented rows record
``provenance.augmentation = "spelling-v1"``.
"""

from __future__ import annotations

import random
import re

SPELLING_REVISION = "spelling-v1"

VARIANTS: dict[str, tuple[str, ...]] = {
    "मलाई": ("मलाइ",),
    "तपाईं": ("तपाइं", "तपाई"),
    "कति": ("कती",),
    "मूल्य": ("मुल्य",),
    "ठीक": ("ठिक",),
    "धन्यवाद": ("धन्यबाद",),
    "मिठो": ("मीठो",),
    "पाइन्छ": ("पाईन्छ",),
    "गर्नुहोस्": ("गर्नुहोस",),
    "दिनुस्": ("दिनुस",),
    "गर्नुस्": ("गर्नुस",),
    "सेभ": ("सेव",),
    "सेव": ("सेभ",),
    "डेलिभरी": ("डेलिवरी",),
    "रिफन्ड": ("रिफण्ड",),
    "मेनु": ("मेन्यु",),
    "भेटौंला": ("भेटौला",),
    "गरिदिनु": ("गरीदिनु",),
}

TOKEN_RE = re.compile(r"[\u0900-\u097F]+")


def apply_spelling_variant(text: str, rng: random.Random, *, max_substitutions: int = 2) -> str | None:
    """Return a spelling-perturbed copy of ``text``, or None when nothing applies."""
    candidates = [
        (match, variant)
        for match in TOKEN_RE.finditer(text)
        for variant in VARIANTS.get(match.group(0), ())
        if variant != match.group(0)
    ]
    if not candidates:
        return None

    rng.shuffle(candidates)
    chosen = []
    used_spans: set[tuple[int, int]] = set()
    for match, variant in candidates:
        span = (match.start(), match.end())
        if span in used_spans:
            continue
        used_spans.add(span)
        chosen.append((match, variant))
        if len(chosen) >= max_substitutions:
            break

    result = text
    for match, variant in sorted(chosen, key=lambda item: item[0].start(), reverse=True):
        result = result[: match.start()] + variant + result[match.end() :]
    return result if result != text else None
