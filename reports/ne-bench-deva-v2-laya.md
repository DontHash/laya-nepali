# Nepali probe report - laya

- Generated: 2026-09-25T08:25:52.615216+00:00
- Corpus revision: ne-bench-deva-v2
- Commit: 78113ca
- Steps: 272
- Model correct: 113/272 (41.5%)
- Abstain: 53/92
- Latency: p50 406.4 ms | p95 520.0 ms
- Classifier errors: 0
- Config: classifier=laya, device=cpu, threshold=0.5

## Per kind

| kind | expected | correct | predicted | false positives |
|---|---|---|---|---|
| social.greet | 12 | 2 | 2 | 0 |
| social.thanks | 12 | 8 | 8 | 0 |
| social.goodbye | 12 | 11 | 50 | 39 |
| discovery.show_menu | 12 | 0 | 0 | 0 |
| discovery.recommend | 12 | 7 | 11 | 4 |
| discovery.query | 36 | 9 | 14 | 5 |
| fulfillment.ask_hours | 12 | 9 | 9 | 0 |
| fulfillment.ask_delivery | 12 | 5 | 43 | 38 |
| fulfillment.order_status | 12 | 4 | 9 | 5 |
| ordering.view_cart | 12 | 0 | 0 | 0 |
| ordering.request_checkout | 12 | 3 | 4 | 1 |
| ordering.repeat_order | 12 | 2 | 2 | 0 |
| ordering.use_saved_address | 12 | 0 | 0 | 0 |
| none | 92 | 53 | 120 | 67 |

## Misses

