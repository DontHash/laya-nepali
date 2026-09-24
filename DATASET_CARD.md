# Dataset card — laya-nepali decisions (draft)

Status: draft, to be completed at P1/P3. Revision: `ne-decisions-v1` (not yet
frozen).

## Summary

Nepali typed-decision data for fine-tuning and evaluating the
`convaiinnovations/laya-multilingual` System 1 checkpoint on restaurant
command understanding (the 13-kind LU vocabulary used by OrderWorkFlow).

## Composition (planned)

- 400 cases × 5 typed questions ≈ 2,000 decisions.
- Each case: a business/menu state plus one customer message.
- Questions per case: `command` (14-option choice), `query_field` (4-option
  choice), `order_intent` / `needs_staff` / `abstain` (noul).
- Languages: Devanagari Nepali and Romanized Nepali, with English code-switch
  where natural.
- Splits: train / calibration / frozen benchmark, grouped by template family;
  a never-trained safety + abstain subset.

## Provenance

Per-row `provenance` with source, generator and license. Source lanes are
recorded in `docs/provenance.md`. No PII: rows are synthetic or generated from
license-clean text; the deterministic gate scans for PII patterns.

## Licensing

Data: CC BY 4.0. Attribution strings for upstream sources are collected here
before publication (P3).

## Known limitations (to be measured at P2)

- Romanized Nepali has no standard spelling; coverage is bounded by the review.
- `noul` questions can under-report on the multilingual checkpoint; the
  benchmark scores a 2-option `choice` variant alongside.
- The data is restaurant-domain; the benchmark measures that domain only.
