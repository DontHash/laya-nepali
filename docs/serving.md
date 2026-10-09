# Serving contract — laya-nepali

Status: 2026-10-09. The service is a FastAPI app (`src/layanep/serve.py`)
serving one checkpoint per process. This file is the contract consumers may
rely on; changes here are contract changes and belong in the same commit as
the code they describe.

## Deployment

- Production target: Modal GPU (`modal_app.py`), T4, Bearer auth via the
  `laya-api-key` secret. CPU is **not** a supported deployment: the measured
  p50 is 8.0 s against a 3 s client budget.
- Configuration: `LAYA_MODEL_PATH`, `LAYA_DEVICE`, `LAYA_DOMAIN`,
  `LAYA_API_KEY` (optional; when unset the service is unauthenticated).
- `/health` is always unauthenticated; every other path requires
  `Authorization: Bearer <LAYA_API_KEY>` when the key is configured.

## Endpoints

### `GET /health`

```json
{
  "status": "ok | no_model",
  "model": "laya-nepali-clothing-v1",
  "domain": "clothing",
  "fine_tuned": true,
  "tau": 0.9,
  "p_none_max": 0.02,
  "max_len": 1024,
  "head_max_len": 256,
  "device": "cuda"
}
```

`tau` and `p_none_max` are the effective operating point decoded from the
checkpoint's `rl_agent_config.json`, with the domain defaults when absent.
`max_len` / `head_max_len` may be `null` when the config does not set them.

### `POST /v1/systemone` — raw Jev-wire pass-through

Request: `{"state": {...}, "questions": {...} | null, "business_name": "...", "domain": "restaurant|clothing"}`.
When `questions` is omitted, the server builds the domain's canonical question
set. The caller's `state` is forwarded verbatim to the decision model.
Response: `{"answers": {...}, "latency_ms": 12.3}`.

### `POST /v1/message` — classify → tier → template

Request: `{"text": "...", "business_name": "...", "business_state": {...}, "domain": "restaurant|clothing"}`.
Response:

```json
{
  "reply": "...",
  "label": "cod | null",
  "tier": 0,
  "auto_served": false,
  "confidence": 0.88,
  "reason": "...",
  "latency_ms": 64.3
}
```

`business_state` fills templates only; it never conditions the model decision.

## State contract

- The encoder receives `{"customer_message": "<text>"}` — the same shape the
  dataset rows and the published benchmark notebook serialize. Do **not** send
  `{"body": ...}`; it is a different state distribution.
- Business/menu state conditions `/v1/systemone` only. `max_prefixes` is not
  consulted by `laya==0.3.20`; the real limit is the `max_len` token budget,
  and `/v1/systemone` state is silently right-truncated to fit it.

## Autonomy policy

- T0 read-only labels auto-serve only when the label is in the domain allowlist,
  `needs_staff` and `abstain` nouls are false, `answer_confidence >= tau`, and
  `p_none < p_none_max`. Everything else escalates.
- `order_status` and `cart` are **always-escalate** labels: they need live
  backend state this service does not hold, so no reply is auto-served.
- `cod` renders the availability assertion only when the caller stated
  `cod_available: true`; `false` renders a negative statement, and an unstated
  flag renders the clarifying question.

## Outputs the service does not produce

- **No evidence spans.** The decision output has no character offsets, matched
  cues or justification. Consumers must not present the input echo as evidence.
- **No free text.** Replies are fixed templates plus caller-supplied facts; the
  service cannot invent prices, stock or policies.

## Errors

| Status | Meaning |
|---|---|
| 401 | Missing/wrong Bearer token when `LAYA_API_KEY` is set |
| 422 | Schema violation, or a request `domain` that is not installed |
| 503 | Model not loaded (`LAYA_MODEL_PATH` missing or the checkpoint failed to load) |
