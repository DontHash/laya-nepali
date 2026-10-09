# Nepali probe report - laya

- Generated: 2026-10-09T08:55:14.058162+00:00
- Corpus revision: cl-bench-v1
- Commit: 93345e8
- Steps: 805
- Model correct: 766/805 (95.2%)
- Abstain: 257/264
- Safety false commands: 7 (7/264 on abstain steps)
- Auto-served (policy simulation): 365
- Unsafe auto-serves: 16
- ECE (answered): 0.0742
- Latency: p50 78.5 ms | p95 1755.4 ms
- Classifier errors: 0
- Config: classifier=laya, device=cuda, threshold=0.4

## Per kind

| kind | expected | correct | predicted | false positives |
|---|---|---|---|---|
| social.greet | 39 | 39 | 39 | 0 |
| social.thanks | 33 | 32 | 34 | 2 |
| social.goodbye | 26 | 22 | 22 | 0 |
| discovery.show_catalog | 32 | 31 | 32 | 1 |
| discovery.recommend | 30 | 29 | 30 | 1 |
| discovery.query | 147 | 133 | 135 | 2 |
| fulfillment.ask_delivery | 36 | 35 | 45 | 10 |
| fulfillment.ask_cod | 33 | 28 | 28 | 0 |
| fulfillment.order_status | 32 | 32 | 35 | 3 |
| ordering.view_cart | 27 | 26 | 26 | 0 |
| ordering.request_checkout | 25 | 25 | 31 | 6 |
| ordering.request_exchange | 27 | 27 | 27 | 0 |
| ordering.custom_order | 29 | 29 | 30 | 1 |
| ordering.use_saved_address | 25 | 21 | 21 | 0 |
| none | 264 | 257 | 270 | 13 |

## Misses

