# External message-bank generation prompt

Versioned spec for growing the corpus with a strong external LLM. The output is
a JSONL message bank, not full cases: ids, state, questions, gold labels and
probabilities are derived by `src/layanep/import_bank.py` through
`templates.build_case`, so the writing model cannot drift the schema.

## Bank format

One JSON object per line, exactly two keys:

```json
{"message": "मलाई बदामले एर्लजी छ, के खानु हुन्छ?", "family": "allergy"}
```

- `message`: Nepali in Devanagari, 1-15 words, one intent, no Latin letters,
  digits, emojis, PII or restaurant names.
- `family`: one id from the 26-family catalog below.
- `//` comment lines are tolerated and skipped by the importer.

## Governance

Rows arrive pre-reviewed by the requester; the importer records
`reviewed_by` in provenance and reopens a deterministic spot-check sample
(15% of safety rows, 5% of kind rows) for in-sheet human review. All automated
gates still run: script/PII validation, benchmark-collision drop, corpus
dedupe, schema validation, export gate.

BatchB (2026-09-26): 3,442 entries delivered, 3,402 imported (20 benchmark
collisions, 20 duplicates dropped, 3 comment lines skipped), 2 rows relabeled
from `unclear` to `late_delivery` before import.

## Prompt (paste into the generating LLM)

