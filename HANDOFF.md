# Handoff - laya-nepali

Last updated: 2026-09-25. State: benchmark v2 frozen; the restaurant batch-2
generation (1,820 tasks, judge + spelling variants) is running in the
background; the export pipeline and tiered review are ready. Next: finish the
run, review the sampled safety/kind set, top up the export, then P2.

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

## Verified

- `python -m pytest -q` -> 102 passed.
- `ruff check src/ tests/ --select=E9,F63,F7,F82,F401,F811 --line-length=120` -> clean;
  `python -m compileall -q src/ tests/` -> clean.
- **Devanagari benchmark v2** (`data/benchmark/ne-bench-deva-v2.json`): 46 cases /
  272 steps, frozen after review (272 accepted, 0 edits). Baseline:
  `reports/ne-bench-deva-v2-laya.{md,json}` = 113/272 (41.5%), abstain 53/92.
- **Dataset export**: `data/export/ne-decisions-v1-{train,calibration}.jsonl` +
  manifest = 50 cases / 250 decisions (44 train / 6 calibration);
  `python -m layanep.eval --check` passes with `reviewed_by` required.
- **Leakage gate worked**: 3 batch-1 messages coincided with benchmark steps
  (`नमस्ते हजुर`, `मेरो अर्डर कहाँ पुग्यो?`, `स्टाफसँग कुरा गर्न मिल्छ?`); they are
  recorded as rejected with the `leakage-gate` note and dropped from the export.
  Generation and review-build now reject benchmark collisions up front.
- Register profile from reference-only sources: reviewed commands p50 6 words,
  pure Devanagari; NepTrans podcasts (52,896 lines, 640k tokens) at 17% Latin
  tokens; rules in `docs/register.md`.
- `.env` is gitignored (it holds the Gemini keys); `.env.example` is tracked.

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

1. **Batch-2 generation is running** (background, started 2026-09-25):
   `python -m layanep.generate --kind-cases 100 --safety-cases 40 --delay-ms 1200
   --out data/generated/ne-candidates-v2.jsonl` (~10 rows/min, ~2,090 rows total).
   It predates `--id-prefix`, so once it finishes remap its ids from `ne-gen-`
   to `ne-v2-` (a small script; variant `-v1` suffixes follow automatically)
   before building the review sheet.
2. **Tiered review of batch 2**:
   ```bash
   python -m layanep.review build --input data/generated/ne-candidates-v2.jsonl
   python -m layanep.review run --reviewer <name>   # safety + 25% sampled kinds
   python -m layanep.review apply
   ```
   then re-run `python -m layanep.export` to top up train/calibration.
3. **P2**: adapt the Kaggle 2xT4 notebook for `laya-multilingual` (subfolder
   encoder/config/tokenizer), run the scaling experiment at 400 / 900 / 1,800
   cases, pick the tier, then the final fine-tune + temperature fit; gates:
   beat 113/272 on v2, abstain target, zero safety false commands, ECE <= 0.10.
4. **Stage 2 (cross-domain)**: e-commerce (Kshitiz), banking (NepGlish after
   transliteration), delivery (Titung); own question schemas; cross-domain
   benchmark `ne-bench-cross-v1`; publish as `laya-nepali-v1`.

## Open decisions / risks

- Dataset criteria keys: **resolved 2026-09-25** - natural keys shared by
  training and benchmark (`a44dac1`).
- Target volume: 400 cases x 5 questions (~2,000 decisions) per the dataset
  card; generation cost/quota with the free-tier keys is unmeasured.
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
