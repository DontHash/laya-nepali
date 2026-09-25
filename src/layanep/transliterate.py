"""Romanized-Nepali rendering and language detection.

Ported from OrderWorkFlow's ``src/lib/dialogue/transliteration.ts``: a
deterministic Romanized -> Devanagari glossary plus the script/token heuristic
the benchmark uses to pick a Laya checkpoint. Unknown Latin words pass through
unchanged.
"""

from __future__ import annotations

import re
import unicodedata

from .glossary import ORDERING_DICT

TRANSLITERATOR_REVISION = "transliterator-v1"

DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")
LATIN_TOKEN_RE = re.compile(r"[a-z]+")


def transliterate_to_devanagari(text: str) -> str:
    """Best-effort Romanized Nepali -> Devanagari for the ordering domain.

    Already-Devanagari text is returned unchanged (NFKC-normalized);
    multi-word phrases matching a dictionary key are replaced whole;
    otherwise every Latin token is mapped independently.
    """
    normalized = unicodedata.normalize("NFKC", text).strip()
    if not normalized:
        return normalized
    if DEVANAGARI_RE.search(normalized):
        return normalized

    lowered = normalized.lower()
    if lowered in ORDERING_DICT:
        return ORDERING_DICT[lowered]

    return LATIN_TOKEN_RE.sub(
        lambda match: ORDERING_DICT.get(match.group(0).lower(), match.group(0)),
        normalized,
    )


def detect_language(text: str) -> str | None:
    """Return ``"ne"``, ``"ne-rom"``, ``"en"``, or None for empty input."""
    normalized = unicodedata.normalize("NFKC", text)
    if not normalized.strip():
        return None

    devanagari_count = sum(1 for char in normalized if DEVANAGARI_RE.match(char))
    latin_count = sum(1 for char in normalized if char.isascii() and char.isalpha())

    if devanagari_count > 0 and devanagari_count >= latin_count:
        return "ne"

    tokens = [token for token in LATIN_TOKEN_RE.findall(normalized.lower()) if len(token) > 1]
    if not tokens:
        return None
    recognized = [token for token in tokens if token in ORDERING_DICT]
    recognized_romanized_nepali = (len(tokens) == 1 and len(recognized) == 1) or len(recognized) >= min(2, len(tokens))
    return "ne-rom" if devanagari_count > 0 or recognized_romanized_nepali else "en"
