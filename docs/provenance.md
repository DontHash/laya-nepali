# Provenance and license lanes

Every row in the export carries a `provenance` object with at least
`source`, `generator` and `license`. Only lanes marked **shipping** may reach
`data/export`, and export rows also record `reviewed_by`.

## Shipping lanes

| Source | License field | Intended use |
|---|---|---|
| Hand-authored / template rows | `CC-BY-4.0` | benchmark, safety/abstain sets |
| LLM-generated candidates (`layanep.generate`, Gemini Flash-Lite) | `CC-BY-4.0` | candidate messages and labels; every row is human- or judge+sample-reviewed before export, and `generator` records the exact model id and date |
| Aksharantar `nep` (AI4Bharat, local copy in ProjectR) | `CC-BY-4.0` | Roman ↔ Devanagari pairs for the transliterator and augmentation |
| Google FLEURS `ne_np` (local copy in NepTrans) | `CC-BY-4.0` | Devanagari phrasing mining (attribution required) |
| `Boredoom17/Nepali-Flow-Roman` (HF) | `CC-BY-4.0` | real Romanized spelling and slang mining |
| `kshitizgajurel/*` customer-care datasets (HF) | `owner-attested` | auxiliary intent rows and phrasing; **owner attestation recorded 2026-09-25** |
| Kaggle Foodmandu menu dataset | `owner-attested` | menu and item vocabulary; **owner attestation recorded 2026-09-25** |

Attested rows stay traceable: `provenance.source` names the exact dataset, so
they can be identified or removed if rights ever change.

## Augmentation lane (verify license before shipping derived rows)

| Source | Status |
|---|---|
| `tnagorra/nspell` spelling-correction data | license check pending; variants generated from local lexicons ship now |
| Bhasha misspelling dictionary (`sarojdhakal/Bhasha`) | license check pending |
| NepTrans `curated_corrections` / `loanwords` lexicons | local project data; use for normalization and variant rules only |

## Reference-only lane (never shipped; statistics and patterns only)

| Source | Use |
|---|---|
| NepTrans conversation transcripts (podcasts, interviews) | register statistics: particles, code-switch density, phrasing patterns — no text enters the dataset |
| LINCE Nepali-English code-switching dataset | code-switch calibration |
| Nepal Earthquake tweets / `raygx/NepaliTweets` | informal register; PII-rich, never copied |
| Nepali Chat Corpus (`itsmeashutosh43`) | conversational register |
| Nepali National Corpus, 350K Sentences, CC100 `ne` | style reference |

## Gate assets (not dataset content)

| Source | Use |
|---|---|
| Nepali Names list (`datafiction/oya-nepali-nlp`) | PII gazetteer: names must never appear in rows |
| Nepali stopwords / n-grams | judge rubric and normalization helpers |

## Blocked lanes

| Source | Reason |
|---|---|
| OpenSLR54 | CC BY-SA 4.0 — share-alike is incompatible with the CC BY 4.0 export |
| NepTrans conversation clips and transcripts | research-only, named people, consent not documented (statistics lane above is the only use) |
| ProjectR lyrics corpus, `mp3pm-scraper`, Wazam audio | scraped / unclear rights |
| VectorScaling OCR lines | license unknown until documented |
| Any row containing real names, phone numbers, addresses or emails | zero-PII rule |

## Rules

1. No source enters the export until its lane is written in this file, the
   row-level `license` field is one of the allowed values
   (`src/layanep/provenance.py`), and export rows record `reviewed_by`.
2. Attribution strings are collected in the dataset card before publication.
3. The deterministic gate (`python -m layanep.eval --check`) scans every field of
   every case (id, workflow, state, questions, criteria, gold, provenance) for
   PII patterns and fails on any hit.
4. Repo-local data (wordlists, lexicons) is used for normalization and
   vocabulary only; underlying text from undocumented-provenance files is never
   redistributed.
