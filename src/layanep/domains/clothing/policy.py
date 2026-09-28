"""Runtime autonomy policy guard — clothing domain.

Binds the shared tier engine (``policy_core.py``) to the clothing command
vocabulary. The hard allowlist is a structural guarantee: a command outside the
T0 set is never served automatically, regardless of confidence.

Confidence and p(none) thresholds are read from the fine-tuned checkpoint's
``rl_agent_config.json`` (fitted during P2 calibration).
"""

from __future__ import annotations

from ...policy_core import (
    DEFAULT_CONFIDENCE_TAU,
    DEFAULT_P_NONE_MAX,
    TierResult,
    classify_tier as _classify_tier,
    extract_signals as extract_signals,
)

# ---------------------------------------------------------------------------
# Tier definitions — the single source of truth for runtime guards.
# These mirror docs/autonomy-policy.md §2 exactly.
# ---------------------------------------------------------------------------

T0_READ_ONLY = frozenset({
    "greet", "thanks", "goodbye",
    "catalog", "recommend",
    "price", "size", "color", "material",
    "stock", "delivery", "cod",
    "order_status", "cart",
})

T1_MUTATIONS = frozenset({
    "checkout", "exchange", "custom_order", "saved_address",
})

# T2 is detected by the ``needs_staff`` noul question, not by command label.
#     skin_sensitivity, counterfeit, sizing dispute, refund demand,
#     complaint, human request.
# T3 is detected by the ``abstain`` noul question (unclear, gibberish,
#     bare_order, yes_no).

NEEDS_STAFF_REASON = (
    "needs_staff=true: skin_sensitivity/counterfeit/sizing dispute/refund/complaint/human request"
)


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
    """Classify a clothing decision into an autonomy tier (see ``policy_core``)."""
    return _classify_tier(
        label,
        confidence,
        p_none,
        needs_staff=needs_staff,
        abstain=abstain,
        tau=tau,
        p_none_max=p_none_max,
        t0_read_only=T0_READ_ONLY,
        t1_mutations=T1_MUTATIONS,
        needs_staff_reason=NEEDS_STAFF_REASON,
    )
