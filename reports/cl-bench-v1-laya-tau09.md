# Nepali probe report - laya

- Generated: 2026-10-09T08:29:06.194682+00:00
- Corpus revision: cl-bench-v1
- Commit: f2b73f8
- Steps: 805
- Model correct: 574/805 (71.3%)
- Abstain: 259/264
- Safety false commands: 5 (5/264 on abstain steps)
- Auto-served (policy simulation): 255
- Unsafe auto-serves: 5
- ECE (answered): 0.0551
- Latency: p50 64.3 ms | p95 75.0 ms
- Classifier errors: 0
- Config: classifier=laya, device=cuda, threshold=0.9

## Per kind

| kind | expected | correct | predicted | false positives |
|---|---|---|---|---|
| social.greet | 39 | 21 | 21 | 0 |
| social.thanks | 33 | 20 | 21 | 1 |
| social.goodbye | 26 | 0 | 0 | 0 |
| discovery.show_catalog | 32 | 26 | 26 | 0 |
| discovery.recommend | 30 | 23 | 24 | 1 |
| discovery.query | 147 | 61 | 62 | 1 |
| fulfillment.ask_delivery | 36 | 27 | 29 | 2 |
| fulfillment.ask_cod | 33 | 25 | 25 | 0 |
| fulfillment.order_status | 32 | 24 | 24 | 0 |
| ordering.view_cart | 27 | 23 | 23 | 0 |
| ordering.request_checkout | 25 | 21 | 25 | 4 |
| ordering.request_exchange | 27 | 27 | 27 | 0 |
| ordering.custom_order | 29 | 6 | 6 | 0 |
| ordering.use_saved_address | 25 | 11 | 11 | 0 |
| none | 264 | 259 | 481 | 222 |

## Misses

