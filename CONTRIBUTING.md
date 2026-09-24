# Contributing

Thanks for helping. This repo is private until v1; the workflow below is the
same one Laya itself uses.

## Setup

```bash
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
```

## Before opening a pull request

```bash
python -m pytest -q
python -m layanep.eval --check
ruff check src/ tests/ --select=E9,F63,F7,F82,F401,F811 --line-length=120
python -m compileall -q src/ tests/
```

The CI runs exactly these commands on Python 3.11 and 3.13.

## Data changes

Dataset changes follow `docs/provenance.md`: a source must have a recorded
license lane before its first row reaches `data/export`, every row carries a
`provenance` object, and the deterministic gate must stay green (schema,
duplicate ids, probability sums, PII scan).

Ground-truth changes to the reviewed set are recorded with the reviewer and the
reason in the review sheet; after the `ne-decisions-v1` freeze they become a
new revision.

## Commits

Conventional prefixes, one logical change per commit:

```
feat(schema): ...
fix(gate): ...
docs(provenance): ...
test(review): ...
```

## License

Code contributions are Apache-2.0; dataset contributions are CC BY 4.0.
