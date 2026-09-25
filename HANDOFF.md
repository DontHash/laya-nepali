# Handoff - laya-nepali

Last updated: 2026-09-26 (morning). State: **dataset v1 reviewed and exported** —
1,835 cases / 9,175 decisions applied (692 human + 1,143 judge-auto; reviewer
DontHash), splits train 1,666 / calibration 169, deterministic gate PASS, all 106
tests green. Two human rows stayed pending and were excluded (`ne-v2-1292`
view_cart, `ne-v3-0248` allergy); review them to add the last 2. Benchmark v2
frozen at 113/272. Next: P2 fine-tune on the Kaggle notebook + gates.

## Commit map (main)

| Commit | What |
|---|---|
| `14ce55e` | P0 scaffold: pinned Laya schema, five-question set, license lanes, deterministic gate, CI |
| `b48e953` | Gate hardening: provenance lanes enforced in code, recursive export discovery, full-case PII scan |
| `dbfa24a` | Pins (`laya==0.3.20`, model revision), `.gitignore` secrets + weight formats, `.env.example` |
| `f1b6290` | Migrated `ne-probe-v1` corpus + Python eval harness + glossary/transliterator from OrderWorkFlow |
| `ddeecf0` | `docs/CASE_STUDY.md` (research basis) |
| `ffc9f08` | Seed benchmark report (`reports/ne-probe-laya.*`) |
| `a44dac1` | Unified command vocabulary on natural keys across dataset + benchmark; baseline re-run |
| `5471aa6` | `templates.py` + `generate.py`: 23 intent families, prompts, soft gold, Gemini client |
| `4a2053e` | `normalize.py` + `review.py`: script filters, review sheet CLI, apply with `reviewed_by` |
| `052ee20` | Review UX: show the intent under review; fix double `gemini-` prefix |
| `cbab57e` | Apply-time script guard; `staff sanga kura` phrasing; batch 1 applied (53 cases) |
| `e8020f7` | Devanagari benchmark v2 (272 steps) + multi-revision support + base baseline |
| `595ddbb` | Benchmark step review CLI + the 272-step review sheet |
| `05a8d2a` | Frozen benchmark v2 after human review (272 accepted, baseline 113/272) |
| `1236713` | Owner-attested provenance lanes; reference-only and augmentation lanes |
| `2985f77` | `reference.py` register profile + `spelling.py` variant augmentation + `docs/register.md` |
| `80f7217` | Budget plans, judge pass, dedup, spelling variants, resume; 7 training businesses |
| `03e6346` | Tiered review: judge auto-accept + 25% sampled human pass |
| `1951570` | Export splits + manifest + benchmark leakage gate (3 batch-1 collisions found and dropped) |
| `fe4e906` | Task id prefixes keep batch ids unique |
| `c1b22e5` | Handoff: batch-2 run, export and leakage-gate status |
| `17d685b` | Kaggle 2xT4 fine-tune notebook (multilingual subfolder, calibration fit, v2 eval) |
| `97ff62b` | Vertex AI backend (`VertexGenerator`, gcloud access token) after free-tier quotas emptied |
| `61bb42c` | Handoff: Vertex state and resume command |
| `94654c1` | Batch-2/3 tiered review sheet (1,838 records, 694 human) |
| `d86fb8b` | Handoff: batch 2+3 complete, review sheet state |
| `45c8198` | Review applied (692 human + 1,143 judge-auto); export 1,835 cases / 9,175 decisions |

## Verified

- `python -m pytest -q` -> 106 passed.
- `ruff check src/ tests/ --select=E9,F63,F7,F82,F401,F811 --line-length=120` -> clean;
  `python -m compileall -q src/ tests/` -> clean.
- **Devanagari benchmark v2** (`data/benchmark/ne-bench-deva-v2.json`): 46 cases /
  272 steps, frozen after review (272 accepted, 0 edits). Baseline:
  `reports/ne-bench-deva-v2-laya.{md,json}` = 113/272 (41.5%), abstain 53/92.
- **Dataset export v1**: `data/export/ne-decisions-v1-{train,calibration}.jsonl` +
  manifest = **1,835 cases / 9,175 decisions** (train 1,666 / calibration 169);
  `python -m layanep.eval --check` passes with `reviewed_by` required. Review
  modes: 692 human (all safety + sampled kinds) + 1,143 judge-auto.
- **Leakage gate worked**: 3 batch-1 messages coincided with benchmark steps
  (`नमस्ते हजुर`, `मेरो अर्डर कहाँ पुग्यो?`, `स्टाफसँग कुरा गर्न मिल्छ?`); they are
  recorded as rejected with the `leakage-gate` note and dropped from the export.
  Generation and review-build now reject benchmark collisions up front.
