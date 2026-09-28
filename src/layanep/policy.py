"""Runtime autonomy policy guard.

Implements the tier system from ``docs/autonomy-policy.md``.  The hard
allowlist is a structural guarantee: a command outside the T0 set is never
served automatically, regardless of confidence.

Confidence and p(none) thresholds are read from the fine-tuned checkpoint's
``rl_agent_config.json`` (fitted during P2 calibration).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

# ---------------------------------------------------------------------------
# Tier definitions — the single source of truth for runtime guards.
# These mirror docs/autonomy-policy.md §2 exactly.
# ---------------------------------------------------------------------------

T0_READ_ONLY = frozenset({
    "greet", "thanks", "goodbye",
    "menu", "recommend",
    "price", "availability", "details",
    "hours", "delivery",
    "order_status", "cart",
})

T1_MUTATIONS = frozenset({
    "checkout", "repeat_order", "saved_address",
})

# T2 is detected by the ``needs_staff`` noul question, not by command label.
# T3 is detected by the ``abstain`` noul question (unclear / OOD).


@dataclass(frozen=True)
class TierResult:
    """The outcome of tier classification for a single message."""

    tier: int
    label: str | None
    confidence: float
    p_none: float
    auto_serve: bool
    reason: str


# ---------------------------------------------------------------------------
# Default calibration thresholds (overridden by checkpoint config).
# ---------------------------------------------------------------------------

DEFAULT_CONFIDENCE_TAU = 0.4
DEFAULT_P_NONE_MAX = 0.02


def classify_tier(
    label: str | None,
    confidence: float,
    p_none: float,
    *,
    needs_staff: bool = False,
    abstain: bool = False,
    tau: float = DEFAULT_CONFIDENCE_TAU,
    p_none_max: float = DEFAULT_P_NONE_MAX,
) -> TierResult:
    """Classify a model decision into an autonomy tier and decide auto-serve.

    Parameters
    ----------
    label:
        The ``command`` question's chosen criteria key (e.g. ``"price"``,
        ``"menu"``), or ``None`` / ``"none"`` when the model abstains.
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
            reason="needs_staff=true: allergy/refund/complaint/human request",
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
    if effective_label in T1_MUTATIONS:
        return TierResult(
            tier=1,
            label=effective_label,
            confidence=confidence,
            p_none=p_none,
            auto_serve=False,
            reason=f"{effective_label} is a T1 mutation: always escalate",
        )

    # --- T0: read-only — auto-serve only when calibration passes ----------
    if effective_label not in T0_READ_ONLY:
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
