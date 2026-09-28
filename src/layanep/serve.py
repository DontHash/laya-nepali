"""FastAPI inference server wrapping the fine-tuned Laya checkpoint.

Exposes ``POST /v1/systemone`` (Jev-wire compatible) plus a higher-level
``POST /v1/message`` that runs the full pipeline: classify → tier guard →
template response or escalation.

Usage::

    # Install serving extras:
    pip install -e ".[model,serve]"

    # Start the server:
    python -m layanep.serve --model-path path/to/finetuned --device cuda

    # Or with uvicorn directly:
    uvicorn layanep.serve:app --host 0.0.0.0 --port 8000

Environment variables (override CLI defaults):
- ``LAYA_MODEL_PATH`` — path to fine-tuned checkpoint directory
- ``LAYA_DEVICE`` — ``cuda``, ``cpu``, or ``mps``
- ``LAYA_HOST`` / ``LAYA_PORT`` — bind address
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Sequence

logger = logging.getLogger("layanep.serve")

# ---------------------------------------------------------------------------
# Lazy imports — the server module must be importable without laya/torch
# installed (for tests that only exercise the policy + response layers).
# ---------------------------------------------------------------------------

_agent = None
_config: dict[str, Any] = {}

# Standard library and project imports that are always safe.
from .domains import available_domains, get_domain


def _resolve_domain(name: str):
    """Return the domain package for ``name``; unknown names fall back to restaurant."""
    try:
        return get_domain(name)
    except KeyError:
        return get_domain("restaurant")


def _load_checkpoint_config(model_path: str) -> dict[str, Any]:
    """Read ``rl_agent_config.json`` from the checkpoint directory."""
    config_path = Path(model_path) / "rl_agent_config.json"
    if config_path.is_file():
        with open(config_path, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def _load_agent(model_path: str, device: str | None = None):
    """Load the Laya agent and return ``(agent, config)``."""
    import laya

    cfg = _load_checkpoint_config(model_path)
    agent = laya.load(model_path, device=device)
    logger.info(
        "loaded checkpoint %s on %s (tau=%s, p_none_max=%s)",
        model_path,
        device or "auto",
        cfg.get("abstain_threshold", "domain default"),
        cfg.get("abstain_p_none", "domain default"),
    )
    return agent, cfg


try:
    from pydantic import BaseModel, Field
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = object  # type: ignore
    Field = lambda *args, **kwargs: None  # type: ignore


if HAS_PYDANTIC:
    class SystemOneRequest(BaseModel):
        state: dict[str, Any]
        questions: dict[str, Any] | None = None
        business_name: str | None = Field(default=None, description="Used to fill the command question instructions")
        domain: str | None = Field(default=None, description="Domain: 'restaurant' or 'clothing'")

    class SystemOneResponse(BaseModel):
        answers: dict[str, Any]
        latency_ms: float

    class MessageRequest(BaseModel):
        text: str
        business_name: str | None = None
        business_state: dict[str, Any] | None = Field(
            default=None,
            description="Menu/catalog, hours, delivery info — used for template responses",
        )
        domain: str | None = Field(default=None, description="Domain: 'restaurant' or 'clothing'")

    class MessageResponse(BaseModel):
        reply: str
        label: str | None
        tier: int
        auto_served: bool
        confidence: float
        reason: str
        latency_ms: float
else:
    SystemOneRequest = object  # type: ignore
    SystemOneResponse = object  # type: ignore
    MessageRequest = object  # type: ignore
    MessageResponse = object  # type: ignore


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

def create_app(
    model_path: str | None = None,
    device: str | None = None,
    domain: str | None = None,
):
    """Factory that creates the FastAPI app with optional model preloading."""
    try:
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
    except ImportError as exc:
        raise ImportError(
            "FastAPI is required for the serving layer. "
            "Install with: pip install -e '.[serve]'"
        ) from exc

    if not HAS_PYDANTIC:
        raise ImportError(
            "Pydantic is required for the serving layer. "
            "Install with: pip install -e '.[serve]'"
        )

    app_domain = domain or os.environ.get("LAYA_DOMAIN", "restaurant")

    # --- Lifespan: load model at startup -----------------------------------

    @asynccontextmanager
    async def lifespan(application):
        global _agent, _config
        path = model_path or os.environ.get("LAYA_MODEL_PATH")
        dev = device or os.environ.get("LAYA_DEVICE")
        if path:
            _agent, _config = _load_agent(path, dev)
        else:
            logger.warning(
                "no model path provided; /v1/systemone and /v1/message will "
                "return 503 until a model is loaded"
            )
        yield

    app = FastAPI(
        title="Laya Nepali",
        description=f"Nepali System 1 decision model — {app_domain} domain",
        version="0.1.0",
        lifespan=lifespan,
    )

    # --- Health check ------------------------------------------------------

    @app.get("/health")
    async def health():
        return {
            "status": "ok" if _agent is not None else "no_model",
            "model": _config.get("model_name", "unknown"),
            "domain": app_domain,
            "fine_tuned": _config.get("fine_tuned", False),
        }

    # --- Raw system_one (Jev-wire compatible) ------------------------------

    @app.post("/v1/systemone", response_model=SystemOneResponse)
    async def system_one(req: SystemOneRequest):
        if _agent is None:
            return JSONResponse(status_code=503, content={"error": "model not loaded"})

        questions = req.questions
        req_domain = req.domain or app_domain
        if questions is None:
            qs = _resolve_domain(req_domain).questions(req.business_name)
            questions = {qid: q.to_dict() for qid, q in qs.items()}

        started = time.perf_counter()
        result = _agent.system_one(req.state, questions)
        elapsed = (time.perf_counter() - started) * 1000

        return SystemOneResponse(answers=result.get("answers", result), latency_ms=round(elapsed, 2))

    # --- High-level message endpoint (classify + tier + respond) -----------

    @app.post("/v1/message", response_model=MessageResponse)
    async def message(req: MessageRequest):
        if _agent is None:
            return JSONResponse(status_code=503, content={"error": "model not loaded"})

        req_domain = req.domain or app_domain
        domain = _resolve_domain(req_domain)
        state = {"body": req.text}
        biz_state = req.business_state or {}
        business_name = req.business_name or biz_state.get("business", {}).get("name")

        qs = domain.questions(business_name)
        questions = {qid: q.to_dict() for qid, q in qs.items()}

        started = time.perf_counter()
        result = _agent.system_one(state, questions)
        elapsed = (time.perf_counter() - started) * 1000

        answers = result.get("answers", result)

        signals = domain.extract_signals(answers)
        tau = float(_config.get("abstain_threshold", domain.DEFAULT_CONFIDENCE_TAU))
        p_none_max = float(_config.get("abstain_p_none", domain.DEFAULT_P_NONE_MAX))
        tier_result = domain.classify_tier(**signals, tau=tau, p_none_max=p_none_max)
        if tier_result.auto_serve and tier_result.label:
            reply = domain.fill_template(tier_result.label, biz_state)
        else:
            reply = domain.escalation_message(tier_result.tier)

        return MessageResponse(
            reply=reply,
            label=tier_result.label,
            tier=tier_result.tier,
            auto_served=tier_result.auto_serve,
            confidence=round(tier_result.confidence, 4),
            reason=tier_result.reason,
            latency_ms=round(elapsed, 2),
        )

    return app


# Default app instance for ``uvicorn layanep.serve:app``
app = create_app()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Laya Nepali inference server.")
    parser.add_argument("--model-path", required=True, help="path to fine-tuned checkpoint directory")
    parser.add_argument("--device", default=None, help="cuda, cpu, or mps (default auto)")
    parser.add_argument("--domain", choices=available_domains(), default="restaurant", help="domain schema (default: restaurant)")
    parser.add_argument("--host", default="0.0.0.0", help="bind host (default 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="bind port (default 8000)")
    args = parser.parse_args(argv)

    import uvicorn

    os.environ["LAYA_MODEL_PATH"] = args.model_path
    os.environ["LAYA_DOMAIN"] = args.domain
    if args.device:
        os.environ["LAYA_DEVICE"] = args.device

    uvicorn.run("layanep.serve:app", host=args.host, port=args.port, log_level="info")
    return 0



if __name__ == "__main__":
    raise SystemExit(main())
