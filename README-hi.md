# dsh-aqua-input-check — जलकृषि आदान रजिस्टर की पूर्णता और प्रतीक्षा-अवधि तिथि की जाँच

`dsh-aqua-input-check` जलकृषि आदानों का एक रजिस्टर पढ़ता है — फ़ार्म हेडर और प्रत्येक आदान प्रविष्टि की एक पंक्ति — और उसी रजिस्टर की पूर्णता तथा तिथि-गणना की जाँच करता है: क्या प्रत्येक प्रविष्टि में उसका तालाब और जाति दर्ज है, क्या नाम दर्ज होने पर आदान की मात्रा और उपयोग की तिथि दर्ज है, क्या उपयोग की तिथि भविष्य की नहीं है, क्या कटाई रजिस्टर में लिखी प्रतीक्षा-अवधि का पालन करती है, क्या पालन-प्रविष्टि में स्रोत और संगरोध प्रमाणपत्र संख्या दर्ज है, क्या आदान का प्रकार आपकी कॉन्फ़िगर की गई शब्दावली से है, और क्या बैच संख्याएँ अद्वितीय हैं।
यह तय नहीं करता कि पालन पद्धति नियमों के अनुरूप है, उत्पाद खाने के लिए सुरक्षित है, दवा उचित थी, या कोई दंड बनता है।

## यह किन सवालों का जवाब देता है

| आपका सवाल | इसका जवाब |
|---|---|
| एक प्रविष्टि में आदान का नाम है, पर तालाब और जाति के कॉलम खाली हैं। | `AQ-001` हर प्रविष्टि में `pondNo` और `species` में से कम से कम एक की अपेक्षा करता है। यह केवल देखता है कि दोनों में से एक भरा है, और यह नहीं आँकता कि वह आदान उस जाति के लिए उपयुक्त है। |
| आदान का नाम भरा है, पर मात्रा और उपयोग की तिथि खाली हैं। | `AQ-002` तब `inputQty` और `usedAt` की अपेक्षा करता है जब `inputName` भरा हो। यह देखता है कि ये कॉलम दर्ज हैं, यह नहीं कि मात्रा उचित है या दवा रोग के अनुरूप है। |
| उपयोग की तिथि `15/03/2026` लिखी है, और एक पंक्ति में अगले महीने की तिथि है। | `AQ-003` `2026-03-15` और `2026-03-15 09:30` दोनों रूप पढ़ता है; जो `usedAt` पढ़ा न जा सके वह अलग से दर्ज होता है, और जाँच-तिथि से आगे की तिथि भविष्य की तिथि के रूप में दर्ज होती है। यह प्रतीक्षा-अवधि को नहीं छूता — इस रूल पैक में कोई प्रतीक्षा-अवधि दिन ही शामिल नहीं है। |
| 1 जून को दवा दी, प्रतीक्षा-अवधि 20 दिन दर्ज है, और 15 जून को कटाई कर ली — क्या यह पकड़ में आता है? | हाँ। `AQ-004` `usedAt`, `harvestAt` और रजिस्टर में लिखे `withdrawalDays` की तुलना करता है और जितने दिन कम हैं उतने दर्ज करता है। इसका मतलब है «आपकी दर्ज प्रतीक्षा-अवधि के अनुसार कटाई जल्दी हो गई», यह नहीं कि उत्पाद असुरक्षित है — अवशेष की जाँच का परिणाम चाहिए, जो यह प्लगइन देख नहीं सकता। तीनों कॉलम भरे और पढ़ने योग्य न हों तो यह नियम कोई अवधि मान लेने के बजाय `skipped` दर्ज करता है। |
| हम जो आदान प्रकार इस्तेमाल करते हैं वह सूची में नहीं है, और कुछ भी दर्ज नहीं हुआ। | `AQ-006` `skipped` दर्ज करता है क्योंकि इस रूल पैक के साथ कोई आदान-प्रकार सूची नहीं आती: `values` तब तक खाली रहता है जब तक आप उसे कॉन्फ़िगर न करें। कॉन्फ़िगर होने पर यह देखता है कि दर्ज `inputType` आपके दिए मानों में से है। यह नहीं आँकता कि वह आदान उपयोग के लिए अनुमत है — उसके लिए प्रतिबंधित दवाओं की सूची और उत्पाद का अनुमोदन क्रमांक चाहिए। |
| एक ही बैच संख्या दो पंक्तियों में आई है। | `AQ-007` दोहराव दर्ज करता है और दोनों पंक्तियाँ बताता है। तुलना में रिक्त स्थान छोड़ दिए जाते हैं; एक ही बैच की कई आदान प्रविष्टियाँ सामान्य हैं बशर्ते वे वही बैच संख्या साझा करें — पंक्ति-संख्या कॉलम को इसके लिए दोबारा इस्तेमाल न करें। बैच संख्या कॉलम न हो तो यह चुपचाप पास होने के बजाय बताता है कि वह चल नहीं सका। |

## यह किन मानकों पर आधारित है

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
|---|---|---|
| 《水产养殖质量安全管理规定》 | 农业部令（现行令号与条号本次未核实） | AQ-001, AQ-002, AQ-005, AQ-007 |
| 《绿色食品 渔药使用准则》 | NY/T 755—2022（2022-07-11 发布、2022-10-01 实施；全部代替已废止的 NY/T 755—2013；属绿色食品系列标准；条号本次未取得） | AQ-003, AQ-004 |
| 本机构养殖生产管理口径（本机构配置） | 无统一标准（本条依据为本机构配置的类型口径） | AQ-006 |

**Boundary:** this plugin checks an **水产养殖投入品记录** for completeness and date arithmetic — that each record
names its pond and species, that a named input records its quantity and use date, that the use date is not in the
future, that harvesting respects the withdrawal period the record states, that stocking records its source and
quarantine certificate, that the input type comes from your vocabulary, and that batch numbers are unique. It does
**not** decide whether farming practice is compliant, whether the product is safe to eat, whether medication was
appropriate, or whether a penalty applies.

> ### ⚠️ What this plugin deliberately does not know
>
> **It ships no withdrawal periods.** `AQ-004` checks that the harvest date is at least as many days after the use
> date as **the record's own withdrawal-period column says**. So a finding means "**by the withdrawal period you
> recorded, harvest came N days early**" — never "this product is unsafe". Residue safety needs a test result,
> which this plugin cannot see. A record with no harvest date reports itself in `skipped` rather than assuming a
> period.
>
> **It ships no list of permitted or prohibited inputs.** `AQ-006` checks that the input type is one you
> configured; whether a product may lawfully be used requires the prohibited-drug list and the product's approval
> number, and this plugin does not go there.
>
> **Every `excerpt` in the rule pack says, in so many words, that the clause text was not obtained.** The regime
> lives in 《水产养殖质量安全管理规定》, NY 5361, NY/T 755 and GB 13078. The verification pass could not
> retrieve verbatim clause text, so the pack states the gap in the `excerpt` field itself and keeps every rule at
> `warn` or `info`. **When the texts are in hand, replace each `excerpt` with the real clause and raise `kind`
> to `direct`.**

## Compatibility

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-aqua-input-check
dsh --profile <name> --dump-config | grep 'dsh-aqua-input-check'
```

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/aqua-input-check.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-aqua-input-check
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## License

[Apache License 2.0](LICENSE) © 2026 dsh-aqua-input-check contributors.
