# AGENTS.md

Context for AI coding assistants working in this repository.

`laya-nepali` builds the Nepali typed-decision dataset, fine-tune and benchmark
for the Laya System 1 decision model. It is private until v1. Nothing here may
touch OrderWorkFlow before P5; the only artifacts that ever leave are the P3
dataset/checkpoint publication, the upstream PRs (P4), and the optional
sidecar adapter (P5).

## Do NOT

- Add a row to `data/export` without a recorded license lane in
  `docs/provenance.md` and a matching row-level `provenance.license`; the gate
  enforces the lanes in `src/layanep/provenance.py`.
- Include real names, phone numbers, addresses, emails or URLs in any state,
  question or gold — the deterministic gate fails on PII patterns.
- Use a blocked source: OpenSLR54 (share-alike), NepTrans conversation
  transcripts (research-only, named people), scraped lyrics/audio, or anything
  with undocumented rights.
- Exceed 20 `choice` options or add `score` questions to v1.
- Change the pinned schema in `src/layanep/schema.py` without updating
  `tests/test_schema.py` and `docs/schema.md` in the same change.
- Skip the gates before declaring a change done:

  ```bash
  python -m pytest -q
  python -m layanep.eval --check
  ruff check src/ tests/ --select=E9,F63,F7,F82,F401,F811 --line-length=120
  python -m compileall -q src/ tests/
  ```

- Commit secrets, model weights or large binaries.
- Reformat files wholesale or reorder imports; match the file being edited.

## Conventions

- Conventional commit prefixes matching the history (`feat(schema):`,
  `fix(gate):`, `docs(provenance):`, `test(review):`); one logical change per
  commit.
- If a change moves numbers, report the before and after in the commit or PR.
- The dataset revision (`ne-decisions-v1`) is frozen at P1 acceptance; changes
  after that create `ne-decisions-v2`.
- Benchmark steps never appear in a training split; splits are grouped by
  template family.
