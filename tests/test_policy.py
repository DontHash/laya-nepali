"""Policy guard: tier classification, auto-serve decisions, and signal extraction."""

from __future__ import annotations

import pytest

from layanep.policy import (
    T0_READ_ONLY,
    T1_MUTATIONS,
    classify_tier,
    extract_signals,
)


def test_t0_auto_serve() -> None:
    result = classify_tier("menu", confidence=0.95, p_none=0.01)
    assert result.tier == 0
    assert result.auto_serve is True


def test_t0_low_confidence_queues() -> None:
    result = classify_tier("price", confidence=0.3, p_none=0.01)
    assert result.tier == 0
    assert result.auto_serve is False


def test_t0_high_p_none_queues() -> None:
    result = classify_tier("greet", confidence=0.9, p_none=0.05)
    assert result.tier == 0
    assert result.auto_serve is False


def test_t1_mutation_always_escalates() -> None:
    result = classify_tier("checkout", confidence=0.99, p_none=0.001)
    assert result.tier == 1
    assert result.auto_serve is False


def test_t2_needs_staff() -> None:
    result = classify_tier("price", confidence=0.95, p_none=0.01, needs_staff=True)
    assert result.tier == 2
    assert result.auto_serve is False


def test_t3_abstain() -> None:
    result = classify_tier("menu", confidence=0.9, p_none=0.01, abstain=True)
    assert result.tier == 3
    assert result.auto_serve is False


def test_t3_none_label() -> None:
    result = classify_tier(None, confidence=0.0, p_none=0.5)
    assert result.tier == 3
    assert result.auto_serve is False
    assert result.label is None


def test_t3_none_string_label() -> None:
    result = classify_tier("none", confidence=0.0, p_none=0.9)
    assert result.tier == 3
    assert result.auto_serve is False
    assert result.label is None


def test_t0_vocabulary_coverage() -> None:
    assert len(T0_READ_ONLY) == 12
    for label in T0_READ_ONLY:
        result = classify_tier(label, confidence=0.95, p_none=0.001)
        assert result.tier == 0
        assert result.auto_serve is True, f"{label} should auto-serve at high confidence"


def test_t1_vocabulary_coverage() -> None:
    assert len(T1_MUTATIONS) == 3
    for label in T1_MUTATIONS:
        result = classify_tier(label, confidence=0.99, p_none=0.001)
        assert result.tier == 1
        assert result.auto_serve is False, f"{label} must always escalate"


def test_extract_signals() -> None:
    answers = {
        "command": {
            "choice": "menu",
            "answer_confidence": 0.92,
            "probabilities": {"menu": 0.92, "none": 0.01, "price": 0.07},
        },
        "needs_staff": {"choice": "false"},
        "abstain": {"choice": "false"},
    }
    signals = extract_signals(answers)
    assert signals["label"] == "menu"
    assert signals["confidence"] == pytest.approx(0.92)
    assert signals["p_none"] == pytest.approx(0.01)
    assert signals["needs_staff"] is False
    assert signals["abstain"] is False

    result = classify_tier(**signals)
    assert result.tier == 0
    assert result.auto_serve is True


def test_unknown_label_escalates() -> None:
    result = classify_tier("something_new", confidence=0.99, p_none=0.001)
    assert result.tier == 3
    assert result.auto_serve is False
