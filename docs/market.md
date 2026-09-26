# Where Jev/Laya-class decision models earn, and what to target in Nepal

Research date: 2026-09-26. Sources: `madewithjev.com` (build directory and
category counts, updated 2026-09-26), `typesafe.ai/blog/introducing-system-one-models-and-jev`
(2026-09-15), `github.com/NandhaKishorM/laya` README + BENCHMARKS (v0.3.20), and
this repo's `docs/CASE_STUDY.md`. Time-sensitive: recheck before any decision.

## 1. Where Jev is actually used

`madewithjev.com` catalogues 901 public builds. By use-case category:

| Field | Builds | Published economics |
|---|---|---|
| Agents and browsers | 167 | browser flight search 7 s, $0.0039 |
| Benchmarks and evals (judging) | 137 | OpenRouter Ori: 154 ms median, >5x faster than the next model |
| SDKs and integrations | 122 | - |
| Games and real time | 74 | virtual try-on $0.0011/decision, 620 ms |
| Routing and model choice | 52 | WebMCP harness: 49/49 tasks, ~112x cheaper |
| Social feeds | 51 | post scorer: 61 questions in ~1 s, $0.0004 |
| Coding and code review | 39 | blink.review (directory sponsor) |
| Search | 36 | Zillow scan <20 s / $0.18; YC index ~$0.002/query |
| Documents and OCR | 30 | 1,018 papers/invoices classified for $0.08, 256 ms |
| Ads and marketing | 24 | 724 ads torn down in 40 s, $0.09 |
| Inbox and support | 24 | 500 emails triaged for 3.5 cents |
| Sales and leads | 15 | 700 leads scored in 40 s, $0.09 |
| Trading and markets | 25 | $10k trading experiment |
| Robots, UI, SEO and GEO | 14/14/10 | SEO internal-link tooling |
| **Ecommerce** | **7** | second-hand shopping agent: 406 ms/listing, $0.00085 |

## 2. Where it earns

- **Pricing:** $0.042 per MTok input, output free, **no free tier**; median
  **$0.000068 per decision** across 15 published runs. Cost is never the
  bottleneck; latency and integration are.
- **TypeSafe's own positioning** (`typesafe.ai`): AI-powered workflows ("smart
  if-statements": classify, route, score, extract, branch), map-reducing over
  big data, real-time applications, and verification (judge, guardrail,
  detect jailbreaks). Explicitly *not* chatbots.
- **Paying patterns:** judging/scoring/evals, agent step-routing, search
  re-ranking, lead/ad scoring, document classification. Directory sponsors
  cluster in SEO/GEO, CRM/funnels, code review and agent infrastructure.
- **The money is in B2B workflow automation**, sold as reliability plus speed,
  not as an assistant.

## 3. Laya's counter-position

From the README and benchmark tables: 25k stars, 2.2k forks; 100+ languages
with a Router (45/51 languages usable vs 23 for the English checkpoint alone);
32.8 ms on a T4; Apache-2.0, self-hostable, Jev-wire compatible
(`POST /v1/systemone`), and **fine-tunable** - Jev states it does not fine-tune
per customer. Fine-tuning is the documented accuracy jump: 0.362 base to 0.766
on the typed-decisions benchmark.

Implications for a Nepali build:
- The wire compatibility means a Jev client needs only a base-URL repoint.
- The fine-tune (and the reviewed dataset behind it) is the differentiator
  TypeSafe's hosted model cannot copy.
- Laya's own gaps are ours to watch: option budget (~20 fully-described options
  per question), score levels need descriptions, confidence semantics differ
  from Jev's, and long documents are stable only to roughly 4k tokens.

## 4. Necessity ranking for Nepal

| Rank | Lane | Why now | Competition |
|---|---|---|---|
| 1 | Commerce / WhatsApp SME order routing | Commerce runs on WhatsApp/Facebook; order intent is the exact "smart if-statement" shape; no Nepali incumbent | none local; 7 global Jev builds |
| 2 | Invoices / receipts / accounting documents | VAT bills, remittance slips, QR receipts; the $0.08/1,000-doc pattern transfers directly | none local |
| 3 | Marketplace search and ranking | Hamrobazar-classifieds natural-language search in Nepali | none local |
| 4 | Fintech support routing (NepGlish) | Highest value and necessity (banks, wallets, remittance) | none local; slow, regulated sales |
| 5 | Nepali evals and judging | The fastest-earning lane in the Jev ecosystem itself; sell "does your LLM handle Nepali?" | none local |
| 6 | Government / citizen services | Highest public necessity (forms, nagarpalika) | slow procurement; flagship later |

## 5. Decision

Stage 2 targets, in order: **commerce (grocery/retail order routing) then
invoices/receipts**, with banking third and evals tooling as a low-cost
byproduct of the benchmark work. The discipline stays the same as
`ne-bench-deva-v2`: freeze a human-reviewed benchmark before training on a new
domain.

Why this order: ecommerce is the thinnest global field (7 builds) and our
deepest data moat; documents are a near-copy of a proven Jev pattern with no
local competition; both are demoable with the existing fine-tune loop before
fintech's longer sales cycle.