- Register profile from reference-only sources: reviewed commands p50 6 words,
  pure Devanagari; NepTrans podcasts (52,896 lines, 640k tokens) at 17% Latin
  tokens; rules in `docs/register.md`.
- **Batch 2+3 dataset**: `data/generated/ne-candidates-v2.jsonl` = 1,838 rows
  (1,736 cases + 102 variants, 23 families, 306 safety cases); review sheet
  1,838 records with 694 needing humans (306 safety + 388 sampled kinds, one
  benchmark collision rejected). With batch 1 that is **1,786 cases /
  ~8,930 decisions**. Model mix: 3.5-flash-lite 671, 3.1-flash-lite 461,
  3.6-flash 4, vertex:2.5-flash-lite 702 (`ne-v2-` + `ne-v3-`).
- `.env` is gitignored (it holds the Gemini keys); `.env.example` is tracked.

## Batch-2 run: quota incident and resume mechanics (2026-09-25)

- The first batch-2 run (671 rows = 641 tasks + 30 spelling variants) stalled for
  93 minutes during an internet outage: a failed task burns `retries x keys`
  attempts with backoff and writes nothing, so the row count froze. The process
  was alive and looping, not hung.
- On restore, every key returned **HTTP 429** for `gemini-3.5-flash-lite` — the
  free-tier daily quota is **per model**. Verified with all four keys at
  `--model` swap time: `gemini-3.1-flash-lite` 200 (restart target), fallbacks
  `gemini-3.1-flash-lite-preview` and `gemini-3.6-flash` 200;
  `gemini-flash-lite-latest` 429, `gemini-3.7/3.8-flash` 400, `gemini-2.5-*` 404.
- Background launches must be detached with WMI (`Invoke-CimMethod Win32_Process
  Create` on `C:\...\Temp\opencode\run-gen-v2.cmd`); children of `Start-Process`
  get killed with the calling shell and end up frozen.
- **Resume must not change `--id-prefix`**: skip matching is exact-id
  (`generate.py:327`), so a prefix change would regenerate every task under new
  ids. Remap `ne-gen-` -> `ne-v2-` only after the run completes.
- Batch-2 provenance is mixed by model: rows up to ~`ne-gen-0994` from
  `gemini-3.5-flash-lite`, then `gemini-3.1-flash-lite` until its bucket
  emptied, then `gemini-3.6-flash`; each row records this in
  `provenance.generator`.
- Late evening: `gemini-3.1-flash-lite` returned 429 on all four keys, so the
  run moved to `gemini-3.6-flash`. Realistic payloads (1,630-char task prompt)
  then 429'd there too while tiny probes passed — free-tier limits are
  token-based, so smoke tests understate throttling. `gemini-3-flash-preview`
  was flaky (503, 503, 4.2s). The run is left grinding overnight (~0.5
  rows/min, zero-risk) and resumes at full speed after the daily reset
  (~12:45 local) on the fast default `gemini-3.5-flash-lite`:
  `python -u -m layanep.generate --kind-cases 100 --safety-cases 40
  --delay-ms 1200 --out data/generated/ne-candidates-v2.jsonl --resume`
- Monitoring caveat: the venv `python.exe` is a launcher stub (12 MB, no
  python frames); the real worker is its `python3.11.exe` child. Target the
  child for CPU, py-spy and kill operations.
- **Vertex backend** (2026-09-25 late night): `generate.py` gained a
  `VertexGenerator` + `--backend vertex` using the authenticated gcloud CLI
  (`gcloud auth print-access-token`, cached/refreshed; project from
  `$GOOGLE_CLOUD_PROJECT` or `gcloud config`; region `us-central1`). Vertex
  publishes the 2.5 family (the 3.x names are AI-Studio-only), so the run uses
  `gemini-2.5-flash-lite` with `thinkingBudget: 0`. Live prompt tests: 2.2 s per
  call; a 3-case smoke run accepted 3/3 with `provenance.generator =
  vertex:gemini-2.5-flash-lite@2026-09-25`. Cost for the remainder is cents.
  Fatal cases: missing project, model 404 (clear message), 401 (token refresh),
  429/5xx (backoff).

## Environment (this machine)

- D: is full (~2 GB free), so the repo `.venv` cannot live in-tree. The working
  environment is `C:\Users\praka\AppData\Local\Temp\opencode\layanep-venv`
  (Python 3.11.9, `pip install -e ".[dev,model]"`). Recreate it anywhere on C:
  if the temp dir is cleaned.
