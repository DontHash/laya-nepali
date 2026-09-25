# Research basis: the Jev/Laya LU probe (from OrderWorkFlow)

Copied from OrderWorkFlow's `JEV_LAYA_CASE_STUDY.md` (2026-09-24) as the
research context for this repo. It records the measured zero-shot results
(Laya 61/79 composite vs deterministic 41/79 vs fixed Gemini 76/79), the
safety boundary, and the decision gates this repo exists to clear.

---

# Jev / Laya feasibility case study (LU command classifier)

Status: Phase 0 complete; LU hardening applied (safety guard + schema fix).
No production path was enabled (`ORDERFLOW_DIALOGUE_LU` stays off). Date:
2026-09-24. Harness commit: `b10d211`; hardening commits: `3e35a6c`, `51dcc06`.

## Verdict

- **Gemini is the bar, and it is high.** After fixing the LU proposal schema
  (below), the production Gemini LU path scores **76/79 (96.2%)** model-only,
  52/55 on the deterministic gap, 0 errors, p50 1.36 s (paced free tier).
  Its remaining misses are one Nepali checkout phrase and two must-abstain
  cases.
- **Laya zero-shot does not beat that bar.** Composite (deterministic-first,
  Laya fallback) **61/79 (77.2%)** vs Gemini's 76/79; 0 errors; p50 881 ms on
  CPU. It is **not** ready to enable: 4/17 abstain cases became confident false
  commands (`"does the momo have nuts?"` -> `discovery.query` at 0.999).
- **The rule layer now covers that safety class for both models**: the handoff
  guard (2026-09-24) intercepts allergy/ingredient-content wording before any
  classifier runs.
- **Jev was not measured**: early-access/waitlist, hosted, no published
  multilingual benchmark, and no access from this environment. The harness
  speaks its wire protocol, so a comparison is one target away.
