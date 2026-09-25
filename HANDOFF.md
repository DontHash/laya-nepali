# Handoff - laya-nepali

Last updated: 2026-09-25. State: P0 scaffold + pre-P1 hardening + the
OrderWorkFlow migration are done and pushed to the private
`DontHash/laya-nepali` repo. The command vocabulary is unified (natural keys);
the next work block is P1 step 1 (`generate.py`).

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

## Verified

- `python -m pytest -q` -> 38 passed.
- `python -m layanep.eval --check` -> `ne-decisions-v1 gate: 1 cases, 5 decisions, PASS`.
- `ruff check src/ tests/ --select=E9,F63,F7,F82,F401,F811 --line-length=120` -> clean;
  `python -m compileall -q src/ tests/` -> clean.
- Baseline re-run after the vocabulary unification (`--classifier=laya --device=cpu
  --threads 6`): **55/79 (69.6%)**, abstain 12/17, p50 1232 ms (busy box), 0 errors.
  The seed run measured 55/79, abstain 13/17, p50 953 ms with a duplicated
  instruction sentence; the clean shared prompt trades `best seller?` (recovered)
  for `yo k ho?` (newly over-confident). Report in `reports/ne-probe-laya.{md,json}`.
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

## Next: P1 (decided)

1. `generate.py` - template skeletons -> Gemini Flash-Lite (keys in `.env`:
   `GEMINI_API_KEY` + ALT2/ALT3/ALT4) produces natural Devanagari and Romanized
   messages plus candidate gold; record `provenance.generator` as
   `gemini-<model>@<date>`; rows are candidates only.
2. `normalize.py` / `transliterate.py` - NFC, whitespace, glossary-assisted
   normalization (the glossary is ported: `src/layanep/glossary.py`).
3. `review.py` - CLI (`python -m layanep.review`) to accept/edit/reject
   candidates and write `data/reviewed/` with `reviewed_by`.
4. `export.py` - template-family splits (train / calibration / frozen benchmark
   + never-trained safety/abstain subset), freeze `ne-decisions-v1`, emit JSONL
   to `data/export/`; the gate then requires provenance + `reviewed_by`.
5. P2: Kaggle 2xT4 fine-tune of `convaiinnovations/laya-multilingual` +
   temperature fitting; P3 publish; P4 upstream; P5 optional OrderWorkFlow
   adapter (shadow only).

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
- Benchmark: `src/layanep/benchmark/{corpus,runner,report}.py`,
  `data/benchmark/ne-probe-v1.json`, `reports/ne-probe-laya.*`.
- Research basis: `docs/CASE_STUDY.md`.
