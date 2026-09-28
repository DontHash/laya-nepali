# Domains

Each commerce domain lives in its own package under `src/layanep/domains/`.
The pipeline and serving layer only talk to the package surface, so adding a
domain never touches shared code.

## Layout

```text
src/layanep/domains/
├── __init__.py        # registry: available_domains(), get_domain(name)
├── restaurant/
│   ├── __init__.py    # binds the surface below
│   ├── questions.py   # typed question definitions + command criteria
│   ├── responses.py   # RESPONSE_TEMPLATES + state flattener
│   ├── policy.py      # T0/T1 vocabularies + tier binding
│   └── generator.py   # businesses, families, prompts, plan/gold/case
└── clothing/
    └── ... same shape
```

Shared engines stay domain-agnostic at the package root: `policy_core.py`
(tier classification) and `responses_core.py` (fill/fallback/escalation).
Domain modules bind them to their vocabularies.

## Required surface

A domain package must expose (see `domains/restaurant/__init__.py`):

| Name | Purpose |
|---|---|
| `DOMAIN_NAME` | registry key, e.g. `"restaurant"` |
| `WORKFLOW` | dataset workflow id recorded in rows |
| `questions(business_name)` | typed question set |
| `T0_READ_ONLY`, `T1_MUTATIONS` | autonomy tier vocabularies |
| `DEFAULT_CONFIDENCE_TAU`, `DEFAULT_P_NONE_MAX` | calibration defaults |
| `classify_tier`, `extract_signals` | shared tier engine bound to the vocabulary |
| `RESPONSE_TEMPLATES`, `fill_template`, `escalation_message` | shared response engine bound to the domain |
| `generator` | synthetic generation: `TRAINING_BUSINESSES`, `FAMILIES`, `FAMILY_BY_ID`, `build_prompt`, `build_plan`, `derive_gold`, `build_case` |

`tests/test_domains.py` checks this surface for every installed domain.

## Adding a domain

1. Copy `domains/clothing/` to `domains/<name>/`.
2. Rewrite the questions, response templates, policy vocabularies and
   generator data (businesses, families, prompts) for the domain.
3. Update `DOMAIN_NAME` and the generator's `GENERATOR_WORKFLOW`.
4. Add tests mirroring `tests/test_clothing_*.py`; the registry contract test
   picks the new domain up automatically.
5. Run the gates: `python -m pytest -q`, `python -m layanep.eval --check`,
   `ruff check src/ tests/ --select=E9,F63,F7,F82,F401,F811 --line-length=120`,
   `python -m compileall -q src/ tests/`.
6. When the domain gets a frozen dataset revision, extend `DATASET_CARD.md`
   and the lanes in `docs/provenance.md`.
