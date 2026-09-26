# P2 scaling experiment - Laya multilingual on Nepali typed decisions

Run date: 2026-09-26. Backend: Kaggle 2xT4, `laya==0.3.20`, multilingual
checkpoint subfolder, RLCD fine-tune with per-type temperature fit.

Data: `ne-decisions-v1` export (1,667 train / 170 calibration cases) and the
frozen benchmark `ne-bench-deva-v2` (46 cases / 272 steps, 92 abstain steps).
`TRAIN_LIMIT` slices the train file; calibration and benchmark stay fixed.

## Results

| Train cases | Benchmark v2 | Abstain | Safety false commands | ECE (answered) | Fitted temps (choice/score/noul) |
|---|---|---|---|---|---|
| 0 (base) | 113/272 (41.5%) | 53/92 | 19 | n/a | shipped config |
| 400 | 170/272 (62.5%) | 77/92 | 15 | 0.0955 | 1.201 / 1.200 / 1.103 |
| 900 | 198/272 (72.8%) | 80/92 | 12 | 0.1164 | 1.098 / 1.200 / 1.076 |
| 1667 (full) | **224/272 (82.4%)** | **82/92** | **10** | **0.0710** | 1.138 / 1.200 / 1.056 |

Latency at the full tier: p50 26.7 ms, p95 28.8 ms (T4 x2).

Gate status at the full tier: beat the 113/272 baseline (yes, +111 steps),
abstain 82/92 = 89% (yes), ECE <= 0.10 (yes, 0.0710), **zero safety false
commands (no, 10)**.

## Per-kind at the full tier

| Kind | Correct | False positives |
|---|---|---|
| abstain | 82/92 | 10 |
| discovery.query | 27/36 | 1 |
| discovery.recommend | 9/12 | 2 |
| discovery.show_menu | 10/12 | 2 |
| fulfillment.ask_delivery | 8/12 | 0 |
| fulfillment.ask_hours | 11/12 | 1 |
| fulfillment.order_status | 11/12 | 0 |
| ordering.repeat_order | 10/12 | 1 |
| ordering.request_checkout | 11/12 | 0 |
| ordering.use_saved_address | 11/12 | 1 |
| ordering.view_cart | 6/12 | 6 |
| social.goodbye | 11/12 | 1 |
| social.greet | 9/12 | 3 |
| social.thanks | 8/12 | 1 |

## Reading

- Accuracy scales monotonically with data (41.5% -> 62.5% -> 72.8% -> 82.4%);
  the working tier choice is the **full export**, not a smaller slice.
- ECE is non-monotonic (0.0955 / 0.1164 / 0.0710) - the 900-case model is
  overconfident, the full model is not. Temperature fit alone does not
  guarantee the ECE gate; it needs the full data.
- Safety false commands shrink with data (19 -> 15 -> 12 -> 10) but stay
  non-zero. Remaining hotspots: `view_cart` (6/12 with 6 false positives,
  including cart-like messages that must abstain) and `social.greet` notes.
- The evaluation abstains on `answer_confidence < 0.5`; the threshold is a
  fixed constant, not fitted. A calibration-split threshold sweep under a
  "zero safety false commands" constraint is the cheapest next lever, ahead of
  more generation.

## Artifacts

- Kaggle kernels: `bhishmbhandari/laya-nepali-finetune-{400,900,full}`
  (private), dataset `bhishmbhandari/laya-nepali-v1`.
- Raw run logs: `reports/p2-logs/kaggle-{400,900,full}.log` (Kaggle stream
  JSONL, one entry per line).
- Notebook: `notebooks/laya_finetune_nepali_2xT4_kaggle.ipynb` (eval cell
  fixed to key by step id, publish cell optional).
