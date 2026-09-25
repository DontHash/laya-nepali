# Handoff - laya-nepali

Last updated: 2026-09-25. State: the Devanagari benchmark v2 is authored (272
steps), the base-checkpoint baseline is measured, and the step review CLI is
ready. **Next action: human review of the 272 benchmark steps**
(`python -m layanep.benchmark.review run`) and `apply` to freeze the corpus.
After that: P1b generation (Devanagari-only, ~1,800 cases, LLM judge + tiered
review) and export.

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

## Verified

- `python -m pytest -q` -> 70 passed.
- `python -m layanep.eval --check` -> `ne-decisions-v1 gate: 1 cases, 5 decisions, PASS`.
- `ruff check src/ tests/ --select=E9,F63,F7,F82,F401,F811 --line-length=120` -> clean;
  `python -m compileall -q src/ tests/` -> clean.
- **Devanagari benchmark v2** (`data/benchmark/ne-bench-deva-v2.json`): 46 cases /
  272 steps, 12 per kind (36 for `discovery.query`), 92 safety/abstain, two
  held-out businesses; `validate_corpus` passes.
- **Base baseline on v2** (`reports/ne-bench-deva-v2-laya.{md,json}`):
  113/272 (41.5%), abstain 53/92, p50 406 ms, 0 errors. Failure shape:
  `show_menu` 0/12, `view_cart` 0/12, `use_saved_address` 0/12,
  `discovery.query` 9/36, 19 safety false commands.
- Baseline on `ne-probe-v1` (mixed script) unchanged: 55/79, abstain 12/17.
- Batch 1 dataset: `data/reviewed/ne-decisions-v1.jsonl` = 53 cases / 265
  decisions, 50 accepted + 3 edited; strict validation passes.
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

## Next: benchmark review, then P1b generation, then export

1. **Review the 272 benchmark steps (critical path):**
   ```bash
   python -m layanep.benchmark.review run --reviewer <name>   # a/e/l/r/s/q
   python -m layanep.benchmark.review list --status pending
   python -m layanep.benchmark.review apply                   # freezes the corpus
   ```
   Then re-run the baseline on the frozen corpus and record the number.
2. **P1b generation** per the revised plan: Devanagari-only default,
   class-balanced allocation (~100 per kind, ~320 safety/abstain), 7-8 training
   businesses, LLM judge pass, dedup; target ~1,800 cases / ~9,000 decisions.
   Reference stats from NepTrans/LINCE/tweets; spelling-variation augmentation
   from nspell/Bhasha; Kshitiz rows as auxiliary (cap ~30%); Foodmandu menus.
   Review: 100% human on safety/abstain, judge + 25% sample on kinds.
3. `export.py` - train/calibration splits, freeze `ne-decisions-v1`, emit JSONL
   to `data/export/`; the gate requires provenance + `reviewed_by` there.
4. P2 scaling experiment (400/900/1,800 cases) then the final fine-tune; P3
   publish; P4 upstream; P5 optional OrderWorkFlow adapter (shadow only).

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
