# Roadmap: from dev benchmark to autonomous-safe Tier 0

Status: 2026-09-26. Baseline and decisions in `docs/autonomy-policy.md` and
`docs/market.md`. Numbers below refer to `ne-bench-deva-v2` (272 Devanagari
steps, frozen) unless stated otherwise.

Current position (kernel v8, 2,249 cases): **215/272 (79.0%)**, abstain 88/92,
**4 safety false commands**, ECE 0.053, 28 ms p50 on 2xT4. Best accuracy seen:
228/272 (v3) but with 12 false commands. The four survivors are
high-confidence semantic confusions: refund timing -> `order_status`,
`म्यानेजर छ?` -> `availability`, unclear fragments -> `menu`.

## Step 0 - finish the batch-7 cycle

- [x] Batch 7 built: 93 deterministic minimal-pair rows, 100% human review.
- [x] Export 2,342 cases / 11,710 decisions; gate PASS.
- [ ] Kernel v9 (batch-7 data) -> measure on the dev benchmark.
- Exit: the four boundaries move; accuracy not materially below v8.

## Phase 1 - trustworthy measurement

- [ ] `docs/autonomy-policy.md` approved (tier map above).
- [ ] Benchmark v3 held-out: ~800 steps across 4-6 businesses, >= 30 steps per
  critical family, authored outside the generator loop (LLM draft + 100% human
  review), minimal pairs for every known confusion. Frozen; never used for
  iteration.
- [ ] `eval` reports bootstrap CIs, per-family precision/recall, and the
  unsafe-rate with its exact binomial CI; the pre-registered rule is printed
  with every run.
- Exit: a number we can defend without the "optimistic dev benchmark" caveat.

## Phase 2 - policy layer first

- [ ] Implement the T0 allowlist + escalation rule in `eval` as a policy
  simulation, so every future run reports unsafe auto-executions (the gate that
  actually matters), not just false commands.
- Exit: a confident wrong kind on a T2 message is queue noise by construction.

## Phase 3 - close the boundary gap (loops until the gate passes)

- [ ] v9 verification; if FPs persist, generalize the batch-7 builder into a
  combinatorial minimal-pair module (person terms x particles, refund
  vocabulary x timing, item x availability, unclear templates, spellings).
- [ ] Two-stage training: general pass at weight 1, then a short low-LR
  hard-tune on contrastive pairs (replaces blanket 5x weighting, which cost 13
  accuracy points: 228 -> 215).
- [ ] Adversarial round: generate confidently-wrong hunters; mine calibration
  errors each run (the notebook already reports safety failures).
- [ ] If data alone stalls: 2-seed ensemble for boundary votes (small paid
  budget allows it).
- Exit: zero unsafe on benchmark v3 at the pre-registered rule, CI reported.

## Phase 4 - real data and shadow (P5 sidecar)

- [ ] Masked owner-attested logs (Kshitiz, Foodmandu) -> benchmark v4 and the
  real distribution for shadow mode.
- [ ] Shadow 2-4 weeks in OrderWorkFlow: model vs operator, no automation.
- [ ] Enable Tier 0 auto only, dead-man switch and full audit log; expand
  nothing until v4 meets the same criteria on real traffic.
- Exit: measured unsafe-auto rate 0 on live traffic; escalation rate trending
  down.

## Phase 5 - escalation product

- [ ] Production queue reusing the review UX: suggestion + calibrated
  confidence + tier + reason; one-click approve, edit or reject.
- [ ] Metrics: unsafe auto = 0, escalation rate, time to answer, operator
  agreement; decisions feed the next training batch (the flywheel).
- Exit: escalation rate falls batch over batch without unsafe events.

## Phase 6 - scale-out lanes

- [ ] Commerce lane next (order routing for more businesses), then the docs
  lane (invoices, receipts) from `docs/market.md`.
- [ ] Each domain gets its own schema, frozen benchmark, and popularity gate
  before training.
- Exit: a second workflow reaches Tier 0 under the same acceptance bar.

## Cadence and cost

Each loop: one human review session (60-200 rows, ~15-45 min), one Kaggle run
(~40 min, free 2xT4), one analysis session. Expect 4-6 loops to held-out zero.
Paid budget is reserved for Vertex data generation top-ups and, if needed, the
2-seed ensemble.
