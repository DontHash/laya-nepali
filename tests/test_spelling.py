"""Spelling-variation augmentation."""

from __future__ import annotations

import random

from layanep.spelling import TOKEN_RE, VARIANTS, apply_spelling_variant


def test_variants_are_real_alternatives() -> None:
    for canonical, alternatives in VARIANTS.items():
        assert alternatives
        assert canonical not in alternatives


def test_no_variant_returns_none() -> None:
    assert apply_spelling_variant("नमस्ते हजुर", random.Random(1)) is None
    assert apply_spelling_variant("", random.Random(1)) is None


def test_variant_is_deterministic_and_survives_token_count() -> None:
    text = "मलाई मिठो लाग्यो, तपाईंलाई कति?"
    first = apply_spelling_variant(text, random.Random(5))
    second = apply_spelling_variant(text, random.Random(5))
    assert first is not None
    assert first == second
    assert len(TOKEN_RE.findall(first)) == len(TOKEN_RE.findall(text))


def test_at_most_max_substitutions() -> None:
    text = "मलाई मिठो लाग्यो, तपाईंलाई कति?"
    for seed in range(20):
        out = apply_spelling_variant(text, random.Random(seed), max_substitutions=1)
        assert out is not None
        original = TOKEN_RE.findall(text)
        changed = sum(1 for before, after in zip(original, TOKEN_RE.findall(out)) if before != after)
        assert changed == 1

    out = apply_spelling_variant(text, random.Random(3), max_substitutions=2)
    original = TOKEN_RE.findall(text)
    changed = sum(1 for before, after in zip(original, TOKEN_RE.findall(out)) if before != after)
    assert 1 <= changed <= 2


def test_variant_uses_the_table() -> None:
    out = apply_spelling_variant("मूल्य कति हो?", random.Random(11))
    assert out is not None
    assert "मुल्य" in out or "कती" in out
