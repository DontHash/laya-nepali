# Nepali probe report - laya

- Generated: 2026-09-25T05:59:43.648431+00:00
- Corpus revision: ne-probe-v1
- Commit: dbfa24a
- Steps: 79
- Model correct: 55/79 (69.6%)
- Abstain: 13/17
- Latency: p50 953.4 ms | p95 1155.1 ms
- Classifier errors: 0
- Config: classifier=laya, device=cpu, threshold=0.5

## Per kind

| kind | expected | correct | predicted | false positives |
|---|---|---|---|---|
| social.greet | 4 | 3 | 5 | 2 |
| social.thanks | 4 | 3 | 4 | 1 |
| social.goodbye | 4 | 4 | 8 | 4 |
| discovery.show_menu | 6 | 4 | 4 | 0 |
| discovery.recommend | 4 | 2 | 2 | 0 |
| discovery.query | 13 | 9 | 12 | 3 |
| fulfillment.ask_hours | 4 | 3 | 3 | 0 |
| fulfillment.ask_delivery | 5 | 4 | 7 | 3 |
| fulfillment.order_status | 4 | 3 | 3 | 0 |
| ordering.view_cart | 4 | 1 | 1 | 0 |
| ordering.request_checkout | 4 | 3 | 3 | 0 |
| ordering.repeat_order | 3 | 1 | 1 | 0 |
| ordering.use_saved_address | 3 | 2 | 2 | 0 |
| none | 17 | 13 | 24 | 11 |

## Misses

- `sk-lu-greet/greet-1` (en) "hi there" - expected `social.greet`, got `abstain`
- `sk-lu-thanks/thanks-3` (ne-rom) "dhanyabad" - expected `social.thanks`, got `abstain`
- `sk-lu-menu/menu-2` (en) "what do you have?" - expected `discovery.show_menu`, got `social.greet`
- `sk-lu-menu/menu-6` (ne) "मेनु देखाउनुहोस्" - expected `discovery.show_menu`, got `social.goodbye`
- `sk-lu-recommend/recommend-3` (en) "best seller?" - expected `discovery.recommend`, got `abstain`
- `sk-lu-recommend/recommend-4` (ne) "के राम्रो छ?" - expected `discovery.recommend`, got `fulfillment.ask_delivery`
- `sk-lu-query-availability/availability-3` (ne-rom) "masala chai cha?" - expected `discovery.query`, got `abstain`
- `sk-lu-query-availability/availability-4` (ne) "तपाईंसँग भेज मोमो छ?" - expected `discovery.query`, got `fulfillment.ask_delivery`
- `sk-lu-query-details/details-1` (en) "tell me about the thali" - expected `discovery.query`, got `abstain`
- `sk-lu-query-details/details-3` (ne) "मोमोमा के छ?" - expected `discovery.query`, got `abstain`
- `sk-lu-hours/hours-3` (ne-rom) "kati baje khulcha?" - expected `fulfillment.ask_hours`, got `abstain`
- `sk-lu-delivery/delivery-1` (en) "do you deliver to Lazimpat?" - expected `fulfillment.ask_delivery`, got `discovery.query`
- `sk-lu-status/status-4` (ne) "मेरो अर्डर कहाँ छ?" - expected `fulfillment.order_status`, got `fulfillment.ask_delivery`
- `sk-lu-cart/cart-2` (en) "what's in my order?" - expected `ordering.view_cart`, got `discovery.query`
- `sk-lu-cart/cart-3` (ne-rom) "mero cart dekhaunus" - expected `ordering.view_cart`, got `abstain`
- `sk-lu-cart/cart-4` (ne) "मेरो कार्ट देखाउनुहोस्" - expected `ordering.view_cart`, got `social.goodbye`
- `sk-lu-checkout/checkout-2` (en) "i'm done, place my order" - expected `ordering.request_checkout`, got `social.goodbye`
- `sk-lu-repeat/repeat-2` (ne-rom) "feri tyahi order garna man cha" - expected `ordering.repeat_order`, got `abstain`
- `sk-lu-repeat/repeat-3` (ne) "फेरि उही अर्डर गर्नुहोस्" - expected `ordering.repeat_order`, got `abstain`
- `sk-lu-saved-address/saved-3` (ne) "सेभ गरेको ठेगाना प्रयोग गर्नुहोस्" - expected `ordering.use_saved_address`, got `abstain`
- `sk-lu-abstain/abstain-5` (en) "no thanks" - expected `abstain`, got `social.thanks`
- `sk-lu-abstain/abstain-6` (en) "does the momo have nuts?" - expected `abstain`, got `discovery.query`
- `sk-lu-abstain/abstain-10` (en) "can i talk to a human?" - expected `abstain`, got `social.greet`
- `sk-lu-abstain/abstain-13` (en) "maybe later" - expected `abstain`, got `social.goodbye`

## Method

- Corpus: `data/benchmark/ne-probe-v1.json` (ported from OrderWorkFlow `lu-probe-v1`).
- The Laya classifier runs in-process (`Agent.system_one`) with a single 16-option `choice` question; Devanagari routes to `multilingual`, Latin text to `english`.
- Metrics are model-only; composite/gap metrics from OrderWorkFlow need the deterministic dialogue classifier and are out of scope here.
- Pinned upstream: see `src/layanep/pins.py`.