- Model weights live in the shared HF cache
  (`C:\Users\praka\.cache\huggingface\hub\models--convaiinnovations--laya`,
  pinned snapshot `55cf4c4...`); no re-download is needed.
- On Windows without symlink privilege set `HF_HUB_DISABLE_SYMLINKS=1` before
  loading checkpoints.
- `laya.load()` has no `revision` argument; `benchmark.runner._pinned_model_path`
  loads the cached snapshot directory for `pins.MODEL_REVISION` and falls back
  to the hub id when it is absent.

## Findings to carry into P1/P2

- **Criteria-key wording is the accuracy lever — resolved**: dataset and
  benchmark now share the natural keys from `questions.py`
  (`COMMAND_CRITERIA` + `COMMAND_LABEL_TO_KIND`), which the zero-shot probe
  measured at 55/79 against 16/79 for dotted keys. Train and evaluate with the
  same question text.
- The multilingual checkpoint ships invalid temperature entries
  (`choice:11+ = 0.1006 -> clamped to 0.5`); confidence from those buckets is
  uncalibrated until P2 fits temperatures on our data.
- Safety: `"does the momo have nuts?"` was a confident false command for both
  Laya and Gemini in OrderWorkFlow; the deterministic handoff guard now
  intercepts it there, but the benchmark should keep a safety/abstain gate and
  the dataset must include the never-trained safety/abstain split.
- `docs/provenance.md` lanes marked "per-card - verify before use"
  (`kshitizgajurel/*`, Kaggle Foodmandu) hard-fail in code until verified.

## Next: finish batch 2, tiered review, top-up export, then P2

1. **Dataset v1 is reviewed and exported** (2026-09-26 morning): 1,835 cases /
   9,175 decisions, train 1,666 / calibration 169, gate PASS. Two human rows
   stayed pending and are excluded; to include them, re-open
   `python -m layanep.review run --reviewer DontHash`, then `python -m
   layanep.review apply` and `python -m layanep.export` (sheet decisions persist;
   ids `ne-v2-1292` view_cart and `ne-v3-0248` allergy).
3. **P2**: `notebooks/laya_finetune_nepali_2xT4_kaggle.ipynb` is ready (loads the
   `multilingual` subfolder, trains with RLCD, fits temperatures on the
   calibration split, evaluates on `ne-bench-deva-v2`); run the scaling
   experiment at 400 / 900 / 1,800 cases via `TRAIN_LIMIT`, pick the tier, then
   the final fine-tune; gates: beat 113/272 on v2, abstain target, zero safety
   false commands, ECE <= 0.10.
4. **Stage 2 (cross-domain)**: e-commerce (Kshitiz), banking (NepGlish after
   transliteration), delivery (Titung); own question schemas; cross-domain
   benchmark `ne-bench-cross-v1`; publish as `laya-nepali-v1`.

## Open decisions / risks

- Dataset criteria keys: **resolved 2026-09-25** - natural keys shared by
  training and benchmark (`a44dac1`).
- Target volume: 400 cases x 5 questions (~2,000 decisions) per the dataset
  card; the working tier is met for restaurant v1 at 1,786 cases / ~8,930
  decisions. Generation quota: free tiers are **per model and per key** (~1,400
  calls exhausted `gemini-3.5-flash-lite` on 2026-09-25); the Vertex backend
  (`--backend vertex`, gcloud token) is the unbilled-quota exit.
- CI runs only the deterministic gates (no weights); the benchmark is a manual
  local run by design.
- The OrderWorkFlow Laya probe path (`npm run lu:probe -- --laya-url=...`) has
  no local server anymore (the temp venv was deleted); reinstall if needed.

## Key files

- Schema/questions: `src/layanep/schema.py`, `src/layanep/questions.py`,
  `docs/schema.md`.
- Gate: `src/layanep/provenance.py`, `src/layanep/validate.py`,
  `src/layanep/eval.py`.
- Generation: `src/layanep/templates.py`, `src/layanep/generate.py`.
- Review: `src/layanep/normalize.py`, `src/layanep/review.py`,
  `data/reviewed/ne-decisions-v1.review.jsonl`.
- Benchmark: `src/layanep/benchmark/{corpus,runner,report,review}.py`,
  `data/benchmark/ne-probe-v1.json`, `data/benchmark/ne-bench-deva-v2.json`,
  `data/benchmark/ne-bench-deva-v2.review.jsonl`,
  `reports/ne-probe-laya.*`, `reports/ne-bench-deva-v2-laya.*`.
- Research basis: `docs/CASE_STUDY.md`.