- `bb-greet/bb-greet-1` (ne) "नमस्ते हजुर" - expected `social.greet`, got `social.goodbye`
- `bb-greet/bb-greet-2` (ne) "नमस्कार दाइ" - expected `social.greet`, got `social.goodbye`
- `bb-greet/bb-greet-4` (ne) "नमस्ते है" - expected `social.greet`, got `abstain`
- `bb-greet/bb-greet-5` (ne) "नमस्कार हजुरहरू" - expected `social.greet`, got `social.goodbye`
- `bb-greet/bb-greet-6` (ne) "हेल्लो दाइ" - expected `social.greet`, got `social.goodbye`
- `pb-greet/pb-greet-1` (ne) "नमस्ते" - expected `social.greet`, got `abstain`
- `pb-greet/pb-greet-2` (ne) "नमस्कार दिदी" - expected `social.greet`, got `social.goodbye`
- `pb-greet/pb-greet-4` (ne) "नमस्ते हजुरहरू" - expected `social.greet`, got `social.goodbye`
- `pb-greet/pb-greet-5` (ne) "नमस्कार" - expected `social.greet`, got `social.goodbye`
- `pb-greet/pb-greet-6` (ne) "हेलो दिदी, कस्तो छ?" - expected `social.greet`, got `fulfillment.ask_delivery`
- `bb-thanks/bb-thanks-3` (ne) "सेकुवा राम्रो थियो, थ्याङ्क यु" - expected `social.thanks`, got `abstain`
- `bb-thanks/bb-thanks-6` (ne) "थ्याङ्क्यु हजुर" - expected `social.thanks`, got `abstain`
- `pb-thanks/pb-thanks-3` (ne) "पुरी तरकारी राम्रो, थ्याङ्क्यु" - expected `social.thanks`, got `abstain`
- `pb-thanks/pb-thanks-6` (ne) "थ्याङ्क यु दिदी" - expected `social.thanks`, got `abstain`
- `bb-goodbye/bb-goodbye-2` (ne) "पछि भेटौंला" - expected `social.goodbye`, got `abstain`
- `bb-menu/bb-menu-1` (ne) "मेनु पठाइदिनु न" - expected `discovery.show_menu`, got `fulfillment.ask_delivery`
- `bb-menu/bb-menu-2` (ne) "के के पाइन्छ त?" - expected `discovery.show_menu`, got `abstain`
- `bb-menu/bb-menu-3` (ne) "मेनु देखाउनुहोस्" - expected `discovery.show_menu`, got `social.goodbye`
- `bb-menu/bb-menu-4` (ne) "तपाईंहरूको मेनु कहाँ छ?" - expected `discovery.show_menu`, got `abstain`
- `bb-menu/bb-menu-5` (ne) "के के खाना छ हजुर?" - expected `discovery.show_menu`, got `abstain`
- `bb-menu/bb-menu-6` (ne) "मेनु पो पठाउनु न" - expected `discovery.show_menu`, got `social.goodbye`
- `pb-menu/pb-menu-1` (ne) "मेनु हेर्न पाइन्छ?" - expected `discovery.show_menu`, got `abstain`
- `pb-menu/pb-menu-2` (ne) "बिहानको मेनु पठाइदिनु" - expected `discovery.show_menu`, got `abstain`
- `pb-menu/pb-menu-3` (ne) "मेनु पठाइदिनु दिदी" - expected `discovery.show_menu`, got `fulfillment.ask_delivery`
- `pb-menu/pb-menu-4` (ne) "तपाईंको मेनु देखाउनु" - expected `discovery.show_menu`, got `social.goodbye`
- `pb-menu/pb-menu-5` (ne) "के के पाइन्छ नि?" - expected `discovery.show_menu`, got `fulfillment.ask_delivery`
- `pb-menu/pb-menu-6` (ne) "मेनु छ कि छैन?" - expected `discovery.show_menu`, got `abstain`
- `bb-recommend/bb-recommend-5` (ne) "कुन चाहिँ खान हुन्छ?" - expected `discovery.recommend`, got `abstain`
- `pb-recommend/pb-recommend-1` (ne) "बिहानको लागि के राम्रो हुन्छ?" - expected `discovery.recommend`, got `abstain`
- `pb-recommend/pb-recommend-2` (ne) "कुन खान चाहिँ मीठो छ?" - expected `discovery.recommend`, got `abstain`
- `pb-recommend/pb-recommend-5` (ne) "सबैभन्दा राम्रो बिहानको खाना कुन हो?" - expected `discovery.recommend`, got `abstain`
- `pb-recommend/pb-recommend-6` (ne) "के खानु राम्रो होला?" - expected `discovery.recommend`, got `abstain`
- `bb-price/bb-price-2` (ne) "छोइला कतिमा पर्छ?" - expected `discovery.query`, got `abstain`
- `bb-price/bb-price-3` (ne) "आलु तामाको दाम कति?" - expected `discovery.query`, got `abstain`
- `bb-price/bb-price-5` (ne) "मसला चिया कतिको हो?" - expected `discovery.query`, got `fulfillment.ask_delivery`
- `bb-price/bb-price-6` (ne) "सेकुवा कतिमा आउँछ?" - expected `discovery.query`, got `fulfillment.ask_delivery`
- `pb-price/pb-price-1` (ne) "सेल रोटीको भाउ कति?" - expected `discovery.query`, got `abstain`
- `pb-price/pb-price-2` (ne) "पुरी तरकारी कति पर्छ?" - expected `discovery.query`, got `abstain`
- `pb-price/pb-price-5` (ne) "लेमन टी कति हो?" - expected `discovery.query`, got `abstain`
- `bb-availability/bb-availability-1` (ne) "आज छोइला पाइन्छ?" - expected `discovery.query`, got `fulfillment.ask_delivery`
- `bb-availability/bb-availability-3` (ne) "आलु तामा अहिले पाइन्छ?" - expected `discovery.query`, got `fulfillment.ask_delivery`
- `bb-availability/bb-availability-4` (ne) "चिउरा छ हजुर?" - expected `discovery.query`, got `abstain`
- `bb-availability/bb-availability-5` (ne) "मसला चिया पाइन्छ नि?" - expected `discovery.query`, got `abstain`
- `bb-availability/bb-availability-6` (ne) "सेकुवा सकियो कि छ?" - expected `discovery.query`, got `abstain`
- `pb-availability/pb-availability-1` (ne) "सेल रोटी अझै छ?" - expected `discovery.query`, got `abstain`
- `pb-availability/pb-availability-4` (ne) "दही छ दिदी?" - expected `discovery.query`, got `fulfillment.ask_delivery`
- `pb-availability/pb-availability-5` (ne) "लेमन टी पाइन्छ?" - expected `discovery.query`, got `abstain`
- `pb-availability/pb-availability-6` (ne) "बिहानको खाना अहिले पाइन्छ?" - expected `discovery.query`, got `abstain`
- `bb-details/bb-details-1` (ne) "छोइलामा के के हुन्छ?" - expected `discovery.query`, got `abstain`
- `bb-details/bb-details-2` (ne) "चिकन सेकुवा कसरी बनाइन्छ?" - expected `discovery.query`, got `discovery.recommend`
- `bb-details/bb-details-3` (ne) "आलु तामामा तामा छ?" - expected `discovery.query`, got `abstain`
- `bb-details/bb-details-5` (ne) "चिउरा भुटेको हो कि कच्चा?" - expected `discovery.query`, got `abstain`
- `bb-details/bb-details-6` (ne) "सेकुवामा पिरो हुन्छ?" - expected `discovery.query`, got `abstain`
- `pb-details/pb-details-1` (ne) "सेल रोटीमा चिनी हुन्छ?" - expected `discovery.query`, got `abstain`
- `pb-details/pb-details-2` (ne) "पुरी तरकारीमा के के हुन्छ?" - expected `discovery.query`, got `abstain`
- `pb-details/pb-details-3` (ne) "आलु पराठामा मक्खन लाग्छ?" - expected `discovery.query`, got `abstain`
- `pb-details/pb-details-4` (ne) "दही घरको हो?" - expected `discovery.query`, got `abstain`
- `pb-details/pb-details-5` (ne) "लेमन टीमा चिनी हुन्छ?" - expected `discovery.query`, got `abstain`
- `pb-details/pb-details-6` (ne) "पराठामा अण्डा हुन्छ?" - expected `discovery.query`, got `abstain`
- `bb-hours/bb-hours-5` (ne) "अहिले खुला छ?" - expected `fulfillment.ask_hours`, got `discovery.query`
- `bb-hours/bb-hours-6` (ne) "आइतबार खुल्छ कि बन्द?" - expected `fulfillment.ask_hours`, got `abstain`
- `pb-hours/pb-hours-1` (ne) "कति बजेसम्म पाइन्छ?" - expected `fulfillment.ask_hours`, got `fulfillment.ask_delivery`
- `bb-delivery/bb-delivery-1` (ne) "यहाँ डेलिभरी हुन्छ?" - expected `fulfillment.ask_delivery`, got `abstain`
- `bb-delivery/bb-delivery-2` (ne) "जोरपाटीमा पुर्याउनुहुन्छ?" - expected `fulfillment.ask_delivery`, got `abstain`
- `bb-delivery/bb-delivery-3` (ne) "डेलिभरी चार्ज कति लाग्छ?" - expected `fulfillment.ask_delivery`, got `discovery.query`
- `pb-delivery/pb-delivery-2` (ne) "डेलिभरी शुल्क कति?" - expected `fulfillment.ask_delivery`, got `discovery.query`
- `pb-delivery/pb-delivery-4` (ne) "कति समयमा डेलिभरी हुन्छ?" - expected `fulfillment.ask_delivery`, got `abstain`
- `pb-delivery/pb-delivery-5` (ne) "पाटन बाहिर पठाउनुहुन्छ?" - expected `fulfillment.ask_delivery`, got `abstain`
- `pb-delivery/pb-delivery-6` (ne) "डेलिभरीको दायरा कति छ?" - expected `fulfillment.ask_delivery`, got `abstain`
- `bb-order-status/bb-status-1` (ne) "मेरो अर्डर कहाँ पुग्यो?" - expected `fulfillment.order_status`, got `fulfillment.ask_delivery`
- `bb-order-status/bb-status-3` (ne) "मेरो अर्डर अहिले कहाँ छ हजुर?" - expected `fulfillment.order_status`, got `fulfillment.ask_delivery`
- `bb-order-status/bb-status-5` (ne) "मेरो अर्डर पठाइयो कि?" - expected `fulfillment.order_status`, got `fulfillment.ask_delivery`
- `bb-order-status/bb-status-6` (ne) "अर्डर स्टेटस कस्तो छ?" - expected `fulfillment.order_status`, got `fulfillment.ask_delivery`
- `pb-order-status/pb-status-1` (ne) "मेरो अर्डर कहाँ छ दिदी?" - expected `fulfillment.order_status`, got `fulfillment.ask_delivery`
- `pb-order-status/pb-status-2` (ne) "अर्डर आउने बेला भयो, कहाँ पुग्यो?" - expected `fulfillment.order_status`, got `fulfillment.ask_delivery`
- `pb-order-status/pb-status-3` (ne) "मेरो अर्डर पठाउनुभयो?" - expected `fulfillment.order_status`, got `abstain`
- `pb-order-status/pb-status-4` (ne) "अर्डर कसले ल्याउँदै छ?" - expected `fulfillment.order_status`, got `fulfillment.ask_delivery`
- `bb-cart/bb-cart-1` (ne) "मेरो कार्ट देखाउनु न" - expected `ordering.view_cart`, got `social.goodbye`
- `bb-cart/bb-cart-2` (ne) "के के अर्डर गरेको छु?" - expected `ordering.view_cart`, got `abstain`
- `bb-cart/bb-cart-3` (ne) "अहिलेसम्मको अर्डर देखाउनुहोस्" - expected `ordering.view_cart`, got `fulfillment.order_status`
- `bb-cart/bb-cart-4` (ne) "मेरो कार्ट खोल्नु न" - expected `ordering.view_cart`, got `social.goodbye`
- `bb-cart/bb-cart-5` (ne) "अर्डरको लिस्ट पठाइदिनु" - expected `ordering.view_cart`, got `fulfillment.order_status`
- `bb-cart/bb-cart-6` (ne) "मैले के के थपेको छु?" - expected `ordering.view_cart`, got `abstain`
- `pb-cart/pb-cart-1` (ne) "मेरो अर्डर लिस्ट देखाउनु दिदी" - expected `ordering.view_cart`, got `abstain`
- `pb-cart/pb-cart-2` (ne) "कार्टमा के छ?" - expected `ordering.view_cart`, got `abstain`
- `pb-cart/pb-cart-3` (ne) "अहिलेसम्म के के राखेको छु?" - expected `ordering.view_cart`, got `fulfillment.ask_delivery`
- `pb-cart/pb-cart-4` (ne) "मेरो कार्ट हेर्न पाइन्छ?" - expected `ordering.view_cart`, got `abstain`
- `pb-cart/pb-cart-5` (ne) "अर्डरको विवरण पठाइदिनु" - expected `ordering.view_cart`, got `fulfillment.order_status`
- `pb-cart/pb-cart-6` (ne) "मैले के के अर्डर गरें?" - expected `ordering.view_cart`, got `abstain`
- `bb-checkout/bb-checkout-2` (ne) "मेरो अर्डर पक्का गर्नुहोस्" - expected `ordering.request_checkout`, got `fulfillment.ask_delivery`
- `bb-checkout/bb-checkout-4` (ne) "ल, अर्डर गरौं" - expected `ordering.request_checkout`, got `abstain`
- `bb-checkout/bb-checkout-5` (ne) "यही अर्डर पठाइदिनु" - expected `ordering.request_checkout`, got `abstain`
- `bb-checkout/bb-checkout-6` (ne) "अहिलेकै अर्डर पक्का गर्नुहोस्" - expected `ordering.request_checkout`, got `fulfillment.ask_delivery`
- `pb-checkout/pb-checkout-1` (ne) "मेरो अर्डर फाइनल गर्नुहोस्" - expected `ordering.request_checkout`, got `social.goodbye`
- `pb-checkout/pb-checkout-2` (ne) "अर्डर प्लेस गर्नुहोस् त" - expected `ordering.request_checkout`, got `abstain`
- `pb-checkout/pb-checkout-3` (ne) "ल, कन्फर्म गर्नुहोस्" - expected `ordering.request_checkout`, got `abstain`
- `pb-checkout/pb-checkout-4` (ne) "यही अर्डर अगाडि बढाउनुहोस्" - expected `ordering.request_checkout`, got `fulfillment.ask_delivery`
- `pb-checkout/pb-checkout-5` (ne) "अर्डर गरिदिनु दिदी" - expected `ordering.request_checkout`, got `fulfillment.ask_delivery`
- `bb-repeat/bb-repeat-1` (ne) "फेरि उही अर्डर गर्नुहोस्" - expected `ordering.repeat_order`, got `fulfillment.ask_delivery`
- `bb-repeat/bb-repeat-2` (ne) "अघिल्लो पटकको जस्तै पठाइदिनु" - expected `ordering.repeat_order`, got `fulfillment.ask_delivery`
- `bb-repeat/bb-repeat-3` (ne) "पहिलेको अर्डर फेरि दोहोर्याउनु" - expected `ordering.repeat_order`, got `abstain`
- `bb-repeat/bb-repeat-5` (ne) "उही अर्डर फेरि गर्नु" - expected `ordering.repeat_order`, got `abstain`
- `bb-repeat/bb-repeat-6` (ne) "हिजोको अर्डर जस्तै दिनु" - expected `ordering.repeat_order`, got `abstain`
- `pb-repeat/pb-repeat-1` (ne) "अघिल्लो जस्तै फेरि ल्याइदिनु" - expected `ordering.repeat_order`, got `fulfillment.ask_delivery`
- `pb-repeat/pb-repeat-2` (ne) "मेरो पुरानो अर्डर दोहोर्याउनु" - expected `ordering.repeat_order`, got `abstain`
- `pb-repeat/pb-repeat-4` (ne) "पहिलेको जस्तै सेल रोटी मगाउनु" - expected `ordering.repeat_order`, got `abstain`
- `pb-repeat/pb-repeat-5` (ne) "उही अर्डर फेरि पठाइदिनु" - expected `ordering.repeat_order`, got `fulfillment.ask_delivery`
- `pb-repeat/pb-repeat-6` (ne) "हिजोको अर्डर फेरि गर्नु" - expected `ordering.repeat_order`, got `fulfillment.ask_delivery`
- `bb-saved-address/bb-saved-1` (ne) "सेभ गरेको ठेगानामा पठाइदिनु" - expected `ordering.use_saved_address`, got `fulfillment.ask_delivery`
- `bb-saved-address/bb-saved-2` (ne) "पुरानै ठेगाना प्रयोग गर्नुहोस्" - expected `ordering.use_saved_address`, got `abstain`
- `bb-saved-address/bb-saved-3` (ne) "सेव गरेको ठेगाना प्रयोग गर्नु" - expected `ordering.use_saved_address`, got `abstain`
- `bb-saved-address/bb-saved-4` (ne) "मेरो पहिलेको ठेगानामै पठाउनुहोस्" - expected `ordering.use_saved_address`, got `fulfillment.ask_delivery`
- `bb-saved-address/bb-saved-5` (ne) "सेव ठेगाना नै राख्नु" - expected `ordering.use_saved_address`, got `abstain`
- `bb-saved-address/bb-saved-6` (ne) "अघिको ठेगाना लिनुहोस्" - expected `ordering.use_saved_address`, got `fulfillment.ask_delivery`
- `pb-saved-address/pb-saved-1` (ne) "सेव गरेको ठेगानामा पुर्याउनु" - expected `ordering.use_saved_address`, got `fulfillment.ask_delivery`
- `pb-saved-address/pb-saved-2` (ne) "पहिलेको ठेगाना नै प्रयोग गर्नु" - expected `ordering.use_saved_address`, got `abstain`
- `pb-saved-address/pb-saved-3` (ne) "पुरानो ठेगानामै पठाइदिनु दिदी" - expected `ordering.use_saved_address`, got `fulfillment.ask_delivery`
- `pb-saved-address/pb-saved-4` (ne) "पहिले दिएको ठेगाना राख्नु" - expected `ordering.use_saved_address`, got `fulfillment.ask_delivery`
- `pb-saved-address/pb-saved-5` (ne) "उही ठेगाना राख्नु" - expected `ordering.use_saved_address`, got `abstain`
- `pb-saved-address/pb-saved-6` (ne) "सेव गरेको ठेगाना नै हाल्नु" - expected `ordering.use_saved_address`, got `abstain`
- `bb-bare-order/bb-bare-5` (ne) "सेकुवा हाल्नु न" - expected `abstain`, got `social.goodbye`
- `bb-yes-no/bb-yesno-1` (ne) "हुन्छ" - expected `abstain`, got `social.goodbye`
- `bb-yes-no/bb-yesno-2` (ne) "हो" - expected `abstain`, got `social.goodbye`
- `bb-yes-no/bb-yesno-3` (ne) "ल हुन्छ" - expected `abstain`, got `social.goodbye`
- `bb-yes-no/bb-yesno-4` (ne) "हुन्न" - expected `abstain`, got `social.goodbye`
- `bb-yes-no/bb-yesno-5` (ne) "अहँ, पर्दैन" - expected `abstain`, got `social.goodbye`
- `bb-yes-no/bb-yesno-6` (ne) "हो त" - expected `abstain`, got `social.goodbye`
- `pb-yes-no/pb-yesno-1` (ne) "हुन्छ दिदी" - expected `abstain`, got `social.goodbye`
- `pb-yes-no/pb-yesno-2` (ne) "हो हजुर" - expected `abstain`, got `social.goodbye`
- `pb-yes-no/pb-yesno-3` (ne) "ल, ठीक छ" - expected `abstain`, got `social.goodbye`
- `pb-yes-no/pb-yesno-4` (ne) "हुन्न" - expected `abstain`, got `social.goodbye`
- `pb-yes-no/pb-yesno-6` (ne) "अहँ" - expected `abstain`, got `social.goodbye`
- `bb-allergy/bb-allergy-5` (ne) "मलाई दूधले एलर्जी छ, के खान मिल्छ?" - expected `abstain`, got `discovery.recommend`
- `bb-refund/bb-refund-1` (ne) "मेरो पैसा फिर्ता गर्नुहोस्" - expected `abstain`, got `social.goodbye`
- `bb-refund/bb-refund-2` (ne) "अर्डर रद्द भयो तर पैसा काटियो" - expected `abstain`, got `fulfillment.ask_delivery`
- `bb-refund/bb-refund-3` (ne) "रिफन्ड कहिले आउँछ?" - expected `abstain`, got `fulfillment.ask_delivery`
- `bb-refund/bb-refund-4` (ne) "डबल चार्ज भयो, फिर्ता चाहियो" - expected `abstain`, got `social.goodbye`
- `bb-refund/bb-refund-5` (ne) "पैसा फिर्ता नगरे गुनासो गर्छु" - expected `abstain`, got `social.goodbye`
- `bb-refund/bb-refund-6` (ne) "मेरो भुक्तानी फिर्ता गर्नु" - expected `abstain`, got `social.goodbye`
- `pb-refund/pb-refund-1` (ne) "पैसा फिर्ता गरिदिनु" - expected `abstain`, got `fulfillment.ask_delivery`
- `pb-refund/pb-refund-2` (ne) "नमगाएको खानाको पैसा काटियो" - expected `abstain`, got `fulfillment.ask_delivery`
- `pb-refund/pb-refund-3` (ne) "रिफन्ड गरिदिनु दिदी" - expected `abstain`, got `social.goodbye`
- `pb-refund/pb-refund-6` (ne) "रकम फिर्ता गर्नु" - expected `abstain`, got `social.goodbye`
- `bb-complaint/bb-complaint-2` (ne) "सेकुवा काँचो थियो, कस्तो खाना हो यो?" - expected `abstain`, got `discovery.recommend`
- `bb-complaint/bb-complaint-3` (ne) "अर्डर एक घण्टापछि आयो" - expected `abstain`, got `fulfillment.order_status`
- `pb-complaint/pb-complaint-1` (ne) "पराठा जलेको आयो" - expected `abstain`, got `fulfillment.ask_delivery`
- `pb-complaint/pb-complaint-2` (ne) "दही बिग्रिएको थियो" - expected `abstain`, got `social.goodbye`
- `pb-complaint/pb-complaint-3` (ne) "अर्डर ढिलो आयो दिदी" - expected `abstain`, got `fulfillment.order_status`
- `pb-complaint/pb-complaint-5` (ne) "खानामा फोहोर भेटियो" - expected `abstain`, got `ordering.request_checkout`
- `bb-human/bb-human-1` (ne) "स्टाफसँग कुरा गर्न मिल्छ?" - expected `abstain`, got `discovery.recommend`
- `pb-human/pb-human-1` (ne) "स्टाफसँग कुरा गर्न सकिन्छ?" - expected `abstain`, got `discovery.query`
- `bb-gibberish/bb-gibberish-3` (ne) "ह ह ह" - expected `abstain`, got `social.goodbye`
- `pb-gibberish/pb-gibberish-3` (ne) "हहहह" - expected `abstain`, got `social.goodbye`
- `pb-gibberish/pb-gibberish-6` (ne) "ययय" - expected `abstain`, got `social.goodbye`
- `bb-unclear/bb-unclear-1` (ne) "यो कस्तो हो?" - expected `abstain`, got `discovery.query`
- `bb-unclear/bb-unclear-5` (ne) "मलाई थाहा भएन" - expected `abstain`, got `social.goodbye`
- `bb-unclear/bb-unclear-6` (ne) "के हो यो?" - expected `abstain`, got `social.goodbye`
- `pb-unclear/pb-unclear-2` (ne) "मलाई बुझिएन" - expected `abstain`, got `social.goodbye`
- `pb-unclear/pb-unclear-4` (ne) "त्यो कुरा मिलेन" - expected `abstain`, got `social.goodbye`

## Method

- Corpus: `D:\Code\LayaNEp\data\benchmark\ne-bench-deva-v2.json`.
- The Laya classifier runs in-process (`Agent.system_one`) with a single 16-option `choice` question; Devanagari routes to `multilingual`, Latin text to `english`.
- Metrics are model-only; composite/gap metrics from OrderWorkFlow need the deterministic dialogue classifier and are out of scope here.
- Pinned upstream: see `src/layanep/pins.py`.
