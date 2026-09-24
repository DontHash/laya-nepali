# Pinned schema

The contract is copied from Laya's official fine-tuning notebook
(`notebooks/laya_finetune_typed_decisions_2xT4_kaggle.ipynb`, upstream
`NandhaKishorM/laya` v0.3.20) and the `LocalLLaMA/typed-decisions` dataset card.
It is implemented in `src/layanep/schema.py` and guarded by
`tests/test_schema.py`.

## Row

A dataset row carries `state`, `questions` and `gold` as **JSON strings**, plus
`id` and `workflow`:

```json
{
  "id": "ne-0001",
  "workflow": "restaurant_command_lu",
  "state": "{\"business\": {...}, \"customer_message\": \"...\"}",
  "questions": "{\"command\": {...}}",
  "gold": "{\"command\": {...}}"
}
```

`state` + `questions` together are exactly the body of a `POST /v1/systemone`
request, so a row can be replayed without reshaping it.

## Question

```json
{"type": "choice", "instructions": "...", "criteria": {"key": "description"}}
```

- `choice` criteria is a `{key: description}` map. The keys are part of the
  model input, so they are machine-stable dotted LU kinds while the descriptions
  carry the natural-language wording.
- `score` criteria is an ordered list of level descriptions.
- `noul` carries no criteria.
- Hard limit: **at most 20 choice options** (Laya's option budget); the
  benchmark card recommends keeping questions under ~20 options.

## Gold

```json
{"label": "discovery.query", "probabilities": {"discovery.query": 0.96, "none": 0.02, ...}}
```

- `choice`: probabilities keyed by criteria keys; missing keys are read as 0.0
  by the notebook; `label` must be one of the criteria keys.
- `noul`: probabilities keyed by `"true"` / `"false"`; `label` is `"true"` or
  `"false"`.
- `score`: probabilities keyed by `str(level_index)`; `label` is the level index
  as a string.
- Probabilities sum to 1.0 within `1e-3`.

## The five questions per case

Defined in `src/layanep/questions.py`:

| id | type | what it asks |
|---|---|---|
| `command` | choice (14) | the 13 LU command kinds plus `none` |
| `query_field` | choice (4) | price / availability / details / none |
| `order_intent` | noul | does the message attempt an order mutation? |
| `needs_staff` | noul | allergy / ingredient / refund / complaint / human handoff? |
| `abstain` | noul | must the assistant refuse to map any command? |

`score` questions are deliberately absent from v1: ordinal `score` is Laya's
weakest primitive and `laya-multilingual` has a measured first-level position
bias (upstream issue #131).

## Known upstream caveats designed around

- `noul` can under-report `true` on the multilingual checkpoint (#156) — the
  benchmark therefore records a 2-option `choice` variant of every `noul`
  question at evaluation time.
- Base checkpoints are near chance on typed decisions zero-shot: all capability
  comes from fine-tuning, so the P2 gate is measured against the fine-tuned
  model.
