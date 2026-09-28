"""Restaurant domain: typed questions, responses, policy guard, generator."""

from __future__ import annotations

from . import generator
from .policy import (
    DEFAULT_CONFIDENCE_TAU,
    DEFAULT_P_NONE_MAX,
    T0_READ_ONLY,
    T1_MUTATIONS,
    classify_tier,
    extract_signals,
)
from .questions import ne_questions as questions
from .responses import RESPONSE_TEMPLATES, escalation_message, fill_template

DOMAIN_NAME = "restaurant"
WORKFLOW = generator.GENERATOR_WORKFLOW

__all__ = [
    "DEFAULT_CONFIDENCE_TAU",
    "DEFAULT_P_NONE_MAX",
    "DOMAIN_NAME",
    "RESPONSE_TEMPLATES",
    "T0_READ_ONLY",
    "T1_MUTATIONS",
    "WORKFLOW",
    "classify_tier",
    "escalation_message",
    "extract_signals",
    "fill_template",
    "generator",
    "questions",
]
