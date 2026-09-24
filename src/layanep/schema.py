"""Pinned Laya typed-decision schema for the Nepali dataset.

The contract mirrors the official fine-tuning notebook
(``notebooks/laya_finetune_typed_decisions_2xT4_kaggle.ipynb``, upstream
NandhaKishorM/laya v0.3.20) and the ``LocalLLaMA/typed-decisions`` dataset card:

- a dataset row carries ``state``, ``questions`` and ``gold`` as JSON strings;
- ``state`` + ``questions`` together are exactly the body of a
  ``POST /v1/systemone`` request;
- a question is ``{"type": "choice" | "noul" | "score", "instructions": str,
  "criteria": ...}``;
- ``choice`` criteria is a ``{key: description}`` map (keys are part of the
  model input);
- ``score`` criteria is an ordered list of level descriptions;
- ``noul`` carries no criteria;
- gold is ``{"label": ..., "probabilities": {key: p}}`` per question, keyed by
  the choice criteria keys, by ``"true"``/``"false"`` for ``noul`` and by
  ``str(level_index)`` for ``score``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Mapping

DATASET_REVISION = "ne-decisions-v1"

QUESTION_TYPES = ("choice", "noul", "score")
MAX_CHOICE_OPTIONS = 20
MAX_SCORE_LEVELS = 10
PROBABILITY_TOLERANCE = 1e-3

LU_COMMAND_KINDS = (
    "social.greet",
    "social.thanks",
    "social.goodbye",
    "discovery.show_menu",
    "discovery.recommend",
    "discovery.query",
    "fulfillment.ask_hours",
    "fulfillment.ask_delivery",
    "fulfillment.order_status",
    "ordering.view_cart",
    "ordering.request_checkout",
    "ordering.repeat_order",
    "ordering.use_saved_address",
)

QUERY_FIELDS = ("price", "availability", "details")
ABSTAIN_KEY = "none"


class SchemaError(ValueError):
    """Raised when a case does not satisfy the pinned Laya schema."""


@dataclass
class Question:
    type: str
    instructions: str
    criteria: dict[str, str] | list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"type": self.type, "instructions": self.instructions}
        if self.criteria is not None:
            out["criteria"] = self.criteria
        return out

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Question":
        return cls(
            type=str(data.get("type", "")),
            instructions=str(data.get("instructions", "")),
            criteria=data.get("criteria"),
        )

    def option_keys(self) -> list[str]:
        if self.type == "choice":
            return list(self.criteria or {})
        if self.type == "score":
            return [str(i) for i in range(len(self.criteria or []))]
        return ["true", "false"]


@dataclass
class Gold:
    label: str
    probabilities: dict[str, float]
    score: float | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"label": self.label, "probabilities": self.probabilities}
        if self.score is not None:
            out["score"] = self.score
        return out

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Gold":
        raw = data.get("probabilities", {})
        return cls(
            label=str(data.get("label", "")),
            probabilities={str(k): float(v) for k, v in dict(raw).items()},
            score=float(data["score"]) if data.get("score") is not None else None,
        )


@dataclass
class Case:
    id: str
    workflow: str
    state: dict[str, Any]
    questions: dict[str, Question]
    gold: dict[str, Gold]
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "id": self.id,
            "workflow": self.workflow,
            "state": self.state,
            "questions": {qid: q.to_dict() for qid, q in self.questions.items()},
            "gold": {qid: g.to_dict() for qid, g in self.gold.items()},
        }
        if self.provenance:
            out["provenance"] = self.provenance
        return out

    def to_row(self) -> dict[str, Any]:
        """Serialise to the dataset row shape consumed by the fine-tuning notebook."""
        row: dict[str, Any] = {
            "id": self.id,
            "workflow": self.workflow,
            "state": json.dumps(self.state, ensure_ascii=False),
            "questions": json.dumps({qid: q.to_dict() for qid, q in self.questions.items()}, ensure_ascii=False),
            "gold": json.dumps({qid: g.to_dict() for qid, g in self.gold.items()}, ensure_ascii=False),
        }
        if self.provenance:
            row["provenance"] = self.provenance
        return row

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "Case":
        return cls(
            id=str(row.get("id", "")),
            workflow=str(row.get("workflow", "")),
            state=_as_object(row.get("state", {})),
            questions={qid: Question.from_dict(q) for qid, q in _as_object(row.get("questions", {})).items()},
            gold={qid: Gold.from_dict(g) for qid, g in _as_object(row.get("gold", {})).items()},
            provenance=dict(row.get("provenance") or {}),
        )


def _as_object(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        value = json.loads(value)
    if not isinstance(value, Mapping):
        raise SchemaError(f"expected a JSON object, got {type(value).__name__}")
    return dict(value)


def validate_question(qid: str, question: Question) -> None:
    prefix = f"question {qid!r}: "
    if question.type not in QUESTION_TYPES:
        raise SchemaError(prefix + f"type must be one of {QUESTION_TYPES}, got {question.type!r}")
    if not question.instructions.strip():
        raise SchemaError(prefix + "instructions must be a non-empty string")

    if question.type == "choice":
        criteria = question.criteria
        if not isinstance(criteria, Mapping) or not criteria:
            raise SchemaError(prefix + "choice criteria must be a non-empty {key: description} map")
        if len(criteria) > MAX_CHOICE_OPTIONS:
            raise SchemaError(prefix + f"{len(criteria)} options exceed the Laya limit of {MAX_CHOICE_OPTIONS}")
        for key, description in criteria.items():
            if not str(key).strip():
                raise SchemaError(prefix + "criteria keys must be non-empty strings")
            if not isinstance(description, str) or not description.strip():
                raise SchemaError(prefix + f"criteria[{key!r}] must be a non-empty description")
    elif question.type == "score":
        criteria = question.criteria
        if not isinstance(criteria, list) or len(criteria) < 2:
            raise SchemaError(prefix + "score criteria must be a list of at least two level descriptions")
        if len(criteria) > MAX_SCORE_LEVELS:
            raise SchemaError(prefix + f"{len(criteria)} levels exceed the limit of {MAX_SCORE_LEVELS}")
        if any(not isinstance(level, str) or not level.strip() for level in criteria):
            raise SchemaError(prefix + "score level descriptions must be non-empty strings")
    else:
        if question.criteria not in (None, {}, []):
            raise SchemaError(prefix + "noul questions must not carry criteria")


def validate_gold(qid: str, question: Question, gold: Gold) -> None:
    prefix = f"gold {qid!r}: "
    if not gold.probabilities:
        raise SchemaError(prefix + "probabilities must be a non-empty map")

    allowed = set(question.option_keys())
    unknown = sorted(set(gold.probabilities) - allowed)
    if unknown:
        raise SchemaError(prefix + f"probabilities contain keys outside the option set: {unknown}")

    for key, value in gold.probabilities.items():
        if not 0.0 <= value <= 1.0:
            raise SchemaError(prefix + f"probability for {key!r} must be in [0, 1], got {value}")
    total = sum(gold.probabilities.values())
    if abs(total - 1.0) > PROBABILITY_TOLERANCE:
        raise SchemaError(prefix + f"probabilities must sum to 1.0 (got {total:.4f})")

    if question.type == "choice":
        if gold.label not in allowed:
            raise SchemaError(prefix + f"label {gold.label!r} is not one of the choice options")
    elif question.type == "noul":
        if gold.label.lower() not in {"true", "false"}:
            raise SchemaError(prefix + f"noul label must be 'true' or 'false', got {gold.label!r}")
    else:
        if not gold.label.isdigit() or int(gold.label) >= len(question.criteria or []):
            raise SchemaError(prefix + f"score label must be a level index as a string, got {gold.label!r}")


def validate_case(case: Case) -> None:
    if not case.id.strip():
        raise SchemaError("id must be a non-empty string")
    if not case.workflow.strip():
        raise SchemaError(f"{case.id}: workflow must be a non-empty string")
    if not isinstance(case.state, Mapping) or not case.state:
        raise SchemaError(f"{case.id}: state must be a non-empty object")
    if not case.questions:
        raise SchemaError(f"{case.id}: questions must be non-empty")

    missing = sorted(set(case.questions) - set(case.gold))
    extra = sorted(set(case.gold) - set(case.questions))
    if missing or extra:
        raise SchemaError(f"{case.id}: gold keys must match question keys (missing={missing}, extra={extra})")

    for qid, question in case.questions.items():
        try:
            validate_question(qid, question)
            validate_gold(qid, question, case.gold[qid])
        except SchemaError as exc:
            raise SchemaError(f"{case.id}: {exc}") from exc
