"""Shared tier engine for the runtime autonomy policy guard.

Domain modules bind this engine to their vocabularies: ``policy.py``
(restaurant) and ``clothing_policy.py`` (clothing) each pass their T0
allowlist, T1 mutation set and escalation wording, so the classification
logic lives in one place.

The hard allowlist is a structural guarantee: a command outside a domain's T0
set is never served automatically, regardless of confidence.

Confidence and p(none) thresholds are read from the fine-tuned checkpoint's
``rl_agent_config.json`` (fitted during P2 calibration).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

DEFAULT_CONFIDENCE_TAU = 0.4
DEFAULT_P_NONE_MAX = 0.02
DEFAULT_NEEDS_STAFF_REASON = "needs_staff=true: escalate to a human operator"


@dataclass(frozen=True)
class TierResult:
    """The outcome of tier classification for a single message."""

    tier: int
    label: str | None
    confidence: float
    p_none: float
    auto_serve: bool
    reason: str


def classify_tier(
    label: str | None,
    confidence: float,
    p_none: float,
    *,
    needs_staff: bool = False,
    abstain: bool = False,
    tau: float = DEFAULT_CONFIDENCE_TAU,
    p_none_max: float = DEFAULT_P_NONE_MAX,
    t0_read_only: frozenset[str] = frozenset(),
    t1_mutations: frozenset[str] = frozenset(),
    always_escalate: frozenset[str] = frozenset(),
    needs_staff_reason: str = DEFAULT_NEEDS_STAFF_REASON,
) -> TierResult:
    """Classify a model decision into an autonomy tier and decide auto-serve.

    Parameters
    ----------
    label:
        The ``command`` question's chosen criteria key, or ``None`` /
        ``"none"`` when the model abstains.
    confidence:
        Calibrated answer confidence from ``agent.system_one``.
    p_none:
        Probability assigned to the ``none`` key in the command question.
    needs_staff:
        ``True`` when the ``needs_staff`` noul question answered ``true``.
    abstain:
        ``True`` when the ``abstain`` noul question answered ``true``.
    tau:
        Confidence threshold for auto-serving (from calibration fit).
    p_none_max:
        Maximum p(none) before the message is treated as OOD.
    t0_read_only:
        The domain's read-only allowlist; only these labels can auto-serve.
    t1_mutations:
        The domain's state-changing labels; they always escalate.
    always_escalate:
        Labels that depend on live backend state the service does not hold
        (order status, cart); they always escalate to a human regardless of
        confidence.
    needs_staff_reason:
        Domain wording recorded when ``needs_staff`` forces escalation.

    Returns
    -------
    TierResult with ``auto_serve=True`` only when all of:
        - the label is in the T0 allowlist,
        - ``needs_staff`` and ``abstain`` are both ``False``,
        - ``confidence >= tau``,
        - ``p_none < p_none_max``.
    """
    effective_label = label if label and label != "none" else None

    # --- T2: staff needed (allergy, refund, complaint, human request) ------
    if needs_staff:
        return TierResult(
            tier=2,
            label=effective_label,
            confidence=confidence,
            p_none=p_none,
            auto_serve=False,
            reason=needs_staff_reason,
        )

    # --- T3: unclear / OOD / abstain --------------------------------------
    if abstain or effective_label is None:
        return TierResult(
            tier=3,
            label=effective_label,
            confidence=confidence,
            p_none=p_none,
            auto_serve=False,
            reason="abstain or model chose none (unclear / OOD)",
        )

    # --- T1: state-changing mutations (always queue) -----------------------
    if effective_label in t1_mutations:
        return TierResult(
            tier=1,
            label=effective_label,
            confidence=confidence,
            p_none=p_none,
            auto_serve=False,
            reason=f"{effective_label} is a T1 mutation: always escalate",
        )

    # --- T2: live-backend-state labels (order status, cart) ----------------
    if effective_label in always_escalate:
        return TierResult(
            tier=2,
            label=effective_label,
            confidence=confidence,
            p_none=p_none,
            auto_serve=False,
            reason=f"{effective_label} needs live backend state: escalate",
        )

    # --- T0: read-only — auto-serve only when calibration passes ----------
    if effective_label not in t0_read_only:
        # Defensive: unknown label → escalate
        return TierResult(
            tier=3,
            label=effective_label,
            confidence=confidence,
            p_none=p_none,
            auto_serve=False,
            reason=f"unknown label {effective_label!r}: escalate",
        )

    if confidence < tau:
        return TierResult(
            tier=0,
            label=effective_label,
            confidence=confidence,
            p_none=p_none,
            auto_serve=False,
            reason=f"T0 but confidence {confidence:.3f} < tau {tau:.3f}: queue",
        )

    if p_none >= p_none_max:
        return TierResult(
            tier=0,
            label=effective_label,
            confidence=confidence,
            p_none=p_none,
            auto_serve=False,
            reason=f"T0 but p_none {p_none:.3f} >= {p_none_max:.3f}: OOD, queue",
        )

    return TierResult(
        tier=0,
        label=effective_label,
        confidence=confidence,
        p_none=p_none,
        auto_serve=True,
        reason="T0 read-only, confident, not OOD: auto-serve",
    )


def extract_signals(answers: Mapping[str, Any]) -> dict[str, Any]:
    """Extract tier-relevant signals from a ``system_one`` result.

    Returns a dict ready to unpack into ``classify_tier``.
    """
    command = answers.get("command", {})
    label = command.get("choice")
    confidence = float(command.get("answer_confidence", command.get("confidence", 0.0)))
    probs = command.get("probabilities") or {}
    p_none = float(probs.get("none", 0.0))

    def _noul_true(key: str) -> bool:
        q = answers.get(key, {})
        choice = q.get("choice", "false")
        return choice == "true"

    return {
        "label": label,
        "confidence": confidence,
        "p_none": p_none,
        "needs_staff": _noul_true("needs_staff"),
        "abstain": _noul_true("abstain"),
    }