- `bench-case-bhaktapur-stitch/cl-bank-0970-step1` (ne) "सामान हेरेर मात्र पैसा दिन पाउँछु?" - expected `fulfillment.ask_cod`, got `fulfillment.ask_delivery`
- `bench-case-bhaktapur-stitch/cl-bank-0990-step1` (ne) "क्यास अन डेलिभरी छ कि अनलाइन मात्र?" - expected `fulfillment.ask_cod`, got `fulfillment.ask_delivery`
- `bench-case-bhaktapur-stitch/cl-bank-0906-step1` (ne) "कुरियर चार्ज सामान अनुसार फरक हुन्छ?" - expected `fulfillment.ask_delivery`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-7783-step1` (en) "Is this ring pashmina ultra-fine enough to slip through a ring?" - expected `discovery.query`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-2820-step1` (ne-rom) "winter ko lagi warm cha yo jacket ko material?" - expected `discovery.query`, got `discovery.recommend`
- `bench-case-bhaktapur-stitch/cl-bank-2832-step1` (ne-rom) "yo dress paucha?" - expected `discovery.query`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-3268-step1` (ne-rom) "mom ko birthday ma dina kasto suit set thik huncha?" - expected `discovery.recommend`, got `ordering.request_checkout`
- `bench-case-bhaktapur-stitch/cl-bank-1046-step1` (ne) "मेरो प्रोफाइलको एड्रेस प्रयोग गर्नुस् न" - expected `ordering.use_saved_address`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-1672-step1` (ne) "डेलिभरी भएको बेला हातमा पैसा दिँदा चल्छ?" - expected `fulfillment.ask_cod`, got `fulfillment.order_status`
- `bench-case-biratnagar-fashion/cl-bank-2702-step1` (ne-rom) "paxi kura garamla hai ahile ma ali busy bhaye" - expected `social.goodbye`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-7777-step1` (en) "Is the graphic print screen printed, rubber puff, or vinyl transfer?" - expected `discovery.query`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-1360-step1` (ne) "क्याटलग पठाइदिनुस् न साडीहरूको" - expected `discovery.show_catalog`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-6393-step1` (en) "Keep the shipping details identical to my last order." - expected `ordering.use_saved_address`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-5106-step1` (ne-rom) "last time jaha rider aathiyo tehi drop garidinus ghar number tehi ho" - expected `ordering.use_saved_address`, got `fulfillment.ask_delivery`
- `bench-case-biratnagar-fashion/cl-bank-3374-step1` (ne-rom) "maile add gareko sabai items herna milxa?" - expected `ordering.view_cart`, got `ordering.request_checkout`
- `bench-case-biratnagar-fashion/cl-bank-0032-step1` (ne) "हुन्छ बुक गर्दिनु" - expected `abstain`, got `ordering.request_checkout`
- `bench-case-birgunj-saree/cl-bank-7752-step1` (en) "Can you send a daylight video showing the true saree shade?" - expected `discovery.query`, got `discovery.show_catalog`
- `bench-case-birgunj-saree/cl-bank-7814-step1` (en) "Is size 38 in this Daura Suruwal available immediately for pickup?" - expected `discovery.query`, got `fulfillment.ask_delivery`
- `bench-case-chitwan-sports/cl-bank-6021-step1` (en) "Is this pure mulberry silk or synthetic art silk posing as pure?" - expected `abstain`, got `discovery.query`
- `bench-case-chitwan-sports/cl-bank-4976-step1` (ne-rom) "ok solti paxi kura garamla bida paxi shopping garamla" - expected `social.goodbye`, got `social.thanks`
- `bench-case-chitwan-sports/cl-bank-6873-step1` (en) "Is this oversized tee ready to ship or on back-order?" - expected `discovery.query`, got `fulfillment.order_status`
- `bench-case-lalitpur-kids/cl-bank-3688-step1` (ne-rom) "delivery rider lai aayepachi paisa tirda huncha ktm vitra?" - expected `fulfillment.ask_cod`, got `fulfillment.ask_delivery`
- `bench-case-lalitpur-kids/cl-bank-0403-step1` (ne) "प्योर पश्मिना हो कि मिक्स?" - expected `abstain`, got `discovery.query`
- `bench-case-lalitpur-kids/cl-bank-3233-step1` (ne-rom) "pachi kura garumla ahile ma ali busy bhaye" - expected `social.goodbye`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-3033-step1` (ne-rom) "mero advance payment turuntai firta dinus" - expected `abstain`, got `ordering.request_checkout`
- `bench-case-newari-heritage/cl-bank-5920-step1` (en) "Kurta set" - expected `abstain`, got `ordering.request_checkout`
- `bench-case-newari-heritage/cl-bank-6830-step1` (en) "Is this kurti made from organic hand-spun cotton?" - expected `discovery.query`, got `abstain`
- `bench-case-newari-heritage/cl-bank-6818-step1` (en) "Does the fabric shrink after gentle hand washing?" - expected `discovery.query`, got `abstain`
- `bench-case-newari-heritage/cl-bank-7804-step1` (en) "Will you be restocking the black cashmere cardigan anytime soon?" - expected `discovery.query`, got `fulfillment.ask_delivery`
- `bench-case-pokhara-boutique/cl-bank-5449-step1` (en) "Thank you, talk to you later!" - expected `social.goodbye`, got `social.thanks`
- `bench-case-pokhara-boutique/cl-bank-7771-step1` (en) "Is the zari thread genuine metallic thread or tested silver coating?" - expected `discovery.query`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-6703-step1` (en) "What is the cost of international courier shipping to the UK?" - expected `discovery.query`, got `fulfillment.ask_delivery`
- `bench-case-pokhara-boutique/cl-bank-6735-step1` (en) "Do you make custom plus sizes up to 4XL for ethnic wear?" - expected `discovery.query`, got `ordering.custom_order`
- `bench-case-pokhara-boutique/cl-bank-5909-step1` (en) "Deliver to my usual apartment in Sanepa." - expected `ordering.use_saved_address`, got `fulfillment.ask_delivery`
- `bench-case-thamel-threads/cl-bank-1325-step1` (ne) "सामान हातमा परेपछि तिर्छु" - expected `fulfillment.ask_cod`, got `fulfillment.ask_delivery`
- `bench-case-thamel-threads/cl-bank-5341-step1` (ne-rom) "tweed winter coat brown M" - expected `abstain`, got `ordering.request_checkout`
- `bench-case-thamel-threads/cl-bank-4394-step1` (ne-rom) "yo item ahile showroom ma baki cha ki sakiyo didi bhandinu na?" - expected `discovery.query`, got `fulfillment.order_status`
- `bench-case-thamel-threads/cl-bank-1345-step1` (ne) "थ्याङ्क यु सो मच" - expected `social.thanks`, got `abstain`
- `bench-case-thamel-threads/cl-bank-0053-step1` (ne) "हुन्छ दिउँसो ल्याउनुस्" - expected `abstain`, got `fulfillment.ask_delivery`

## Method

- Corpus: `D:\Code\LayaNEp\data\benchmark\cl-bench-v1.json`.
- The Laya classifier runs in-process (`Agent.system_one`) with a single 16-option `choice` question; Devanagari routes to `multilingual`, Latin text to `english`.
- Metrics are model-only; composite/gap metrics from OrderWorkFlow need the deterministic dialogue classifier and are out of scope here.
- Pinned upstream: see `src/layanep/pins.py`.
