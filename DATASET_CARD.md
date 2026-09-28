# Dataset card — laya-nepali decisions

Status: v1 frozen. Revisions `ne-decisions-v1` (restaurant, 6,197 cases /
30,985 decisions) and `cl-decisions-v1` (clothing, 8,035 cases / 40,175
decisions). Split counts and review modes are recorded in the manifests under
`data/export/` and `data/clothing_export/`.

## Summary

Nepali typed-decision data for fine-tuning and evaluating the
`convaiinnovations/laya-multilingual` System 1 checkpoint on two commerce
domains: restaurant command understanding (the 13-kind LU vocabulary used by
OrderWorkFlow) and clothing retail (catalog, sizing, COD, exchange, custom
orders).

## Composition

- Restaurant: 6,197 cases (train 5,585 / calibration 612) × 5 typed questions.
- Clothing: 8,035 cases (train 6,425 / calibration 805 / test 805) × 5 typed
  questions.
- Each case: a business state (menu or catalog) plus one customer message.
- Questions per case: `command` (16-option choice for restaurant, 19-option for
  clothing), `query_field` (4-option for restaurant, 6-option for clothing),
  and the `order_intent` / `needs_staff` / `abstain` noul questions.
- Languages: Devanagari Nepali and Romanized Nepali, with English code-switch
  where natural.
- Splits: train / calibration / frozen benchmark, grouped by template family;
  a never-trained safety + abstain subset.

## Provenance

Per-row `provenance` with source, generator and license. Source lanes are
recorded in `docs/provenance.md`. No PII: rows are synthetic or generated from
license-clean text; the deterministic gate scans for PII patterns.

## Licensing

Data: CC BY 4.0. Upstream sources, lanes and attestations are recorded in
`docs/provenance.md`, and every row carries its own `provenance` object.

## Known limitations

- Romanized Nepali has no standard spelling; coverage is bounded by the review.
- `noul` questions can under-report on the multilingual checkpoint; the
  benchmark scores a 2-option `choice` variant alongside.
- `ne-bench-deva-v2` measures the restaurant domain and `cl-bench-v1` the
  clothing domain; benchmark steps never appear in a training split.