- **Recommendation**: keep `ORDERFLOW_DIALOGUE_LU=off`. Revisit Laya only
  after pilot traffic exists to fine-tune and calibrate on (its own model card
  calls the base checkpoints "a fast base to specialise, not a zero-shot
  decision engine"), and then require it to beat the fixed Gemini baseline
  (96.2%) with 17/17 abstains before any shadow rollout.

## What Jev and Laya are

| | Jev (TypeSafe AI, launched 2026-09-15) | Laya (Convai Innovations, 2026-09-18) |
|---|---|---|
| What | Closed "System One" API: typed `choice` / `score` / `noul` decisions over text in one forward pass; no text generation, no type errors | Apache-2.0 open weights, Jev-wire-compatible (`POST /v1/systemone`) |
| Access | Early access / waitlist; `api.typesafe.ai`, console + Python SDK | `pip install laya` (`laya[serve]`, `laya[mcp]`), self-host; Node ONNX SDK (`@receptron/laya`) exists but needs ~1.7 GB weights / ~2 GB RAM |
| Speed | 70-500 ms end-to-end (third-party p50 236-276 ms) | 32.8 ms on a T4; 193-464 ms on healthy CPU; measured here p50 881 ms (CPU, 6 threads) |
| Cost | $0.042 / MTok input, output free | $0 self-hosted + host cost |
| Limits | Closed, hosted, no published multilingual benchmark; English-first (`docs.typesafe.ai/models.md`), no customer fine-tuning; 255-option cardinality | <20 options recommended; English ctx 512 tok; calibration needs per-domain temperature fitting; documented `noul` label-following bug (#156); base checkpoints near chance on typed-decisions zero-shot (0.362 vs 0.461 majority baseline); project is days old |
| Nepali | No published support; "handled but not equally well"; **cannot be fine-tuned on our data** | Not in its published 51-language sweep; Devanagari routes to the multilingual checkpoint; **fine-tunable** (Apache-2.0) |

Sources: `typesafe.ai/blog/introducing-system-one-models-and-jev` (2026-09-15),
`docs.typesafe.ai` quickstart/models/jaggedness pages, `github.com/NandhaKishorM/laya`
README + BENCHMARKS.md (v0.3.20), `flowtivity.ai` benchmark (2026-09-21),
`madewithjev.com` (2026-09-22), MASSIVE dataset card (no Nepali). These are
time-sensitive; recheck before any decision.

## Where a decision model can plug in (verified seams)

- LU command classifier: `src/lib/dialogue/classifier.ts:93` (`LuRunner`
  injectable), `:152` (`classifyLuTurn`), prompt at `:112`. Deterministic
  classifier always wins; the model is consulted only when it returns nothing.
- Dialogue planner accepts `preclassified` (`src/lib/dialogue/policy.ts:32`).
- Order parser has an injectable `CloudParseRunner`
  (`src/lib/ai/order-parser.ts:173`) but is extraction, not classification -
  out of scope for typed decisions.
- Eval seam: `dialogue-contract-v1` (`npm run dialogue:eval`) is deterministic
  only, so this study adds a separate corpus + runner rather than touching the
  frozen gate.

## Method

- New corpus `src/dialogue-eval/lu-probe.ts` (`lu-probe-v1`): **79 steps**
  across both held-out menus - all 13 LU command kinds, 17 must-abstain cases
  (bare orders, plain yes/no, allergy/refund/human, gibberish), in English (51),
  Romanized Nepali (13), Devanagari (15).
- New runner/scoring `src/dialogue-eval/lu-probe-runner.ts` and CLI
  `src/eval/run-lu-probe.ts` (`npm run lu:probe`). Scores model vs
  deterministic vs composite (= deterministic when present, else model) per
  command kind, abstain accuracy, deterministic-gap accuracy, latency, errors.
- Laya scored via `POST /v1/systemone` as a single 16-option `choice` question
  with natural-language criteria keys, after four prompt-design iterations
  (abstract dotted keys scored far worse: 16/79; criteria-key wording is a
  first-class accuracy lever for this model).
- Gemini scored via the production `defaultLuRunner` + `buildLuPrompt`,
  paced at one request per 4.5 s (`--delay-ms=4500`) for the free tier.
- Reproduction:
  `LAYA_BASE_URL=http://127.0.0.1:8000 npm run lu:probe -- --laya-url=http://127.0.0.1:8000`
  and `npm run lu:probe -- --gemini --delay-ms=4500`. Reports in
  `dialogue-reports/lu-probe-*.{md,json}`. CI runs the deterministic probe.
- Environment: Windows dev box, 12 logical CPUs; Laya 0.3.20 + torch 2.14.0
  (CPU), `english` + `multilingual` checkpoints preloaded, `LAYA_THREADS=6`,
  `HF_HUB_DISABLE_SYMLINKS=1` (required on Windows without symlink privilege).

## Results (2026-09-24, lu-probe-v1)

| Classifier | Model correct | Composite | Abstain | Deterministic gap | p50 / p95 | Errors |
|---|---|---|---|---|---|---|
| deterministic | 41/79 (51.9%) | 41/79 (51.9%) | 17/17 | 17/55 | <1 ms | 0 |
| Laya (zero-shot, CPU) | 55/79 (69.6%) | **61/79 (77.2%)** | 13/17 | **37/55 (67.3%)** | 881 / 1434 ms | 0 |
| Gemini (production LU path, fixed schema) | **76/79 (96.2%)** | **76/79 (96.2%)** | 15/17 | **52/55 (94.5%)** | 1359 / 2054 ms | 0 |

The Gemini row is the fixed schema run (below), paced for the free tier. The
earlier broken run - 68/79 errors, every success an abstain - is preserved in
git history (`dialogue-reports/lu-probe-gemini.*` at `b10d211`) and described
in the defect section.

Deterministic baseline shape: 24 non-null predictions, all correct (100%
precision), abstains on all 17 must-abstain cases, but abstains on 38 steps
where a command was expected - that gap is the LU classifier's whole reason to
exist. Gemini closes 52/55 of it; Laya 37/55.

### Laya per kind (model correct / expected)

Strong: `social.goodbye` 4/4, `fulfillment.ask_delivery` 4/5,
`discovery.show_menu` 4/6, `social.greet` 3/4, `social.thanks` 3/4,
`fulfillment.ask_hours` 3/4, `fulfillment.order_status` 3/4,
`ordering.request_checkout` 3/4, `ordering.use_saved_address` 2/3,
`discovery.query` 9/13.
Weak: `ordering.view_cart` 1/4, `ordering.repeat_order` 1/3,
`discovery.recommend` 2/4.

Language split (from the misses list): the lift is concentrated in English
free text. Romanized Nepali and Devanagari are weak zero-shot (`"dhanyabad"` ->
none, `"मेनु देखाउनुहोस्"` -> goodbye, `"mero cart dekhaunus"` -> none).

### Safety-relevant false commands

Laya, high confidence (all 4 are now intercepted by the handoff guard before
classification):

| Message | Expected | Laya | Confidence |
|---|---|---|---|
| `does the momo have nuts?` | abstain (allergy) | `discovery.query` | 0.999 |
| `can i talk to a human?` | abstain (handoff) | `social.greet` | 0.999 |
| `maybe later` | abstain | `social.goodbye` | 0.997 |
| `no thanks` | abstain | `social.thanks` | 0.999 |

Moving the abstain rules into the option description did not fix these
(confidently wrong), which matches the model card's own warning about
zero-shot base checkpoints. Gemini's fixed run also produced
`"does the momo have nuts?"` -> `discovery.query` (plus `"yo k ho?"` ->
`social.greet`), which is why the deterministic handoff guard
(`src/lib/ai/message-intent.ts`) was broadened on 2026-09-24 to intercept
allergy and ingredient-content wording - `nuts`, `peanuts`, `dairy`, `lactose`,
`gluten`, `shellfish`, `contains`, question-shaped `egg/milk/wheat/...`, and
`<staple> free` - while leaving ordinary orders (`"do you have egg momo?"`)
flowing.

## Defect found and fixed (Gemini LU, 2026-09-24)

Before the fix, the probe's Gemini target failed 68/79 calls. The captured raw
output for `"where is my order?"`:

```json
{"recognized": true, "command": "fulfillment.order_status", "evidence": "where is my order?"}
```

`luProposalSchema` required `command` to be a discriminated-union object
(`{ "kind": "fulfillment.order_status" }`), so every command proposal was
rejected and the classifier silently fell back to "none"; abstain responses
(`recognized: false`) validated fine, which is why the failure was invisible in
smoke tests.

Fix (`51dcc06`): `luProposalSchema` is now flat -
`{ recognized, commandKind, query, question, evidence }` with consistency
refinements - and `classifyLuTurn` maps it back to `DialogueCommand`; the
prompt states the flat shape; `run-lu-probe.ts` gained `--delay-ms` pacing; CI
runs the deterministic probe after `dialogue:eval`. Re-measured: **76/79
(96.2%), 0 errors**.

## Cost and operations (if ever adopted)

- Marginal decision cost is negligible either way at this project's volumes
  (Gemini: fractions of a cent per turn; Jev: ~$0.00004 per 1-2K-token call;
  Laya: $0 + host).
- The real drivers are quota independence and latency. Gemini free-tier
  exhaustion is a documented recurring pain; a self-hosted decision model
  removes that for the LU leg only (the parser call remains). The paced probe
  run itself demonstrates the quota ceiling: 79 steps at 4.5 s spacing.
- Hosting reality: no Python or sidecar infrastructure exists in this stack
  (Vercel Hobby, 30s/60s function budgets, no Docker). Laya needs an always-on
  sidecar (GPU for its 33 ms headline; a decent CPU runs ~0.9 s p50 as
  measured) and cannot run inside Vercel functions. The Node ONNX SDK avoids
  Python but needs ~2 GB RAM and still wants a long-lived host.

## Decision gates (when to revisit)

1. ~~Fix the Gemini LU schema defect and re-measure.~~ Done 2026-09-24: the bar
   is 76/79 (96.2%) with 52/55 gap coverage.
2. ~~Broaden the deterministic handoff/ingredient guard.~~ Done 2026-09-24.
3. Real pilot traffic collected; Laya fine-tuned (its README documents a free
   2xT4 Kaggle loop) and temperature-calibrated on our decisions.
4. Re-run `npm run lu:probe` and require: composite **above 76/79**, abstain
   **17/17**, and no safety false commands - before any
   `ORDERFLOW_DIALOGUE_LU=shadow` rollout.
5. Jev only if waitlist access exists and a wide-option or hosted-convenience
   need is real; it can be scored through the same `/v1/systemone` target.

## Honest limits of this study

- One dev machine, one Laya release (0.3.20, days old), zero-shot only; no
  fine-tuning or temperature fitting was attempted.
- 79 steps with hand-authored ground truth (Nepali phrasing judgment calls);
  kind-level scoring only (`discovery.query` sub-fields and evidence text are
  not graded).
- Laya's own criteria-label sensitivity means another prompt design could move
  the number; the harness makes that measurable, the verdict should be
  re-derived after any prompt or model change.
- The Gemini baseline is one paced free-tier run; its remaining misses (one
  Nepali checkout phrase, two abstains) are single-step observations.
- Jev was not measured at all; the comparison table is Laya and Gemini on the
  current production stack, not Laya vs Jev.
