# laya-nepali

Nepali typed-decision dataset, fine-tune, and benchmark for the
[Laya](https://github.com/NandhaKishorM/laya) System 1 decision model.

**Status: P0 scaffold.** Private until v1 (P3). Nothing Laya-specific leaves
this repo except through the upstream PRs (P4) and the optional OrderWorkFlow
adapter (P5).

## What this is

Laya is a non-autoregressive decision model: give it a state (text, JSON) and
typed questions (`choice` / `noul` / `score`), and it returns calibrated
probabilities in one forward pass. Its base checkpoints are near chance
zero-shot; capability comes from fine-tuning on decisions from your domain.

This repo adapts Laya to Nepali:

- **P0 — scaffold** (this commit): private repo, pinned fine-tune schema,
  license lanes, CI gates.
- **P1 — dataset v1**: 400 cases × 5 typed questions ≈ 2,000 decisions across
  the 13 LU command kinds, query subfields (price/availability/details),
  abstains and safety handoffs, in Devanagari and Romanized Nepali, with a
  human-reviewed ground truth and zero PII.
- **P2 — fine-tune + calibration** on Kaggle 2×T4, base checkpoint
  `convaiinnovations/laya-multilingual`, temperature fitting per question type.
- **P3 — publish v1**: HF dataset (CC BY 4.0) + checkpoint (Apache-2.0) with an
  honest model card and a benchmark report in Laya's `BENCHMARKS.md` format.
- **P4 — upstream**: Romanized-Nepali `lang_guess` PR, benchmark integration,
  findings.
- **P5 — optional integration** in OrderWorkFlow behind the existing
  `LuRunner`, shadow first.

## Layout

```
src/layanep/            schema pin, generation, normalization, transliteration,
                        review, export, deterministic eval gate
src/layanep/benchmark/  frozen Nepali benchmark corpus/runner/report (P1/P2)
tests/                  pytest suites + golden fixtures
docs/                   schema.md (pinned contract), provenance.md (license lanes)
data/sources/           raw downloads (gitignored)
data/generated/         generated candidates (gitignored)
data/reviewed/          human-reviewed ground truth
data/export/            frozen export consumed by the gate and the notebook
```

## Development

```bash
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"

python -m pytest -q
python -m layanep.eval --check
ruff check src/ tests/ --select=E9,F63,F7,F82,F401,F811 --line-length=120
python -m compileall -q src/ tests/
```

The last three commands mirror Laya's own contribution gates.

## Licensing

- Code: Apache-2.0 (`LICENSE`).
- Data: CC BY 4.0 (`DATA_LICENSE`); every row carries provenance and the
  source lanes are recorded in `docs/provenance.md`.