```
You are generating training data for a Nepali restaurant WhatsApp assistant.
Your entire output is ONE downloadable file named `ne-messages-batchB.jsonl`.
If you have a code interpreter or file-output tool: write the file and give me the download
link. If you cannot, output the raw file content only (no prose), and if output limits are
hit continue in the next message with a line "PART n/m"; never truncate a JSON line, never
repeat a line already written. If you need smaller parts, use the 4-part split at the end.

FORMAT — strictly JSON Lines (.jsonl):
- One JSON object per line, exactly two keys: "message" and "family".
- "message": Nepali text in Devanagari, written LITERALLY (never \uXXXX escapes).
- "family": exactly one id from the catalog below, lowercase.
- No markdown fences, no headers, no comments, no trailing commas, no blank lines.
- UTF-8. No emojis, no digits, no Latin letters anywhere in "message".

MEANING: the assistant routes one customer WhatsApp message to exactly one intent.
Write messages a real customer would type. ONE intent per message, never two.

HARD RULES
1. 1-15 words per message (mostly 2-8), natural typing, not formal written Nepali.
2. Never mention any restaurant name. Never include names, phones, addresses, emails, URLs.
3. Particles: at most 1 in 3 messages may end with नि/त/है/न; दाइ/दिदी/हजुर in at most 1 in 3;
   the rest plain. Vary word order.
4. Rotate food words: मःम, मोमो, थाली, चिया, कफी, लस्सी, पिज्जा, बर्गर, चाउमिन, सेकुवा, छोइला,
   समय बजी, चटामरी, योमरी, पराठा, भात, दाल, तरकारी, मिठाई, आइसक्रिम.
5. Spelling/register variety: both रिफन्ड and रिफण्ड, both मःम and मोमो, both ढिलो and ढिला;
   mix formal (हजुर/दाइ/दिदी) and casual (no address) styles.
6. No sentence may repeat anywhere in the file.
7. For every "contrast" pair, generate BOTH sides in the same part; the distinguishing word
   should be the main difference. Examples (do NOT copy, write fresh):
   "अर्डर कति बेरमा आउँछ?" (order_status) vs "अर्डर ढिलो आयो" (late_delivery)
   "के राम्रो हुन्छ?" (recommend) vs "मलाई बदामले एलर्जी छ, के खानु हुन्छ?" (allergy)
   "फेरि त्यही अर्डर गरिदिनु" (repeat_order) vs "फेरि भन्नु न" (unclear_repeat)
   "मःम छ?" (query_availability) vs "म्यानेजर छ?" (human)
   "अर्डर कहाँ छ?" (order_status) vs "रिफन्ड कहिले आउँछ?" (refund_status)
8. Complaints and pleas are never "unclear": messages that blame lateness, cold or wrong
   food, or payment issues belong to late_delivery, complaint, refund or refund_status.

FAMILY CATALOG (id — meaning — contrast with)
greet — greeting (नमस्ते, नमस्कार, हेलो) — contrast: show_menu, unclear
thanks — thanking — contrast: yes_no
goodbye — ending the conversation
show_menu — asking to see the menu or what is available — contrast: recommend, greet
recommend — asking for a recommendation or best seller — contrast: show_menu
query_price — asking the price of a specific item (name one)
query_availability — asking whether a specific item is available (name one) — contrast: human
query_details — asking what an item contains or is made of (name one) — contrast: allergy
ask_hours — opening hours — contrast: ask_delivery
ask_delivery — delivery area, fee or time — contrast: order_status, use_saved_address
order_status — tracking an existing order — contrast: late_delivery, refund_status, view_cart
view_cart — seeing the current cart or draft order — contrast: order_status, request_checkout
request_checkout — placing or confirming the order — contrast: view_cart, bare_order
repeat_order — asking for the same order again — contrast: unclear_repeat, request_checkout
use_saved_address — using a saved or home address — contrast: ask_delivery
bare_order — a bare item with no quantity or confirmation (मोमो, चिया) — contrast: request_checkout
yes_no — a plain yes or no answer (हुन्छ, होइन) — contrast: thanks
allergy — asking about allergens OR declaring an allergy (मलाई दूधले एलर्जी छ) — contrast: query_details
refund — asking for a refund or disputing a payment — contrast: refund_status, order_status
refund_status — asking when a refund arrives or why it is pending — contrast: order_status, refund
late_delivery — complaining the order was late or took too long — contrast: order_status, complaint
complaint — complaining food was cold, wrong or damaged — contrast: late_delivery, order_status
human — asking for staff, manager or owner (स्टाफसँग कुरा, म्यानेजर छ?) — contrast: query_availability, greet
gibberish — keyboard mash with no meaning — contrast: greet
unclear — unclear or off-topic with no request (त्यो के हो?, कहाँ जान्छ?) — contrast: show_menu, ask_delivery
unclear_repeat — vague plea to repeat the words, not an order (फेरि भन्नु न) — contrast: repeat_order

GENERATE EXACTLY THESE COUNTS (TOTAL 3444 lines, one message per line):
greet 360, bare_order 300, yes_no 270, refund_status 240, unclear_repeat 225, late_delivery 210,
gibberish 180, unclear 180, order_status 165, thanks 120, refund 120, view_cart 105,
recommend 90, ask_hours 90, allergy 90, complaint 90, human 90, request_checkout 78,
goodbye 75, query_details 75, repeat_order 75, query_price 60, query_availability 45,
show_menu 45, use_saved_address 36, ask_delivery 30.

FALLBACK 4-PART SPLIT (use only if you cannot emit one file; keep contrast pairs together):
PART 1 — greet 360, unclear 180, gibberish 180, thanks 120, yes_no 270, goodbye 75
PART 2 — allergy 90, query_details 75, bare_order 300, human 90, query_availability 45,
         request_checkout 78
PART 3 — order_status 165, late_delivery 210, refund_status 240, refund 120, complaint 90,
         ask_delivery 30, view_cart 105
PART 4 — show_menu 45, recommend 90, query_price 60, ask_hours 90, repeat_order 75,
         use_saved_address 36, unclear_repeat 225

SELF-CHECK BEFORE FINISHING
(a) line count equals 3444 (or the sum of the parts you produced); (b) every line is valid JSON
with exactly the two keys; (c) "family" values only from the catalog; (d) no Latin letters,
digits or emojis in any "message"; (e) no repeated sentence; (f) both sides present for every
contrast pair inside each part. Then output ONLY the file (or its download link).
```

## Import

Save the downloaded bank under `data/generated/` (gitignored) before importing:

```bash
python -m layanep.import_bank --input <bank.jsonl> --out data/generated/ne-bank-<name>.jsonl --id-prefix ne-bank
```

Then merge into `data/reviewed/ne-decisions-v1.review.jsonl` and rebuild the
sheet as usual.
