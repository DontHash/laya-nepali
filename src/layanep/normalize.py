"""Surface normalization applied to every message before review and export.

NFC, whitespace collapsing and stripping of wrapping quotes. Glossary-assisted
Romanized handling lives in ``transliterate.py``; this module is deterministic
and network-free.
"""

from __future__ import annotations

import unicodedata

NORMALIZER_REVISION = "normalizer-v1"
QUOTE_CHARS = "\"'\u2018\u2019\u201c\u201d"


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFC", text)
    return " ".join(normalized.split()).strip(QUOTE_CHARS).strip()