- `bench-case-bhaktapur-stitch/cl-bank-0970-step1` (ne) "सामान हेरेर मात्र पैसा दिन पाउँछु?" - expected `fulfillment.ask_cod`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-0990-step1` (ne) "क्यास अन डेलिभरी छ कि अनलाइन मात्र?" - expected `fulfillment.ask_cod`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-0906-step1` (ne) "कुरियर चार्ज सामान अनुसार फरक हुन्छ?" - expected `fulfillment.ask_delivery`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-2037-step1` (ne) "यो ओभरकोट मेरो काँधको नाप अनुसार अल्टर गरिदिनु" - expected `ordering.custom_order`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-0846-step1` (ne) "टपको फेब्रिक चेन्ज गरेर सिलाउन मिल्छ?" - expected `ordering.custom_order`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-1318-step1` (ne) "यो कुर्ता मेरो नाप अनुसार सिलाइदिनु" - expected `ordering.custom_order`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-0826-step1` (ne) "ब्लाउजको पछाडि डोरी राखिदिनुहोला" - expected `ordering.custom_order`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-2712-step1` (ne-rom) "ok bye didi paxi linchu ma" - expected `social.goodbye`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-3128-step1` (ne-rom) "ok bye bye have a nice evening" - expected `social.goodbye`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-5223-step1` (ne-rom) "la ta solti ma bhat khayera msg thukchu pack gardai garnu bye" - expected `social.goodbye`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-1786-step1` (ne) "नमस्ते हजुर मलाई एउटा स्वेटर चाहिएको थियो" - expected `social.greet`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-3084-step1` (ne-rom) "namaskar hajur shop khulla cha ahile?" - expected `social.greet`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-0122-step1` (ne) "हिजो पठाएको सामान हिँड्यो कि छैन?" - expected `fulfillment.order_status`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-0162-step1` (ne) "पार्सल हिँडिसकेको हो त दिदी?" - expected `fulfillment.order_status`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-1563-step1` (ne) "सेतो बाहेक अरु के रङ्गमा उपलब्ध छ?" - expected `discovery.query`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-3304-step1` (ne-rom) "navy blue color ma dekhna payincha yo hoodie?" - expected `discovery.query`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-7783-step1` (en) "Is this ring pashmina ultra-fine enough to slip through a ring?" - expected `discovery.query`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-2164-step1` (ne) "यो बर्को ऊनी धागोले बनेको हो?" - expected `discovery.query`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-1682-step1` (ne) "यो कपडा कटन हो कि मिक्स हो?" - expected `discovery.query`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-2820-step1` (ne-rom) "winter ko lagi warm cha yo jacket ko material?" - expected `discovery.query`, got `discovery.recommend`
- `bench-case-bhaktapur-stitch/cl-bank-3651-step1` (ne-rom) "georgette fabric ho ki chiffon ho yo kurti ko material?" - expected `discovery.query`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-2245-step1` (ne) "यो उनिया स्विटरको कति पर्छ भनिदिनुस् न" - expected `discovery.query`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-2832-step1` (ne-rom) "yo dress paucha?" - expected `discovery.query`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-3268-step1` (ne-rom) "mom ko birthday ma dina kasto suit set thik huncha?" - expected `discovery.recommend`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-3264-step1` (ne-rom) "mero height 5 2 cha kasto maxi dress suhauchha?" - expected `discovery.recommend`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-4981-step1` (ne-rom) "drive link xa vane share handeu na heram sabai photo" - expected `discovery.show_catalog`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-4985-step1` (ne-rom) "pinterest type retro outfits haru ko link xa tapai haru ko?" - expected `discovery.show_catalog`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-2089-step1` (ne) "मेरो अघिल्लो महिनाकै ठेगानामा सामान पठाइदिनुहोला" - expected `ordering.use_saved_address`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-1026-step1` (ne) "अस्ति साडी पठाएको ठेगानामै पठाइदिनुहोला" - expected `ordering.use_saved_address`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-1046-step1` (ne) "मेरो प्रोफाइलको एड्रेस प्रयोग गर्नुस् न" - expected `ordering.use_saved_address`, got `abstain`
- `bench-case-bhaktapur-stitch/cl-bank-1725-step1` (ne) "मैले रोजेको सामानको कुल हिसाब दिनु न" - expected `ordering.view_cart`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-1672-step1` (ne) "डेलिभरी भएको बेला हातमा पैसा दिँदा चल्छ?" - expected `fulfillment.ask_cod`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-0896-step1` (ne) "वीरगन्ज पठाउन कति पैसा पर्छ हजुर?" - expected `fulfillment.ask_delivery`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-7119-step1` (en) "Can you customize the neckline of this kurta into a sweetheart neck?" - expected `ordering.custom_order`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-2209-step1` (ne) "यो कालो कोट मेरो काँधको नाप अनुसार अल्टर गरिदिनु" - expected `ordering.custom_order`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-1553-step1` (ne) "यो ड्रेस मेरो नाप अनुसार सिलाइदिनु" - expected `ordering.custom_order`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-6587-step1` (en) "That is all from my side today, goodbye!" - expected `social.goodbye`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-2702-step1` (ne-rom) "paxi kura garamla hai ahile ma ali busy bhaye" - expected `social.goodbye`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-3086-step1` (ne-rom) "namasteee online hununchha?" - expected `social.greet`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-0212-step1` (ne) "हुडीको पार्सल ट्र्याकिङ दिनु न" - expected `fulfillment.order_status`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-2882-step1` (ne-rom) "courier tracking link pathaidinu na" - expected `fulfillment.order_status`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-1392-step1` (ne) "कतिवटा कलर अपन उपलब्ध छन् यस डिजाइनमा?" - expected `discovery.query`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-2810-step1` (ne-rom) "single color matra ho ki aru pani cha hajur?" - expected `discovery.query`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-3945-step1` (ne-rom) "cream ra brown color ma stock baki cha yo trench coat ko?" - expected `discovery.query`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-7777-step1` (en) "Is the graphic print screen printed, rubber puff, or vinyl transfer?" - expected `discovery.query`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-3274-step1` (ne-rom) "yo beige trench coat ko price kati parcha hajur?" - expected `discovery.query`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-2162-step1` (ne) "यो विन्डचिटर लार्ज साइजमा पाइन्छ?" - expected `discovery.query`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-1680-step1` (ne) "बत्तीस साइजको कट्टु छ हजुर?" - expected `discovery.query`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-2546-step1` (ne) "यो मखमली जुत्ता सात नम्बरमा उपलब्ध छ?" - expected `discovery.query`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-3294-step1` (ne-rom) "XXL size ma yo kurti paucha ki paudaina?" - expected `discovery.query`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-1505-step1` (ne) "यो सर्ट उपलब्ध छ?" - expected `discovery.query`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-2201-step1` (ne) "यो ट्र्याकसूट छ?" - expected `discovery.query`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-3382-step1` (ne-rom) "mero order confirm bhayo bhane receipt send garnus" - expected `ordering.request_checkout`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-3713-step1` (ne-rom) "order place gardinus delivery address share garisake maile" - expected `ordering.request_checkout`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-4140-step1` (ne-rom) "order place gardinus delivery address drop garisake chat box ma" - expected `ordering.request_checkout`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-1360-step1` (ne) "क्याटलग पठाइदिनुस् न साडीहरूको" - expected `discovery.show_catalog`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-3869-step1` (ne-rom) "dhanyabad didi customer support ekdam babal raicha" - expected `social.thanks`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-6393-step1` (en) "Keep the shipping details identical to my last order." - expected `ordering.use_saved_address`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-1056-step1` (ne) "ठेगाना पुरानै छ सिस्टमबाट हेर्नुहोस्" - expected `ordering.use_saved_address`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-1452-step1` (ne) "अघिल्लो हप्ता पठाउनुभएको लोकेसन सुरक्षित छ त्यहीँ हाल्दिनु" - expected `ordering.use_saved_address`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-1072-step1` (ne) "पुरानै एड्रेसमा डेलिभर गर्दिनु न दिदी" - expected `ordering.use_saved_address`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-5106-step1` (ne-rom) "last time jaha rider aathiyo tehi drop garidinus ghar number tehi ho" - expected `ordering.use_saved_address`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-1432-step1` (ne) "मेरो अर्डर लिस्टमा के के थपियो?" - expected `ordering.view_cart`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-3374-step1` (ne-rom) "maile add gareko sabai items herna milxa?" - expected `ordering.view_cart`, got `abstain`
- `bench-case-biratnagar-fashion/cl-bank-0032-step1` (ne) "हुन्छ बुक गर्दिनु" - expected `abstain`, got `ordering.request_checkout`
- `bench-case-birgunj-saree/cl-bank-5694-step1` (en) "Can I schedule a specific delivery time for New Road?" - expected `fulfillment.ask_delivery`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-6884-step1` (en) "What courier company do you use to ship parcels to Dharan and Biratnagar?" - expected `fulfillment.ask_delivery`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-6324-step1` (en) "Is shipping free if I purchase two cashmere sweaters in Kathmandu?" - expected `fulfillment.ask_delivery`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-5878-step1` (en) "Is it possible to customize the kurti with long sleeves instead of sleeveless?" - expected `ordering.custom_order`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-5886-step1` (en) "Can I request custom initials embroidered on the cashmere scarf?" - expected `ordering.custom_order`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-4160-step1` (ne-rom) "fitting alteration service cha ready made kapada lai body fit banauna?" - expected `ordering.custom_order`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-2529-step1` (ne) "हस त बाइ फेरि अर्को हप्ता सम्पर्क गर्छु" - expected `social.goodbye`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-3548-step1` (ne-rom) "hii dear sanchai xau?" - expected `social.greet`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-7752-step1` (en) "Can you send a daylight video showing the true saree shade?" - expected `discovery.query`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-7733-step1` (en) "What shades of red do you have for traditional wedding sarees?" - expected `discovery.query`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-5614-step1` (en) "Is the embroidery on this lehenga silver, gold, or antique bronze?" - expected `discovery.query`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-5622-step1` (en) "What ply is this cashmere sweater?" - expected `discovery.query`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-5534-step1` (en) "What is the cost of a complete Daura Suruwal set including Dhaka topi?" - expected `discovery.query`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-6712-step1` (en) "What do you charge for altering ready-made garments bought elsewhere?" - expected `discovery.query`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-4617-step1` (ne-rom) "daura suruwal set ko total cost kati parcha topi sahit?" - expected `discovery.query`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-6720-step1` (en) "What sizes do you carry for the Daura Suruwal sets?" - expected `discovery.query`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-1775-step1` (ne) "यो कुर्ता बयालीस साइजमा छ?" - expected `discovery.query`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-4836-step1` (ne-rom) "oversized fit ho ki slim fit ho yesko shoulder sizing?" - expected `discovery.query`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-4066-step1` (ne-rom) "height 5 9 weight 75kg lai kun size lida perfect fit huncha?" - expected `discovery.query`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-7814-step1` (en) "Is size 38 in this Daura Suruwal available immediately for pickup?" - expected `discovery.query`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-5662-step1` (en) "Is size L completely sold out in this kurti?" - expected `discovery.query`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-2518-step1` (ne) "यो छालाको पेटी उपलब्ध छ?" - expected `discovery.query`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-3903-step1` (ne-rom) "bihe ko reception party ma lagauna kasto gown best hola?" - expected `discovery.recommend`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-5818-step1` (en) "Let's finalize this! I have shared my phone number and address." - expected `ordering.request_checkout`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-6228-step1` (en) "Dhanyabad for arranging same-day dispatch in Kathmandu." - expected `social.thanks`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-7518-step1` (en) "Thanks a million for reserving the pashmina shawl for me." - expected `social.thanks`, got `abstain`
- `bench-case-birgunj-saree/cl-bank-5906-step1` (en) "Use my previous shipping details for Dharan." - expected `ordering.use_saved_address`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-2582-step1` (ne) "सामान धादिङ गजुरीसम्म ल्याइदिनुहुन्छ?" - expected `fulfillment.ask_delivery`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-6021-step1` (en) "Is this pure mulberry silk or synthetic art silk posing as pure?" - expected `abstain`, got `discovery.query`
- `bench-case-chitwan-sports/cl-bank-2072-step1` (ne) "यो दौरा सुरुवाल मेरो जिउको नाप लिएर सिलाइदिनुस्" - expected `ordering.custom_order`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-1968-step1` (ne) "यो पार्टी वेयर गाउन मेरो नाप अनुसार सिलाइदिनु" - expected `ordering.custom_order`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-3732-step1` (ne-rom) "blouse ko back gala deep banauna milxa stitching ma photo pathauchu?" - expected `ordering.custom_order`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-7578-step1` (en) "Bye bye team, thanks once again!" - expected `social.goodbye`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-4976-step1` (ne-rom) "ok solti paxi kura garamla bida paxi shopping garamla" - expected `social.goodbye`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-7467-step1` (en) "Namaste! Are you currently open for inquiries?" - expected `social.greet`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-7487-step1` (en) "Namaste, wanted to check if customer service is online." - expected `social.greet`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-2141-step1` (ne) "हेलो दाइ सन्चै हुनुहुन्छ?" - expected `social.greet`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-3841-step1` (ne-rom) "namaste sir aaja outlet open cha ki chaina?" - expected `social.greet`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-2433-step1` (ne) "मेरो पार्सल अहिले कहाँ छ स्थिति बताइदिनुस्" - expected `fulfillment.order_status`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-5615-step1` (en) "Do you have bottle green in this georgette saree?" - expected `discovery.query`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-7753-step1` (en) "Does this winter wrap come in camel brown?" - expected `discovery.query`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-6797-step1` (en) "Is this cashmere sweater available in pastel pink?" - expected `discovery.query`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-4841-step1` (ne-rom) "wine red color ma cha yo saree photos heram na" - expected `discovery.query`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-3513-step1` (ne-rom) "pink color ma herna milxa yo set?" - expected `discovery.query`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-6809-step1` (en) "Does this pashmina have silk mixed into the warp for extra shine?" - expected `discovery.query`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-6297-step1` (en) "Is this Banarasi saree pure silk or art silk?" - expected `discovery.query`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-1864-step1` (ne) "यो पहेँलो सुरुवालको मूल्य कति हो?" - expected `discovery.query`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-4051-step1` (ne-rom) "yo party dress ko cost kati parne ho total?" - expected `discovery.query`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-6749-step1` (en) "Does this dress come in petite sizing for someone 5'0"?" - expected `discovery.query`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-5583-step1` (en) "Will this lehenga fit a 36DD bust comfortably?" - expected `discovery.query`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-6873-step1` (en) "Is this oversized tee ready to ship or on back-order?" - expected `discovery.query`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-6305-step1` (en) "Is the emerald green Banarasi saree in stock right now?" - expected `discovery.query`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-1624-step1` (ne) "यो जुत्ता छ?" - expected `discovery.query`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-6626-step1` (en) "Please provide photos of your semi-formal office wear kurtas." - expected `discovery.show_catalog`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-5200-step1` (ne-rom) "baggy parachute pants ko available colorway catalog share garnus na" - expected `discovery.show_catalog`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-7539-step1` (en) "Thank you kindly, enjoy the rest of your productive week." - expected `social.thanks`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-7535-step1` (en) "Thank you! The oversized tee fits exactly how I wanted." - expected `social.thanks`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-5435-step1` (en) "Thank you, you made shopping so effortless." - expected `social.thanks`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-3791-step1` (ne-rom) "tysm sis dress ekdam babal lagyo fit pani perfect cha" - expected `social.thanks`, got `abstain`
- `bench-case-chitwan-sports/cl-bank-3987-step1` (ne-rom) "thank u so much didi size ekdam fit aayo malai" - expected `social.thanks`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-2158-step1` (ne) "डेलिभरी ब्वायलाई हातमा पैसा दिँदा चल्छ?" - expected `fulfillment.ask_cod`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-3688-step1` (ne-rom) "delivery rider lai aayepachi paisa tirda huncha ktm vitra?" - expected `fulfillment.ask_cod`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-7856-step1` (en) "Can I send a Pathao rider to collect the package directly from your boutique?" - expected `fulfillment.ask_delivery`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-0803-step1` (ne) "लम्बाइ दुई इन्च घटाइदिनु पर्ने भयो" - expected `ordering.custom_order`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-0811-step1` (ne) "ढाका टोपीको गोलाइ अलि ठूलो बनाइदिनु न" - expected `ordering.custom_order`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-2941-step1` (ne-rom) "aafnai size anusar banauna k garnu parcha?" - expected `ordering.custom_order`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-6590-step1` (en) "Logging off, talk soon!" - expected `social.goodbye`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-6578-step1` (en) "Leaving the chat for now, farewell!" - expected `social.goodbye`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-6570-step1` (en) "Goodbye, looking forward to receiving the tracking details." - expected `social.goodbye`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-1351-step1` (ne) "हस त बाइ" - expected `social.goodbye`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-4276-step1` (ne-rom) "bye bro bholi payment garera screenshot pathauchu bye bye" - expected `social.goodbye`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-3237-step1` (ne-rom) "huss ta bye good night hajur" - expected `social.goodbye`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-3233-step1` (ne-rom) "pachi kura garumla ahile ma ali busy bhaye" - expected `social.goodbye`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-1556-step1` (ne) "नमस्कार हजुर सन्चै हुनुहुन्छ?" - expected `social.greet`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-2316-step1` (ne) "नमस्कार दिदी आरामै हुनुहुन्छ?" - expected `social.greet`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-3085-step1` (ne-rom) "oyee k xa khabar" - expected `social.greet`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-2805-step1` (ne-rom) "navy blue color cha yo hoodie ko?" - expected `discovery.query`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-2134-step1` (ne) "यो कट्टु कुन फेब्रिकबाट बनेको हो?" - expected `discovery.query`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-2757-step1` (ne-rom) "yo black hoodie ko price kati ho?" - expected `discovery.query`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-2416-step1` (ne) "यो ऊनी पञ्जा ठूलो साइजमा पाइन्छ?" - expected `discovery.query`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-3185-step1` (ne-rom) "XL size stock ma cha ki xaina?" - expected `discovery.query`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-1867-step1` (ne) "यो रातो कुर्ता अझै स्टकमा बाँकी छ?" - expected `discovery.query`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-4653-step1` (ne-rom) "yo piece ahile ready stock ma cha showroom ma?" - expected `discovery.query`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-4338-step1` (ne-rom) "mero height 5 4 cha kasto type ko pant suhauchha bhandinu na didi" - expected `discovery.recommend`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-3600-step1` (ne-rom) "daily college wear ko lagi comfortable kapada suggest gardinu na" - expected `discovery.recommend`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-3033-step1` (ne-rom) "mero advance payment turuntai firta dinus" - expected `abstain`, got `ordering.request_checkout`
- `bench-case-lalitpur-kids/cl-bank-1787-step1` (ne) "छिटो पठाइदिनुभयो धेरै धेरै धन्यवाद" - expected `social.thanks`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-2539-step1` (ne) "मेरो पहिलेकै ठेगानामा पार्सल पठाइदिनुहोला" - expected `ordering.use_saved_address`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-1047-step1` (ne) "अस्ति जहाँ डेलिभर भयो त्यहीँ पठाउनु" - expected `ordering.use_saved_address`, got `abstain`
- `bench-case-lalitpur-kids/cl-bank-2949-step1` (ne-rom) "last time delivery gareko location mai send garnus" - expected `ordering.use_saved_address`, got `abstain`
- `bench-case-newari-heritage/cl-bank-6318-step1` (en) "Can you deliver the package to Tribhuvan International Airport tomorrow at 6 PM?" - expected `fulfillment.ask_delivery`, got `abstain`
- `bench-case-newari-heritage/cl-bank-5920-step1` (en) "Kurta set" - expected `abstain`, got `ordering.request_checkout`
- `bench-case-newari-heritage/cl-bank-5884-step1` (en) "Can you tailor a saree blouse according to a reference photo I send?" - expected `ordering.custom_order`, got `abstain`
- `bench-case-newari-heritage/cl-bank-2554-step1` (ne) "यो जुत्ता मेरो खुट्टाको नाप अनुसार अलि खुकुलो बनाएर बनाइदिनु" - expected `ordering.custom_order`, got `abstain`
- `bench-case-newari-heritage/cl-bank-4158-step1` (ne-rom) "sleeves ali lamo banayera customized garna milcha matching kapada thapera?" - expected `ordering.custom_order`, got `abstain`
- `bench-case-newari-heritage/cl-bank-6599-step1` (en) "Leaving now, take care!" - expected `social.goodbye`, got `abstain`
- `bench-case-newari-heritage/cl-bank-5456-step1` (en) "Bye bye! Thanks again for everything." - expected `social.goodbye`, got `abstain`
- `bench-case-newari-heritage/cl-bank-6238-step1` (en) "I'll visit the Jhamsikhel shop personally this Friday. Bye!" - expected `social.goodbye`, got `abstain`
- `bench-case-newari-heritage/cl-bank-4012-step1` (ne-rom) "tata bye bye bholi address send garchu" - expected `social.goodbye`, got `abstain`
- `bench-case-newari-heritage/cl-bank-7480-step1` (en) "Namaste! Hope someone is free for a short consultation." - expected `social.greet`, got `abstain`
- `bench-case-newari-heritage/cl-bank-7488-step1` (en) "Hi! Reaching out after a recommendation from my sister." - expected `social.greet`, got `abstain`
- `bench-case-newari-heritage/cl-bank-7476-step1` (en) "Good evening! Is anyone online to take an order?" - expected `social.greet`, got `abstain`
- `bench-case-newari-heritage/cl-bank-3534-step1` (ne-rom) "namaste didi aaja shop open cha ki bida ho?" - expected `social.greet`, got `abstain`
- `bench-case-newari-heritage/cl-bank-4293-step1` (ne-rom) "oyee sis message hera na kurti set chaine bhayo" - expected `social.greet`, got `abstain`
- `bench-case-newari-heritage/cl-bank-6338-step1` (en) "Where is my courier package right now? Under name Pooja Thapa." - expected `fulfillment.order_status`, got `abstain`
- `bench-case-newari-heritage/cl-bank-5744-step1` (en) "Where is my courier package right now? Order under name Sunita Shrestha." - expected `fulfillment.order_status`, got `abstain`
- `bench-case-newari-heritage/cl-bank-6794-step1` (en) "Can I get this waistcoat dyed to match my bride's lehenga color?" - expected `discovery.query`, got `abstain`
- `bench-case-newari-heritage/cl-bank-4378-step1` (ne-rom) "lilac color ma available cha yo fleece sweatshirt ahile ko time ma?" - expected `discovery.query`, got `abstain`
- `bench-case-newari-heritage/cl-bank-6830-step1` (en) "Is this kurti made from organic hand-spun cotton?" - expected `discovery.query`, got `abstain`
- `bench-case-newari-heritage/cl-bank-6818-step1` (en) "Does the fabric shrink after gentle hand washing?" - expected `discovery.query`, got `abstain`
- `bench-case-newari-heritage/cl-bank-1625-step1` (ne) "यो सुरुवाल कुन फेब्रिकबाट बनेको हो?" - expected `discovery.query`, got `abstain`
- `bench-case-newari-heritage/cl-bank-7685-step1` (en) "What do you charge for minor hem adjustments on ready-made wear?" - expected `discovery.query`, got `abstain`
- `bench-case-newari-heritage/cl-bank-2010-step1` (ne) "यो कालो ट्राउजरको कति पर्छ भनिदिनुस् न" - expected `discovery.query`, got `abstain`
- `bench-case-newari-heritage/cl-bank-2099-step1` (ne) "यो लेगिन्स लार्ज साइजमा उपलब्ध छ?" - expected `discovery.query`, got `abstain`
- `bench-case-newari-heritage/cl-bank-7804-step1` (en) "Will you be restocking the black cashmere cardigan anytime soon?" - expected `discovery.query`, got `abstain`
- `bench-case-newari-heritage/cl-bank-5668-step1` (en) "Is the maroon velvet shawl in stock or made-to-order?" - expected `discovery.query`, got `abstain`
- `bench-case-newari-heritage/cl-bank-4850-step1` (ne-rom) "yo model baki cha bhane reserve gardinu stock ma cha?" - expected `discovery.query`, got `abstain`
- `bench-case-newari-heritage/cl-bank-2531-step1` (ne) "अफिस जानको लागि कुन पेटी सबैभन्दा टिकाउ हुन्छ?" - expected `discovery.recommend`, got `abstain`
- `bench-case-newari-heritage/cl-bank-4325-step1` (ne-rom) "saree ko latest bridal catalog pathaidinu na didi photos sahit" - expected `discovery.show_catalog`, got `abstain`
- `bench-case-newari-heritage/cl-bank-3992-step1` (ne-rom) "thank you didi mero family lai dress dherai man paryo" - expected `social.thanks`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-5449-step1` (en) "Thank you, talk to you later!" - expected `social.goodbye`, got `social.thanks`
- `bench-case-pokhara-boutique/cl-bank-7564-step1` (en) "Talk to you later once the payment clears. Goodbye!" - expected `social.goodbye`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-4005-step1` (ne-rom) "bye bro bholi bihana bank transfer garera confirm garchu" - expected `social.goodbye`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-4013-step1` (ne-rom) "huss ta hai pachi feri chat garumla bye didi" - expected `social.goodbye`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-5409-step1` (en) "Namaste, I wanted to ask about your boutique services." - expected `social.greet`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-4560-step1` (ne-rom) "sanchai hununxa didi? shopping garna aako ma" - expected `social.greet`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-6795-step1` (en) "What color is the lining fabric inside the sheer kurti?" - expected `discovery.query`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-4644-step1` (ne-rom) "multi color print matra ho ki plain solid color ni cha?" - expected `discovery.query`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-7771-step1` (en) "Is the zari thread genuine metallic thread or tested silver coating?" - expected `discovery.query`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-6695-step1` (en) "Could you quote the price for this pastel engagement gown?" - expected `discovery.query`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-6711-step1` (en) "How much is the bridal red veil with pearl lace?" - expected `discovery.query`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-6703-step1` (en) "What is the cost of international courier shipping to the UK?" - expected `discovery.query`, got `fulfillment.ask_delivery`
- `bench-case-pokhara-boutique/cl-bank-2500-step1` (ne) "यो ढाका पटुकीको मूल्य कति हो भनिदिनुस् न" - expected `discovery.query`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-6735-step1` (en) "Do you make custom plus sizes up to 4XL for ethnic wear?" - expected `discovery.query`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-6727-step1` (en) "Is size XXL available in this festive kurti design?" - expected `discovery.query`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-6875-step1` (en) "Are you out of stock on the pure gold zari Banarasi sarees?" - expected `discovery.query`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-5505-step1` (en) "I need a traditional Newari dress for a photo shoot, what do you suggest?" - expected `discovery.recommend`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-6537-step1` (en) "Thank you! Can't wait to gift this Palpali Dhaka topi to my father." - expected `social.thanks`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-5889-step1` (en) "Please deliver to the same address as my previous order." - expected `ordering.use_saved_address`, got `abstain`
- `bench-case-pokhara-boutique/cl-bank-5909-step1` (en) "Deliver to my usual apartment in Sanepa." - expected `ordering.use_saved_address`, got `fulfillment.ask_delivery`
- `bench-case-pokhara-boutique/cl-bank-6351-step1` (en) "Did the Dhaka topi get added to my order summary?" - expected `ordering.view_cart`, got `abstain`
- `bench-case-thamel-threads/cl-bank-2290-step1` (ne) "सामान हातमा परेपछि क्यास दिन मिल्छ हजुर?" - expected `fulfillment.ask_cod`, got `abstain`
- `bench-case-thamel-threads/cl-bank-1325-step1` (ne) "सामान हातमा परेपछि तिर्छु" - expected `fulfillment.ask_cod`, got `abstain`
- `bench-case-thamel-threads/cl-bank-0989-step1` (ne) "सामान हेरेर चित्त बुझेपछि पैसा तिर्छु" - expected `fulfillment.ask_cod`, got `abstain`
- `bench-case-thamel-threads/cl-bank-0889-step1` (ne) "हवाइजहाजबाट छिटो पठाउन मिल्छ कि?" - expected `fulfillment.ask_delivery`, got `abstain`
- `bench-case-thamel-threads/cl-bank-5341-step1` (ne-rom) "tweed winter coat brown M" - expected `abstain`, got `ordering.request_checkout`
- `bench-case-thamel-threads/cl-bank-7978-step1` (en) "Do you make custom matching outfits for mother and son?" - expected `ordering.custom_order`, got `abstain`
- `bench-case-thamel-threads/cl-bank-7974-step1` (en) "Can you customize the collar style of the men's bandhgala?" - expected `ordering.custom_order`, got `abstain`
- `bench-case-thamel-threads/cl-bank-0813-step1` (ne) "ट्र्याक सुटको कम्मर अलिकति कसिलो बनाइदिनु" - expected `ordering.custom_order`, got `abstain`
- `bench-case-thamel-threads/cl-bank-4719-step1` (ne-rom) "body size measurement send garda personalized banaidinu huncha?" - expected `ordering.custom_order`, got `abstain`
- `bench-case-thamel-threads/cl-bank-2707-step1` (ne-rom) "see you bye" - expected `social.goodbye`, got `abstain`
- `bench-case-thamel-threads/cl-bank-3243-step1` (ne-rom) "bye hajur arko hapta kura garumla" - expected `social.goodbye`, got `abstain`
- `bench-case-thamel-threads/cl-bank-4815-step1` (ne-rom) "huss bye ma bholi bihana final garchu address" - expected `social.goodbye`, got `abstain`
- `bench-case-thamel-threads/cl-bank-4687-step1` (ne-rom) "courier update dinus na 3 days vaisakyo message nai xaina" - expected `fulfillment.order_status`, got `abstain`
- `bench-case-thamel-threads/cl-bank-2799-step1` (ne-rom) "black bahek kun kun color cha?" - expected `discovery.query`, got `abstain`
- `bench-case-thamel-threads/cl-bank-4084-step1` (ne-rom) "pure georgette fabric ho ki synthetic chiffon ho yo kurti ko material?" - expected `discovery.query`, got `abstain`
- `bench-case-thamel-threads/cl-bank-3654-step1` (ne-rom) "pure silk saree ho ki synthetic mixed fabric banako ho?" - expected `discovery.query`, got `abstain`
- `bench-case-thamel-threads/cl-bank-7658-step1` (en) "Can you share the price of the Newari Haku Patasi complete set?" - expected `discovery.query`, got `abstain`
- `bench-case-thamel-threads/cl-bank-5250-step1` (ne-rom) "yo black windcheater ko dam kati ho solti fixed price bhannus na?" - expected `discovery.query`, got `abstain`
- `bench-case-thamel-threads/cl-bank-3626-step1` (ne-rom) "chest 42 size cha yo jacket ko ki max 40 matra ho?" - expected `discovery.query`, got `abstain`
- `bench-case-thamel-threads/cl-bank-3932-step1` (ne-rom) "XL size stock ma available cha yo jacket ko check garnus ta" - expected `discovery.query`, got `abstain`
- `bench-case-thamel-threads/cl-bank-3187-step1` (ne-rom) "38 bust size lai kun size lida ramro?" - expected `discovery.query`, got `abstain`
- `bench-case-thamel-threads/cl-bank-7798-step1` (en) "Are these pure pashmina shawls sold out or still available?" - expected `discovery.query`, got `abstain`
- `bench-case-thamel-threads/cl-bank-4394-step1` (ne-rom) "yo item ahile showroom ma baki cha ki sakiyo didi bhandinu na?" - expected `discovery.query`, got `abstain`
- `bench-case-thamel-threads/cl-bank-1345-step1` (ne) "थ्याङ्क यु सो मच" - expected `social.thanks`, got `abstain`
- `bench-case-thamel-threads/cl-bank-3866-step1` (ne-rom) "huss thank u very much quick response ko lagi hajur" - expected `social.thanks`, got `abstain`

## Method

- Corpus: `D:\Code\LayaNEp\data\benchmark\cl-bench-v1.json`.
- The Laya classifier runs in-process (`Agent.system_one`) with a single 16-option `choice` question; Devanagari routes to `multilingual`, Latin text to `english`.
- Metrics are model-only; composite/gap metrics from OrderWorkFlow need the deterministic dialogue classifier and are out of scope here.
- Pinned upstream: see `src/layanep/pins.py`.
