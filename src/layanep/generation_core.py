"""Shared synthetic-generation engine.

Domain generator modules supply the data (businesses, families, prompt voice)
and bind this engine through a ``GenerationSpec``; plan building, gold
derivation and case assembly live here once.

Gold is *constructed* from the family that requested the message rather than
sampled from a teacher: the intended outcome is known by construction,
probabilities are deliberately soft, and the review pass corrects any message
that fails to express its intent.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from .reference import REGISTER_RULES
from .schema import ABSTAIN_KEY, Case, Gold


@dataclass(frozen=True)
class GenerationFamily:
    """One intended intent: what the message should express and its gold outcomes."""

    id: str
    command: str
    instruction: str
    query_field: str = ABSTAIN_KEY
    order_intent: bool = False
    needs_staff: bool = False
    abstain: bool = False
    confusable: str | None = None
    mentions_item: bool = False


@dataclass(frozen=True)
class GenerationTask:
    id: str
    family: GenerationFamily
    language: str
    business: Any
    variant: int
    prompt: str


@dataclass(frozen=True)
class GenerationSpec:
    """A domain's binding for the generation engine."""

    workflow: str
    command_criteria: Mapping[str, str]
    query_fields: Sequence[str]
    query_field_descriptions: Mapping[str, str]
    questions: Callable[[str | None], dict[str, Any]]
    build_prompt: Callable[[Any, GenerationFamily, str, int], str]


def prompt_rules(
    family: GenerationFamily,
    *,
    audience: str,
    item_word: str,
    list_word: str,
    register_line: str,
    variant: int = 0,
) -> list[str]:
    """Build the shared rule block for a generation prompt."""
    rules = [
        f"- The customer is writing to the {audience}; never write as the {audience}.",
        "- Express exactly one intent and nothing else; do not add a second request or order.",
        f"- Do not put the {audience}'s name in the message.",
    ]
    if family.mentions_item:
        rules.append(f"- Name one specific {item_word} from the {list_word}.")
    if variant:
        rules.append(f"- Variation {variant + 1}: use a clearly different wording, length and tone.")
    rules.extend(
        ["- " + rule for rule in REGISTER_RULES[:-1]]
        + [
            f"- {register_line}",
            "- No names, phone numbers, addresses, emails, URLs, emojis or line breaks.",
            "- Return only the message text, with no quotes and no explanation.",
        ]
    )
    return rules


def build_variant_plan(
    spec: GenerationSpec,
    *,
    businesses: Sequence[Any],
    families: Sequence[GenerationFamily],
    languages: Sequence[str],
    variants: int = 1,
    limit: int | None = None,
    id_prefix: str = "gen",
) -> list[GenerationTask]:
    """Legacy planner: every family × language × business × variant."""
    tasks: list[GenerationTask] = []
    for variant in range(variants):
        for family in families:
            for language in languages:
                for business in businesses:
                    tasks.append(
                        GenerationTask(
                            id=f"{id_prefix}-{len(tasks) + 1:04d}",
                            family=family,
                            language=language,
                            business=business,
                            variant=variant,
                            prompt=spec.build_prompt(business, family, language, variant),
                        )
                    )
                    if limit is not None and len(tasks) >= limit:
                        return tasks
    return tasks


def build_budget_plan(
    spec: GenerationSpec,
    *,
    businesses: Sequence[Any],
    families: Sequence[GenerationFamily],
    languages: Sequence[str],
    kind_cases: int,
    safety_cases: int,
    limit: int | None = None,
    id_prefix: str = "gen",
) -> list[GenerationTask]:
    """Budget planner: equal cases per command family and per safety family.

    Gives every command-kind family ``kind_cases`` cases and every
    safety/abstain family ``safety_cases``, cycling businesses and languages;
    ``id_prefix`` keeps ids unique across batches so dataset revisions never
    collide.
    """
    combos = [(business, language) for language in languages for business in businesses]
    tasks: list[GenerationTask] = []
    if not combos:
        return tasks
    max_budget = max(kind_cases, safety_cases)
    for index in range(max_budget):
        for position, family in enumerate(families):
            budget = kind_cases if family.command != ABSTAIN_KEY else safety_cases
            if index >= budget:
                continue
            combo_index = index + position
            business, language = combos[combo_index % len(combos)]
            variant = combo_index // len(combos)
            tasks.append(
                GenerationTask(
                    id=f"{id_prefix}-{len(tasks) + 1:04d}",
                    family=family,
                    language=language,
                    business=business,
                    variant=variant,
                    prompt=spec.build_prompt(business, family, language, variant),
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


def _command_distribution(rng: random.Random, spec: GenerationSpec, family: GenerationFamily) -> dict[str, float]:
    """Soft command targets, with no mass on ``none`` for command families.

    Kind messages are by definition commands, so the residual probability must
    not leak onto the abstain key: that leak made the model learn p(none)
    5-12% for social and query kinds and broke p(none)-gated abstention. Only
    abstain families keep ``none`` as the primary label.
    """
    keys = list(spec.command_criteria)
    distribution = dict.fromkeys(keys, 0.0)
    distribution[family.command] = rng.uniform(0.88, 0.95)
    rest = 1.0 - distribution[family.command]
    if family.command == ABSTAIN_KEY:
        secondary = family.confusable or "greet"
        distribution[secondary] += rest
    elif family.command in spec.query_fields:
        others = [other for other in spec.query_fields if other != family.command]
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


def derive_gold(spec: GenerationSpec, family: GenerationFamily, rng: random.Random) -> dict[str, Gold]:
    def noul(intended: bool) -> Gold:
        primary = "true" if intended else "false"
        probabilities = _categorical(rng, ("true", "false"), primary, 0.90, 0.96)
        return Gold(label=primary, probabilities=probabilities)

    return {
        "command": Gold(label=family.command, probabilities=_command_distribution(rng, spec, family)),
        "query_field": Gold(
            label=family.query_field,
            probabilities=_categorical(
                rng, list(spec.query_field_descriptions), family.query_field, 0.86, 0.94
            ),
        ),
        "order_intent": noul(family.order_intent),
        "needs_staff": noul(family.needs_staff),
        "abstain": noul(family.abstain),
    }


def build_case(
    spec: GenerationSpec,
    task: GenerationTask,
    message: str,
    rng: random.Random,
    *,
    generator: str,
) -> Case:
    state = task.business.state_base()
    state["customer_message"] = message
    state["language"] = task.language
    return Case(
        id=task.id,
        workflow=spec.workflow,
        state=state,
        questions=spec.questions(task.business.name),
        gold=derive_gold(spec, task.family, rng),
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
