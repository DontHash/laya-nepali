# Provenance and license lanes

Every row in the export carries a `provenance` object with at least
`source`, `generator` and `license`. Only lanes marked **allowed** may reach
`data/export`.

## Allowed lanes (CC BY 4.0 compatible, attribution recorded)

| Source | License | Intended use |
|---|---|---|
| Aksharantar `nep` (AI4Bharat, local copy in ProjectR) | CC BY 4.0 | Roman ↔ Devanagari training pairs for the transliterator |
| Google FLEURS `ne_np` (local copy in NepTrans) | CC BY 4.0 | Devanagari phrasing mining |
| `Boredoom17/Nepali-Flow-Roman` (HF) | CC BY 4.0 | real Romanized spelling and slang mining |
| `kshitizgajurel/*` Nepali customer-care datasets (HF) | per-card — verify before use | intent/command phrasing inspiration |
| Kaggle Foodmandu menu dataset | per-card — verify before use | menu and item vocabulary |
| Hand-authored / translated / template-generated rows | CC BY 4.0 (ours) | the dataset itself |

## Blocked lanes

| Source | Reason |
|---|---|
| OpenSLR54 | CC BY-SA 4.0 — share-alike is incompatible with the CC BY 4.0 export |
| NepTrans conversation clips and transcripts | research-only, named people, consent not documented |
| ProjectR lyrics corpus, `mp3pm-scraper`, Wazam audio | scraped / unclear rights |
| VectorScaling OCR lines | license unknown until documented |
| Any row containing real names, phone numbers, addresses or emails | zero-PII rule |

## Rules

1. No source enters the export until its license is written in this file and the
   row-level `license` field matches it.
2. Attribution strings are collected in the dataset card before publication.
3. The deterministic gate (`python -m layanep.eval --check`) scans every state
   and instruction for PII patterns and fails on any hit.
4. Repo-local data (wordlists, lexicons) is used for normalization and
   vocabulary only; underlying text from undocumented-provenance files is never
   redistributed.
