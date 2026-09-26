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

## Decision-rule and data experiments at the full tier

Every Kaggle run retrains the model, so run-to-run noise matters. Ordered by date:

| Run | Data | Decision rule | Benchmark | Abstain | Safety FP | ECE |
|---|---|---|---|---|---|---|
| full v1 | 1,667 (dataset v1) | conf >= 0.5 | 224/272 (82.4%) | 82/92 | 10 | 0.0710 |
| full v2 | 1,807 (+batch-4 safety) | conf >= 0.5 | 218/272 (80.1%) | 81/92 | 11 | 0.0412 |
| full v3 | 1,807 | conf >= 0.5 | **228/272 (83.8%)** | 80/92 | 12 | 0.0666 |
| full v4 | 1,807 | conf >= 0.6, p(none) < 0.02 | 167/272 (61.4%) | 89/92 | 3 | 0.3503 |
| full v5 | 1,807 | conf >= 0.9, p(none) < 0.5 | 198/272 (72.8%) | 88/92 | 4 | 0.1783 |

Calibration sweeps (per run, on the 187-case calibration split, ~50 safety command
items, 286 kind command items):

- v3's model: zero safety FPs from tau >= 0.6 (kind hits 156/286 at tau 0.6,
  154 at 0.8).
- v5's model: zero safety FPs only at tau 0.9 (kind hits 63/286) - the fit does
  not transfer across retrains.
- v4's rule combined tau 0.6 with p(none) < 0.02 (the selector wrongly kept the
  *smallest* zero-FP cap instead of the largest); greeting kinds collapsed to
  0/12 before the selector was fixed.

Failure taxonomy of the remaining safety FPs at the best rule:

- Refund-status and late-delivery complaint phrasings read as `order_status`
  at 0.8-0.99 confidence with p(none) < 0.01
  (`रिफन्ड कहिले आउँछ?`, `अर्डर एक घण्टापछि आयो`, `अर्डर ढिलो आयो दिदी`).
- `फेरि भन्नु न` ("don't say it again") read as `repeat_order` at 0.99 (`फेरि`
  is the false friend).

These are high-confidence semantic confusions, not threshold misses, so neither
a confidence floor nor a p(none) cap reaches zero without destroying accuracy.
Closing the last FPs needs targeted contrastive data (batch 5) and/or a
deterministic product-side guard (OrderWorkFlow already intercepts allergy-like
handoffs), not more thresholding.

## Reading

- Accuracy scales monotonically with data in the fixed-rule runs
  (41.5% -> 62.5% -> 72.8% -> 82.4%); the working tier is the **full export**.
- The best published candidate is the **v3 model**: 228/272 (83.8%), abstain
  80/92, ECE 0.0666, safety FPs 12/92 (all in the taxonomy above).
- ECE is comfortably under the 0.10 gate whenever the threshold stays at 0.5;
  aggressive abstain rules wreck it (0.18-0.35) because the surviving answers
  are overconfident.
- Gate status at v3: baseline beaten (+115 steps), abstain 87%, ECE 0.0666;
  **zero safety false commands is not met (12)** and is a documented residual.

## Artifacts

- Kaggle kernels: `bhishmbhandari/laya-nepali-finetune-{400,900,full}` (private);
  `-full` version 3 is the best candidate (228/272), versions 4-5 hold the
  threshold experiments. Dataset `bhishmbhandari/laya-nepali-v1` (version 2 adds
  the batch-4 safety rows).
- Raw run logs: `reports/p2-logs/kaggle-{400,900,full,full-batch4,full-threshold,full-pnone,full-threshold-v2}.log`.
- Notebook: `notebooks/laya_finetune_nepali_2xT4_kaggle.ipynb` (step-level eval
  map, optional publish, calibration-fitted abstain rules, safety failure
  reporting).
