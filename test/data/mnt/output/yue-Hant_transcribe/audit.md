# Transcription Alignment Audit

## Summary

- format: scinoephile-transcription-alignment v2
- language: yue-Hant
- ASR sources: 6
- selected VAD blocks: 33
- selected merged subtitles: 156
- references: reference
- pause encoding: one ・ per 250 ms
- merge request boundary: 4 consecutive ・

### Reference reference

- reference subtitles: 100
- whisper CER: 107.298%
- mimo CER: 121.429%
- qwen CER: 120.807%
- sensevoice CER: 110.093%
- firered CER: 159.317%
- glm CER: 116.615%
- merged CER: 127.640%
- text-aligned timing groups: 89
- candidate:reference subtitle groups: 1:1 × 66, 1:2 × 4, 2:1 × 11, 2:2 × 2, 3:1 × 3, 3:2 × 2, 4:2 × 1
- temporal micro IoU: 43.054%
- one-to-one temporal micro IoU: 41.310% (66 groups)
- mean reference-time coverage: 72.454%
- mean signed start/end error: -760/-20 ms
- mean absolute start/end error: 1043/781 ms
- unmatched candidate/reference subtitles: 41/2

## Alignments

### Block 1

```text
whisper     　歩　　　　　　　　　　　　　　　　　
mimo        阿部　　　　　　　　　　　子阿部子　　
qwen        　啊　　　　　　　　　　　　　　　　　
sensevoice  　歩　　　　　　　　　　　　　　　　こ
firered     ｉｄｏｇｏｉｄｏ　ｇｏｗｈａｔｄｏ　　
glm         ある　　　　　　　　　　　　　　　　こ
            －－－－－－－－－－－－－－－－－－－
merged      行呀　　　　行呀｜行啦行啦我好健康｜　
reference   　　　　　　　　　　　　　　　　　　　

whisper     　　　　　　行　歩　　　　　　　　　行　　　　　　・・　　　我好健　　　　　　　　康
mimo        　　　私は元気阿部子の大好きどんどん行こうさすが道・・　　　　　　　　　　　　　　　
qwen        　　　　　　狗　啊　　　　　　　　　狗　　　　　　・・　　　我係健　　　　　　　　記
sensevoice  歩　こ私は元気　歩くの大好きどんどん行こうさ　　道・・飛んネる草ら　　　　　　　　　
firered     　　　　　　　　　　　　　　　　　　　　　　　　　・・ｅｓｓｈｅｗｈａ　ｔｃ　ａｎｔ
glm         あるこ私は元気　あるこ大好きとんとう　ごう山　　道・・電車の木下坂　　　　　　　　　
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      　　　　　　　　　　　　　　　　　　行　　　　　　・・路我最鍾意快啲行｜山路｜隧道草
reference   　　　　　　　　　　　　　　　　　　　　　　　　　・・　　　　　　　　　　　　　　　

whisper     歩　行　　　　　　　　　　愛歩　　　　　　　　　　　　　慢慢　　　　　　　　　　　　　走坡道洞　窟　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　草原　一　　　　　　　　　　　　　　　歩走　　　　　　　　　　　　　
mimo        　　　　　　　　　　　　　とね　　　　　　　　　る草穴　一本　　　　　　　　　　足で背　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　こぼこじゃりび　　　　
qwen        啊　狗　　　　　　　　　　我最　　　　　　　　　　　　　喜動　　　　　　　　　　動有狗走過路碰著不　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　散巴拉一　　　　　　　　　　　　　　　本巴　　　　　　　　　　　　　
sensevoice  　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　一　　　　　　　　　　　　　　　本走にでこぼ　　　　　紅茶　　
firered     ｋ　ｅｅｐｉｄｏｎｔ　　ｋｎｏ　　　　　　　　　ｗｔｈ　ａｔｉｓｔｏｋｅｅｐｄｏｎｔｄｏｎｔｙｏｕｇｏｓａｋａｍｉｃｈｉｋｏｎａｌｕｋｕｓａａｐａｒａｙｉｂｏｎｇｂａｓｈｉｔｉｓｅ　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　
glm         　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　日　　　　　　　　　　　　　　　本橋に세계를　　　　　쓰고쓰자
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      地｜行啦行啦我最精神｜行路我最鍾意快快行｜斜路隧道草地｜　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　一條獨木橋凹凸沙石路｜哩｜咪｜係　　　　　　　　　　　　　　　
reference   　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　

whisper     　
mimo        　
qwen        　
sensevoice  　
firered     　
glm         리
            －
merged      　
reference   　

whisper     　　
mimo        　　
qwen        　　
sensevoice  　で
firered     　　
glm         미　
            －－
merged      　　
reference   　　

whisper     　　　　　絲・・綱　　木砂路　　　　　　　　　　　　　　　　　　　　　　　　　　　　
mimo        　　　　　　・・　　　　　米　　　　　　　　　　　　　　　　　　　　　　　　　　　奇
qwen        　　　　　士・・呢一個木頭調　　　　　　　　　　　　　　　　　　　　　　　　　　　離
sensevoice  道雲없이く　・・　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　く
firered     　　　　　ｋ・・ｏｍｏｋｏｔ　ａｄｉ籍咕嚕嚕咕嚕咕嚕咕嚕咕嚕咕嚕咕嚕咕嚕咕嚕咕嚕咕嚕
glm         　　　　　　・・　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      　　　　　　・・呢一個木頭人｜　　　　　　　咕嚕咕嚕　　　　　　　　　　咕嚕咕嚕咕　
reference   　　　　　　・・　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　

whisper     　雲下　　　　　　　　　　　　　　　　　　　　
mimo        咕嚕咕嚕咕　　　　　　　　　　　　　　　　　　
qwen        別雲朵酥脆　　　　　　　　　　　　　　　　　　
sensevoice  って下り道　　　　　　　　　　　　　　　　　　
firered     咕嚕咕嚕咕嚕咕嚕　咕嚕咕嚕咕嚕咕嚕咕嚕咕嚕咕嚕
glm         　　　　　　　　　　　　　　　　　　　　　　　
            －－－－－－－－－－－－－－－－－－－－－－－
merged      　　　　　　　嚕｜咕嚕咕嚕咕嚕　　　　　　　　
reference   　　　　　　　　　　　　　　　　　　　　　　　

whisper     下　　路　　　　　　　　　　　　　　　　　　　　　　　　　　
mimo        咕得古達　　　　　　　　　　　　　　　　　　　　　　　　　利
qwen        孤　　單　　　　　　　　　　　　　　　　　　　　　　　　　離
sensevoice  　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　
firered     咕嚕咕嚕咕嚕咕嚕咕嚕　咕嚕咕嚕咕嚕咕嚕咕嚕咕嚕咕嚕　咕嚕咕嚕
glm         　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      　　　　咕嚕咕嚕咕嚕｜咕嚕咕嚕咕嚕咕嚕咕嚕咕嚕咕嚕｜咕嚕咕　
reference   　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　

whisper     　　　　　　　　　　　　　　　　　　・・・
mimo        米奇　　　　　　　　　　　　　　　　・・・
qwen        　別　　　　　　　　　　　　　　　　・・・
sensevoice  　　　　　　　　　　　　　　　　　　・・・
firered     咕嚕咕嚕咕嚕咕嚕咕嚕咕嚕　咕嚕咕嚕　・・・
glm         　　　　　　　　　　　　　　　　　　・・・
            －－－－－－－－－－－－－－－－－－－－－
merged      　嚕咕嚕咕嚕咕嚕咕嚕咕嚕｜咕嚕咕嚕｜・・・
reference   　　　　　　　　　　　　　　　　　　・・・
```

### Block 2

```text
whisper     　　　
mimo        　　　
qwen        　　　
sensevoice  　歩こ
firered     ｉ　　
glm         あるこ
            －－－
merged      行啦行
reference   　　　

whisper     歩行歩行我好健康　歩行　　　　　　　　　　大好　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　趕快走狗　　　　　　　　　　狗　　　　出來吧　　　　　　　　探險試　　　　　　　　用林　　　　　野到　　　　　　　・・　　　　　　　　　　　　　　　　　　　　　　　　
mimo        阿部子阿部子　　　　　　私を元気阿部子の　大好き　　　ど　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　んどん　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　行こう　傷も・・病も全部お願い感謝　　　しようはやしの熊嬉し　　
qwen        啊狗啊狗我係健記　啊狗都　　　　　　　　　大好き　　　ど　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　んどん遛狗皮　　　　　　膚也大氣　　　　也別帶　　　　　　我嚟探險士哦　　　　　　黑沙的　　　　　奧特曼　　　　　　・・　　　　　　　　　　　　　　　　　　　　　　　　
sensevoice  　歩子　　　　　　　　　私は元気　歩くの　大好き　　とど　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　行こうキスも・・歌も出てお　い　　でた　しを林　　　の　　　く前
firered     　　　　　　　　　　　　　　　　　ｄｏｇｏｉｄｏｇｏｗｈ　ａｔｄ　　　　　　　　ｏｅｓｓｈ　　　　　　　　　　　　ｅｗｈａｔｃａｎｔｋ　ｅｅｐｉｄｏｄｏｋｎｏｗｔｈａｔｉｓｔｈｅｋｅｙｄｏｎｔｄｏｎｔｙｏｕｇｏｉｔｓｔｈｅｎｅｍｏｔｉｍｅｔｏｋｅｅｐｍｏｖｉｎｇｔｈｅｎｔｈｅｒｅｓａｌｌ　　　　　　・・　　　　　　　　　　　　　　　　　　　　ｔｏ　　
glm         あるこ　　　　　　　　　私は元気あるこのお大好きとっとと　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　行こう　昔も・・今も出てお　い　　でたけしよう　　村の　　　奧深
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      啦　　　我好健康｜　　　　　　　　　行路我最鍾意快啲行啦｜斜路隧道草地｜獨木橋凹凸不平嘅砂石路｜穿過蜘蛛網落斜路｜森林入面自古以來住住｜　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　有好多朋　　　　　　・・　　　　　　　　　　　　　　　　　　　　　　　　
reference   　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　・・　　　　　　　　　　　　　　　　　　　　　　　　

whisper     　・　　　　　　　　　　　　　　　　　　　　　　　　　
mimo        い・な友達　が　さ　嬉　　　　　　　　　　　　　し　　
qwen        　・　去滿　　　　　　　　　　　　　　　　　　　　　　
sensevoice  　・　友達たく　さ　嬉　　　　　　　　　　　　　しいい
firered     ｍ・ｏｒｒｏｗ　ｗｏｎｔｙｏｕｄａｎｃｅｗｉｔｈｍｅｔ
glm         い・　友達たく　さん喜　　　　　　　　　　　　　し　い
            －－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      　・　友真開心｜　　　　　　　　　　　　　　　　　　有
reference   　・　　　　　　　　　　　　　　　　　　　　　　　　　

whisper     　友人多開心　　　　　　　　　
mimo        　　　　　　　　　　　　　　　
qwen        地友達滿地　　　　　　　　　　
sensevoice  な友達ちたく　さ　　　　　　　
firered     ｏｍｏｒｒｏ　ｗｗｏｎｔｙｏｕ
glm         今友達　たく　さ　　　　　　　
            －－－－－－－－－－－－－－－
merged      朋友　多開心｜　　　　　　　　
reference   　　　　　　　　　　　　　　　

whisper     　　　　　　　　　・　　
mimo        　　　　　　　　　・　　
qwen        　　　　　　　歡　・喜　
sensevoice  　　　　　　　　　・嬉　
firered     ｄａｎｃｅｗｉｔ　・ｈ　
glm         　　　　　　　ん　・喜　
            －－－－－－－－－－－－
merged      　　　　　　　歡｜・喜｜
reference   　　　　　　　　　・　　

whisper     　　　　　　　　　　　　　　　　　　　　　友人多　開
mimo        　　　　　　　　　　　　　　　　　　　　　い　　　　
qwen        滿地　　　　　　　　　　　　　　　　　　　友達　　滿
sensevoice  しい　　　　　　　　　　　　　　　　　　　い　　　　
firered     ｍｅｔｏｍｏｒｒｏｗｗｏｎｔｙｏｕｄａｎｃｅｗｉ　ｔ
glm         しい　　　　　　　　　　　　　　　　　　　　　　　　
            －－－－－－－－－－－－－－－－－－－－－－－－－－
merged      　　　　　　　　　　　　　　　　　　　滿地友達滿｜心
reference   　　　　　　　　　　　　　　　　　　　　　　　　　　

whisper     心　　　・・・
mimo        　　な　・・・
qwen        地歡喜　・・・
sensevoice  　　な　・・・
firered     ｈｍｅ　・・・
glm         　　今　・・・
            －－－－－－－
merged      地歡喜｜・・・
reference   　　　　・・・
```

### Block 3

```text
whisper     姐姐呀姐姐點解咁耐都仲　　　未到　嘅　・你唔好噉啦食完粒糖呢就到㗎喇　・・・點解　
mimo        姐姐啊姐姐點解咁耐都仲　　　未到　嘅　・你唔好咁啦食完粒糖咧就到噶啦　・・・　　　
qwen        姐姐啊姐姐點解咁耐都仲　　　未到　嘅　・你唔好咁啦食完粒糖咧就到噶啦　・・・就食　
sensevoice  姐姐啊姐姐點解咁耐都仲　　　未到　噶　・你唔好咁啦食完粒糖啦就到噶啦　・・・　　　
firered     姐姐啊姐姐點解咁耐都仲　　　未到　嘅　・你唔好咁啦食完粒糖咧就到噶啦　・・・　　　
glm         姐姐啊姐姐點解咁耐都仲　　　未到　㗎　・你唔好咁啦食完粒糖咧就到㗎啦　・・・　　　
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      姐姐呀姐姐點解咁耐都仲　　　未到　嘅｜・你唔好咁啦食完粒糖呢就到㗎喇｜・・・　　　
reference   　　　　　　　　為何那麼久還未到｜　　・你不　　　要這樣糖　　吃完就　・・・會到｜
```

### Block 4

```text
whisper     爸爸何　時才到　・・吃完　這粒糖之後　　・　　　轉完這個彎之後呢　・・　就會到的了　・・・
mimo        爸Ｂ啊幾時先到　・・噶食埋呢粒糖之後啦　・　　　轉埋呢個彎之後咧　・・　就會到噶啦　・・・
qwen        爸啲啊幾時先到　・・噶食埋呢粒糖之後啦　・　　　轉埋呢個彎之後咧　・・　就會到噶啦　・・・
sensevoice  大啲啊幾時先到　・・噶食埋呢粒蚌之後啦　・　　　轉埋呢個彎之後呢　・・　就會到噶啦　・・・
firered     爸啲啊幾時先到　・・噶食埋呢粒糖之後啦　・　　　轉埋呢個彎之後咧　・・誒就會到噶啦　・・・
glm         爸爸啊幾時見到　・・噶食埋呢粒糖之後啦　・　　　轉埋呢個彎之後咧　・・誒就會到噶啦　・・・
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      爸爸啊幾時先到｜・・　食埋呢粒糖之後啦｜・　　　轉埋呢個彎之後咧｜・・　就會到㗎啦｜・・・
reference   爸爸何　時才到｜・・　　　　　　多吃一　・粒糖｜轉了這個彎　　　　・・　就　到　了｜・・・
```

### Block 5

```text
whisper     屎空氣咁清晨監　視媽咪　養病嘅　・・・
mimo        　小葵咁識得家　姐媽咪　養大嘅　・・・
qwen        你好系咁清心今日　冇咩　人帶嘅　・・・
sensevoice  只好企咁清晒三　晒媽咪　養大嘅　・・・
firered     啲空氣咁清新啱　晒媽咪　養病噶　・・・
glm         你好系咁清曉今日系媽咪　餵飽嘅　・・・
            －－－－－－－－－－－－－－－－－－－
merged      啲空氣咁清新啱　晒媽咪　養病㗎｜・・・
reference   　　　這兒的空氣很清新｜　　　　・・・
```

### Block 6

```text
whisper     那
mimo        誒
qwen        誒
sensevoice  誒
firered     誒
glm         誒
            －
merged      　
reference   　

whisper     　個是誰　呢　・・是　　尤親叔叔當　・然很　快就到　了　　
mimo        嗰個系邊個咧　・・系　　郵差叔叔啊　・佢　好快就到　噶啦　
qwen        嗰個系邊個咧　・・系　　油餐叔叔啊　・梗繫好快就到　噶啦　
sensevoice  嗰　系邊個呢　・・系　　油餐叔叔啊　・梗繫好快就到　噶啦　
firered     　個系邊個咧　・・系　　郵差叔叔啊　・梗繫好快就到　噶啦　
glm         嗰個　邊個咧　・・系　　油茶叔叔啊　・梗繫好快就到　噶啦　
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      嗰個係邊個咧｜・・係　　郵差叔叔啊｜・梗係好快就到　㗎啦｜
reference   　　　那個　　・・是誰｜郵差叔叔　　・一定很快就到｜　　　

whisper     尤親叔叔你好嗎　你　・・好
mimo        郵差叔叔你好嘛　誒　・・　
qwen        油餐叔叔你好嗎　誒　・・　
sensevoice  油餐叔叔你好嗎　啊　・・　
firered     郵差叔叔你好嗎　唉　・・　
glm         油茶叔叔你好嘛　　　・・　
            －－－－－－－－－－－－－
merged      郵差叔叔你好嗎　誒｜・・　
reference   郵差叔叔你好嗎｜　　・・　

whisper     我是大卷草子吃　　　　多多子狗　・・・
mimo        我係大軟兔子啊　　　請多多指教　・・・
qwen        我係大卷手指啊　　　請多多指教　・・・
sensevoice  我係大卷兔子啊　　　等多得屎噶　・・・
firered     我係大卷兔子啊　　　請多多指教　・・・
glm         我係大隻叔叔啊　　　請多多指教　・・・
            －－－－－－－－－－－－－－－－－－－
merged      我係大隻兔子啊　　　請多多指教｜・・・
reference   我是大卷草子你好嗎｜請多多指教｜・・・
```

### Block 7

```text
whisper     係小朋友你好嘛你屋企人喺　　咩度啊　・・係對面　做緊　　嘢　・・・我唔　虧晒你　喎　
mimo        誒小朋友你好嘛你屋企人喺唔　喺度啊　・・喺對面　做緊　　嘢　・・・好唔　該晒你　　　
qwen        誒小朋友你好嘛你屋企人喺　　咪度啊　・・誒對面　做緊　　嘢　・・・我唔　該晒你　喎　
sensevoice  誒小朋友你好嗎你屋企人喺　　咩度啊　・・哎對明　族緊　　嘢　・・・我唔　該晒你　　　
firered     誒小朋友你好嘛你屋企人喺　　邊度啊　・・喺對面　做緊　　嘢　・・・好唔　該晒你　　　
glm         喂小明有你好嗎你屋企人喺　　咩度啊　・・喂對面　做緊　　嘢　・・・我唔　該曬你　喎　
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      喂小朋友你好嗎你屋企人喺　　邊度啊｜・・喺對面　做緊　　嘢｜・・・好唔　該晒你　喎｜
reference   　　　　你好小朋　　　　友｜你家人　・・在家嗎｜他們在對面　・・・幹活｜多謝你｜　　

whisper     喂咁多位你哋好嘛　・我係啱啱搬嚟嘅大卷　啊　・・・請多多指教　・・・
mimo        喂咁多位你哋好嘛　・我係啱啱搬嚟嘅大卷　啊　・・・請多多指教　・・・
qwen        喂咁多位你哋好嘛　・我係啱啱搬嚟嘅大卷　啊　・・・請多多指教　・・・
sensevoice  喂咁多位你哋好嗎　・我係啱啱搬嚟嘅大卷　啊　・・・請多多指教　・・・
firered     喂咁多位你哋好嘛　・我係啱啱搬嚟嘅大卷　啊　・・・請多多指教　・・・
glm         喂咁多位你哋好嗎　・我係啱啱搬嚟嘅大卷　啊　・・・請多多指教　・・・
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      喂咁多位你哋好嘛｜・我係啱啱搬嚟嘅大卷　啊｜・・・請多多指教｜・・・
reference   　　　　大家好嗎｜・我是剛剛搬來的大卷｜　　・・・請多多指教｜・・・
```

### Block 8

```text
whisper     唔怕走佢唔好聲　　　　　　　咩・・・　　欸　唔該晒你喎　・・・
mimo        誒　　　　　　　　　　　　　　・・・　　　　唔該晒你喎　・・・
qwen        　　我爸　　　　　走　去唔做咩・・・　　哎　唔該晒你　　・・・
sensevoice  　　酒誒　　　　　　　　　　　・・・　　　　唔該晒你　　・・・
firered     抓着我了怎麼都分　呢　　　　　・・・　　哎　唔該晒你　　・・・
glm         　　　　　　　　　　　　　　　・・・　　喂　唔該曬你喎　・・・
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      　　我爸爸走咗　　　　去　做咩・・・呀｜喂　唔該晒你喎｜・・・
reference   　　女兒人家都不害羞｜和你很熟・・・絡　嗎｜　　　　　　・・・
```

### Block 9

```text
whisper     我哋終於到啦　嘩好　
mimo        我哋終於到啦　　好　
qwen        我哋終於到啦　　好　
sensevoice  我哋終於到啦　　好　
firered     我哋終於到啦　　　　
glm         我哋終於到啦　　　　
            －－－－－－－－－－
merged      我哋終於到啦｜　好｜
reference   我們終於到　　　　　

whisper     嘢　等埋　喇　・・・　唔好咁　　　　　心急　呀　
mimo        嘢　　好　嘢　・・・　唔好咁　　　　　心急　啊　
qwen        呀　等埋　呀　・・・　唔好咁　　　　　心急　啊　
sensevoice  　　得系　啊　・・・　唔好咁　　　　　心急　啊　
firered     　　　　　　　・・・　唔好咁　　　　　心急　啊　
glm         　　　　　　　・・・　　冇咁　　　　　心急　啊　
            －－－－－－－－－－－－－－－－－－－－－－－－
merged      喂　等埋　喇｜・・・　唔好咁　　　　　心急　呀｜
reference   了｜真好｜呀　・・・等等我呀｜不用那麼心急｜　　

whisper     你睇下　河好靚呀　係咩　
mimo        你睇下啲海好靚啊　系咩　
qwen        你睇　　住好靚啊　系咩　
sensevoice  你睇　　住好靚啊　系咩　
firered     你睇　　見好靚啊　系咩　
glm         你睇　見佢好靚啊　系咩　
            －－－－－－－－－－－－
merged      你睇吓呢度好靚呀　係咪｜
reference   　　這條河好美呀｜是呀｜

whisper     你見唔見到有魚呀　・・冇㗎你個緊字眼呀　因住　　　　　戴眼鏡呀　
mimo        你見唔見到有魚啊　・・冇噶你　一陣先啊　戴住　　　　　副眼鏡啊　
qwen        你見唔見到有魚啊　・・冇嘅你個近視眼咧　因住　　　　　戴眼鏡啊　
sensevoice  你見唔見得有雨啊　・・冇噶你嗰　陣眼都　　住　　　　　戴眼鏡啊　
firered     你見唔見得有魚啊　・・冇噶你個近視眼都　一住　　　　　戴眼鏡啊　
glm         你見唔見到有魚啊　・・冇嘅你個緊視眼咧　一直　　　　　戴眼鏡啊　
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      你見唔見到有魚呀｜・・冇㗎你個近視眼咧　因住　　　　　戴眼鏡呀｜
reference   你　　見到有魚嗎｜・・　　為何我看不見｜你的近視眼小心戴眼鏡呀｜

whisper     小心唔好跌落河呀　・嗯　・・・　去睇下　屋靚唔靚　囉嗯・・・
mimo        小心唔好跌落河啊　・嗯　・・・啊去睇下間屋靚唔靚　咯啊・・・
qwen        小心唔好跌落河啊　・嗯　・・・啊去睇下　我靚唔靚　咯　・・・
sensevoice  小心唔好跌落河啊　・嗯　・・・啊佢睇緊　我靚唔靚　　　・・・
firered     小心唔好跌落河啊　・嗯　・・・啊去睇間　屋靚唔靚　咯啊・・・
glm         小心唔好跌落河啊　・嗯　・・・啊佢睇見佢個靚唔靚　咯　・・・
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      小心唔好跌落河呀｜・嗯｜・・・啊去睇下間屋靚唔靚｜　　・・・
reference   小心不要掉下河呀｜・　　・・・　　　　　　　　　　　　・・・
```

### Block 10

```text
whisper     　　　把電眼抬下啦　　　　　　　　　　
mimo        　　　把電　抬好了　　　　　　　　　　
qwen        　　　　快點睇下啦　啊啊啊　　　　　啊
sensevoice  　　　快啲去睇下啦　　　　　　　　　　
firered     啊啊啊把敵人抬下來　　　啊　　　　　啊
glm         　　　把電影抬下來　　　　　　　　　　
            －－－－－－－－－－－－－－－－－－－
merged      　　　快啲去睇下啦｜　　　　　　　　　
reference   　　　　　　　好漂　亮呀過去看看｜哈哈

whisper     　　　　　　　　　・・・　　　　　　・・・
mimo        　　　　　　　　　・・・　　　　　　・・・
qwen        啊啊啊　啊啊　啊啊・・・啊啊　啊啊　・・・
sensevoice  　　　　　　　　　・・・　　　　　　・・・
firered     啊啊啊　啊啊　啊啊・・・啊啊　啊　　・・・
glm         　　　　　　　　　・・・　　　　　　・・・
            －－－－－－－－－－－－－－－－－－－－－
merged      　　啊　啊啊｜啊啊・・・啊啊｜啊啊｜・・・
reference   真好哈｜　　　　　・・・　　　　　　・・・
```

### Block 11

```text
whisper     嘩咁夠　嘅・・・　
mimo        哇咁舊　嘅・・・啊
qwen        哇咁夠　嘅・・・　
sensevoice  哇咁舊　嘅・・・　
firered     哇咁舊　嘅・・・吓
glm         哇咁夠　嘅・・・　
            －－－－－－－－－
merged      哇咁舊｜　・・・　
reference   　　　　　・・・　
```

### Block 12

```text
whisper     都怪我噉
mimo        　拐我幹
qwen        　鬼佬咁
sensevoice  　鬼咁咁
firered     　怪哥咁
glm         　喂佢咁
            －－－－
merged      　　　　
reference   　　　　

whisper     　呀係呀真　係呀　　・・・
mimo        嘛啊來　　　　　　啦・・・
qwen        　啊吓點　　　啊　　・・・
sensevoice  　啊你啊　　你啊　　・・・
firered     　啊唉第　　一次見啦・・・
glm         　啊系啊　　系啊　　・・・
            －－－－－－－－－－－－－
merged      　呀係呀真｜　　　　・・・
reference   　　　　　　　　　　・・・
```

### Block 13

```text
whisper     甚麼這麼化學的好像雙臘一樣　・・・　　　
mimo        　　乜佢翻學噶好似上林咁啊　・・・　　　
qwen        　　唔咁化學噶好似手林咁啊　・・・　　　
sensevoice  　　乜咁化學噶好似想諗咁啊　・・・　　　
firered     　　乜咁化學噶好似想冧咁啊　・・・　　　
glm         　　咩咁翻學噶好似想諗咁啊　・・・　　　
            －－－－－－－－－－－－－－－－－－－－
merged      　　乜咁化學㗎好似雙眼咁呀｜・・・　　　
reference   　　　　　那麼兒戲像是快塌　・・・下來｜
```

### Block 14

```text
whisper     　　咦
mimo        　　　
qwen        　　　
sensevoice  　　　
firered     　　　
glm         　　　
            －－－
merged      　　　
reference   次子　

whisper     咦咦　
mimo        　啊　
qwen        　啊　
sensevoice  　　　
firered     　　　
glm         　　　
            －－－
merged      咦啊｜
reference   　　　

whisper     你睇下　・嗯　
mimo        你睇下　・啊　
qwen        你睇下　・啊　
sensevoice  你睇下　・　　
firered     你睇下　・　　
glm         你睇下　・爬　
            －－－－－－－
merged      你睇下｜・啊｜
reference   你看看　・那　

whisper     柏樹　呀　・・嘩　
mimo        棵樹　啊　・・哇　
qwen        棵樹　啊　・・哇　
sensevoice  啪樹　啊　・・哇　
firered     棵樹　啊　・・哇　
glm         　樹　啊　・・　　
            －－－－－－－－－
merged      棵樹　呀｜・・嘩｜
reference   棵樹｜好　・・高　

whisper     　　　　　　爸爸話我哋小朋友嘅成就　第二日好似呢棵樹噉呀　・・　即係點呀　・要好似佢咁高咁大呀　・・・啊啊啊　
mimo        　　　　　　爸Ｂ話我哋小朋友嘅成就　第日又好似呢棵樹咁啊　・・　即系點啊　・要好似佢咁高咁大　　・・・　　啊　
qwen        　　　　　　爸邊話我哋小朋友嘅成就　第日又好似呢棵樹咁啊　・・　即系點啊　・要好似佢咁高咁大　　・・・　　啊　
sensevoice  　　　　　　爸ｂ話我哋小朋友嘅成就　但日又好似呢棵樹咁啊　・・一腳系點啊　・咦好似佢咁高咁大　　・・・　　　　
firered     　　　　　　爸爸話我哋小朋友嘅成就　第日又好似呢棵樹咁啊　・・　即系點啊　・要好似佢咁高咁大　　・・・　　啊　
glm         　　　　　　爸比話我哋小朋友嘅成就　第二就好似呢棵樹咁啊　・・　即系點啊　・亦好似佢咁高咁大　　・・・　　啊　
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      　　　　　　爸爸話我哋小朋友嘅成就｜第日又好似呢棵樹咁呀｜・・　即係點呀｜・要好似佢咁高咁大呀｜・・・　　啊｜
reference   好大呀看看｜爸爸說我們小朋友的成就｜　日後要像這棵樹那樣｜・・　　　　　　・　　　那麼高　大呀｜・・・　　　　
```

### Block 15

```text
whisper     爸比呀呢棵係咩　樹　嚟㗎　
mimo        爸Ｂ啊呢棵系咩　樹　嚟噶　
qwen        爸Ｂ啊呢棵系咩　樹　嚟噶　
sensevoice  爸ｂ啊呢個系咩　樹　嚟噶　
firered     爸ｂ啊呢棵系咩　樹　嚟噶　
glm         爸爸啊你個係咩　樹　嚟㗎　
            －－－－－－－－－－－－－
merged      爸Ｂ呀呢棵係咩　樹　嚟㗎｜
reference   爸爸呀這棵是什麼樹｜　　　

whisper     哦係橡樹　啊　橡樹　啊　・・係咪大笨橡邊嘅樹啊　
mimo        哦系橡樹　啊　橡樹　　　・・系咪大笨象變嘅樹啊　
qwen        哦系橡樹　啊　橡樹　啊　・・系咪大笨象俾嘅樹呀　
sensevoice  哦系橡樹　啊　橡樹　　　・・系咪大笨象俾嘅樹啊　
firered     哦系橡樹　啊　橡樹　　　・・系咪大笨象邊嘅樹啊　
glm         哦係樟樹　啊　樟樹　　　・・係咪大笨樹邊嘅樹啊　
            －－－－－－－－－－－－－－－－－－－－－－－－
merged      哦係橡樹　啊｜橡樹　啊｜・・係咪大笨象變嘅樹啊｜
reference   　是橡樹｜　　橡樹｜　　・・　　大笨象變的樹嗎｜

whisper     啊　・・・啊　
mimo        　　・・・　　
qwen        　　・・・　　
sensevoice  啊　・・・　　
firered     　　・・・　　
glm         　　・・・　　
            －－－－－－－
merged      啊｜・・・啊｜
reference   　　・・・　　
```

### Block 16

```text
whisper     　　　小心啲呀　
mimo        哎哎呀小心啲喎　
qwen        　哎呀小心啲啊　
sensevoice  　哎啊小心啲　　
firered     　哎呀小心啲啊　
glm         　哎呀小心啲喎　
            －－－－－－－－
merged      　哎呀小心啲喎｜
reference   　　　小心　點｜

whisper     有粒種子呀　
mimo        有粒種子啊　
qwen        有粒種子啊　
sensevoice  有粒種子啊　
firered     有粒種子啊　
glm         有粒種子啊　
            －－－－－－
merged      有粒種子啊｜
reference   有粒種子呀｜

whisper     　・畀我呀唔畀唔畀唔　畀　衰咗我差　　食雞鼻　・・・
mimo        吓・俾我啊唔俾唔俾唔　俾　再阻我踩　　住雞髀　・・・
qwen        　・俾我啊唔俾唔俾唔　俾　追到我睇一　隻雞鼻　・・・
sensevoice  　・俾　啊唔俾唔俾唔　俾　追到我睇　　食雞髀　・・・
firered     　・俾我啊唔俾唔俾唔　俾　追到我請你　食雞髀　・・・
glm         　・餅喎啊唔餅唔餅唔　餅　追到我睇　　只雞餅　・・・
            －－－－－－－－－－－－－－－－－－－－－－－－－－
merged      　・俾我呀唔俾唔俾唔　俾｜追到我請你　食雞髀｜・・・
reference   　・　　姐姐給我看看｜不　給不給不給｜　　　　・・・
```

### Block 17

```text
whisper     啊　我都揾　　　　　　　　　　　　　　到　隻雞腿　・・・
mimo        ＨｕｈＡｒｅｔｈｅｗｉｎｄｏｗｓｏｐｅｎｂａｂｅ　・・・
qwen        吓吓我都影　　　　　　　　　　　　　　到　只雞髀　・・・
sensevoice  　　我都穩　　　　　　　　　　　　　　到　只雞髀　・・・
firered     嗯哼耳朵聞　　　　　　　　　　　　　　到就給一百　・・・
glm         　　我都揾　　　　　　　　　　　　　　到　只雞尾　・・・
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      啊　我都揾　　　　　　　　　　　　　　到　隻雞髀｜・・・
reference   　　　　　　　　　　　　　　　　我也找到　只雞腿｜・・・
```

### Block 18

```text
whisper     咩雞腿啊喺呢度邊度會有雞腿㗎　・・你　睇下　・・我喺呢度執到粒粽子啊　爸爸　我　　都有一粒　啊　
mimo        咩雞髀啊喺呢度邊度會有雞髀噶　・・你　睇下　・・我喺呢度執到粒種子啊　爸Ｂ　我　　都有一粒　啊　
qwen        咩雞髀啊喺呢度邊度會有雞髀噶　・・你　睇下　・・我喺呢度執到粒種子啊　爸邊　我　　都有一粒啦爸　
sensevoice  咩雞髀啊喺呢度邊度會有雞髀噶　・・你　睇下　・・我喺呢度執到粒種子啊　爸ｂ　我　　都有一粒　啊　
firered     咩雞髀啊喺呢度邊度會有雞髀噶　・・你　睇下　・・我喺呢度執到粒種子啊　爸ｂ　我　　都有一粒　啊　
glm         咩雞比啊喺呢度邊度會有雞比㗎　・・你　睇下　・・我喺呢度執到粒種子啊　爸爸　我　　都有一粒　啊　
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      咩雞髀啊喺呢度邊度會有雞髀㗎｜・・你　睇下｜・・我喺呢度執到粒種子啊｜爸爸　我　　都有一粒　啊｜
reference   　雞　腿在這　裏怎會有雞　　　・・腿｜這些｜・・我　　　撿到粒種子　　爸爸｜我也撿到　一粒　呀｜

whisper     　　・・・
mimo        嗯　・・・
qwen        嗯　・・・
sensevoice  嗯　・・・
firered     　　・・・
glm         嗯　・・・
            －－－－－
merged      嗯｜・・・
reference   　　・・・
```

### Block 19

```text
whisper     種子呀　・・喺屋入面點會有種子　呢　有喎點解呀　・話唔　定呢係松鼠搬入嚟㗎　・吓咩　松鼠識　搬屋㗎咩　・・・先生呀啲嘢究竟搬去邊㗎　・・・對唔住呀請搬入嚟呀　真係唔好意思呀　・快啲去打開後門透下氣　啦　哦　・・・乖乖啲快啲去　・・嗱佢哋幾精哎　喲　・・・
mimo        種子啊　・・喺屋入邊點會有種子　呢　系啊點解啊　・話唔　定呢系松鼠搬入嚟噶　・吓乜　松鼠識　搬屋嘅咩　・・・先生啊啲嘢究竟搬去邊噶　・・・對唔住啊請搬入嚟啊　真系唔好意思啊　・快啲去打開後門唞下氣　啦　啊　・・・乖乖哋快啲去　・・　　　　　　　　　・・・
qwen        種子啊　・・喺屋入邊點會有種子　咧　系啊點解啊　・話唔　定咧系從書搬入嚟噶　・吓咪　從書即　搬屋噶咩　・・・先生啊啲嘢究竟搬去邊噶　・・・對唔住啊請搬入嚟啊　真系唔好意思啊　・快啲去打開後碗唞下氣　啦　啊　・・・乖乖哋快啲去　・・啊佢哋幾精啊　　　・・・
sensevoice  種子啊　・・喺屋入邊點會用種子　咧　系　點解啊　・話唔　定咧系松鼠搬入嚟噶　・吓乜　蟲水識　搬屋噶咩　・・・先生啊啲嘢究竟搬去邊噶　・・・對唔住啊請搬入嚟啊　真系唔好意思啊　・快啲去打開後門透下氣　啦　啊　・・・乖乖哋快啲去　・・　佢哋幾　　　　　・・・
firered     種子啊　・・喺屋入邊點會有種子　咧　系　點解啊　・話唔　定咧系松鼠搬入嚟噶　・吓乜　松鼠識　搬屋嘅咩　・・・先生啊啲嘢究竟搬去邊噶　・・・對唔住啊請搬入嚟啊　真系唔好意思啊　・快啲去打開後門唞下氣　啦　啊　・・・乖乖哋快啲去　・・　　　　　　　　　・・・
glm         種子啊　・・喺屋入邊點會有種子　咧　系喎點解噶　・話唔　定咧系從水搬入嚟噶　・嚇乜　從水啲　搬屋噶咩　・・・先生啊啲嘢究竟搬去邊噶　・・・對唔住啊請搬入嚟啊　真系唔好意思啊　・快啲去打開後門透下氣　啦　啊　・・・乖乖哋快啲去　・・　我哋幾接嘅　　　・・・
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      種子呀｜・・喺屋入邊點會有種子　呢｜係喎點解呀｜・話唔　定呢係松鼠搬入嚟㗎｜・吓乜　松鼠識　搬屋嘅咩｜・・・先生呀啲嘢究竟搬去邊㗎｜・・・對唔住呀請搬入嚟呀｜真係唔好意思呀｜・快啲去打開後門唞下氣　啦｜啊｜・・・乖乖哋快啲去｜・・啊佢哋幾精啊｜　　・・・
reference   種子　　・・在屋　裏怎會有種子｜　　是　為何會　・這樣｜可能是松鼠搬　　進　・來的｜松鼠懂得搬屋　嗎｜・・・先生　這些東西搬到那裏｜・・・對不　起請搬　　　　　　進來得罪了｜・快點去打開後門透透氣｜　　　　・・・乖乖的快點去｜・・　來呀來呀來　呀｜・・・
```

### Block 20

Source errors: glm: Source produced no nonblank text.

```text
whisper     追
mimo        加
qwen        等
sensevoice  等
firered     等
            －
merged      　
reference   追

whisper     我呀　　
mimo        油啊　　
qwen        我啊　　
sensevoice  我啊　啊
firered     我啊　　
            －－－－
merged      我呀｜　
reference   我呀　追
```

### Block 21

Source errors: glm: Source produced no nonblank text.

```text
whisper     看看看看　　　　・・・
mimo        Ｉｇｏｔｓｉｎ　・・・
qwen        睇下　　　　新　・・・
sensevoice  睇下　　　　先　・・・
firered     睇下　　　　先　・・・
            －－－－－－－－－－－
merged      睇下　　　　先｜・・・
reference   　　　　　　開｜・・・
```

### Block 22

Source errors: mimo: Source produced no nonblank text.; qwen: Source produced no nonblank text.; sensevoice: Source produced no nonblank text.; glm: Source produced no nonblank text.

```text
whisper    嗯嗯嗯　　　　　
firered    ｕｎｋ　ｓｐｋｕ
           －－－－－－－－
merged     嗯嗯嗯｜　　　　
reference  　　　　　　　　

whisper    　　　・・・
firered    ｎｋ　・・・
           －－－－－－
merged     　嗯｜・・・
reference  　　　・・・
```

### Block 24

```text
whisper     搞掂啦　・嗯　
mimo        搞掂啦　・嗯　
qwen        搞掂啦　・嗯　
sensevoice  搞掂啦　・嗯　
firered     搞掂啦　・　　
glm         搞掂啦　・　　
            －－－－－－－
merged      搞掂啦｜・嗯｜
reference   唔沒問　・題｜

whisper     爸爸話呢見我啲污糟嘢一味要靠客　㗎　・・・冇嘅・・去晒　邊啫　　・・・
mimo        爸Ｂ話咧見到啲污糟嘢一定要敲黑　噶　・・・冇嘅・・去晒　邊咧　　・・・
qwen        爸ｂ話咧見到啲污糟有一味要靠黑　嘅　・・・冇嘅・・去晒　邊啊　誒・・・
sensevoice  爸ｂ話呢見到啲污糟人一味要靠吓　噶　・・・冇嘅・・去晒　邊啦　　・・・
firered     爸爸話呢見到啲污糟又一味要靠客　噶　・・・冇嘅・・去晒　邊呢　　・・・
glm         爸爸話咧見到啲污糟有一味要考客　嘅　・・・冇嘅・・去曬　邊咧　　・・・
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      爸爸話呢見到啲污糟嘢一味要靠嚇　㗎｜・・・冇嘅・・去晒　邊啫｜　・・・
reference   爸爸　說見到　　　鬼怪就要靠嚇｜　　・・・　不・・見了｜　　　　・・・
```

### Block 25

```text
whisper     冇呀去咗　　　邊　
mimo        冇喎去咗　　　邊　
qwen        冇啊去咗　　　邊　
sensevoice  冇啊去咗　　　邊　
firered     冇啊去咗　　　邊　
glm         冇啊去咗　　　邊　
            －－－－－－－－－
merged      冇啊去咗　　　邊｜
reference   　不見了｜去看看｜

whisper     睇下有冇啲未嚇走嘅　　　　　　先　
mimo        睇下有冇啲未吓走嘅　　　　　　先　
qwen        睇下有冇啲未吓走嘅　　　　　　先　
sensevoice  睇下有冇啲未吓酒嘅　　　　　　先　
firered     睇下有冇啲未吓走嘅　　　　　　先　
glm         睇下有冇啲未客走嘅　　　　　　先　
            －－－－－－－－－－－－－－－－－
merged      睇下有冇啲未嚇走嘅　　　　　　先｜
reference   　　　　　　是嘛看看還有沒有未走　

whisper     真　係冇喎嗯　　　
mimo        真　系冇喎嗯　阿　
qwen        真　系冇啊嗯　　　
sensevoice  真　系冇　　　　　
firered     真　系冇　　　　　
glm         真　系冇喎　　　　
            －－－－－－－－－
merged      真　係冇喎嗯｜　　
reference   的｜　　　沒　有｜

whisper     　嗰度係沖涼房嚟㗎　頭先我哋見　到啲髒　嘢　　・噢咩喎　・　嗰啲髒　嘢　　畀我哋兩個客人嚟沖涼房　呢一度　不過而家唔見晒　一啲都搵唔到喎　・等我去睇下　・・・
mimo        爹嗰度系沖涼房嚟噶　頭先我哋見　到啲污糟嘢　啊・哦咩污　・糟嗰啲污糟嘢　　俾我哋兩個吓咗嚟沖涼房　呢一度　不過而家唔見晒　一啲都揾唔到啊　・等我去睇下　・・・
qwen        　嗰度系粗糧房嚟噶　頭先我哋見　到啲污糟嘢　啊・哦咩話　・　嗰啲污糟嘢啊　俾我哋兩個校長嚟粗糧房　呢一度　不過而家唔見晒　一啲都揾唔到啊　・等我去睇下　・・・
sensevoice  　嗰度系沖涼房嚟噶　頭先我哋見　到啲污糟嘢　啊・　　　　・　嗰啲污糟嘢　　俾我哋兩個客　嚟沖涼房　呢　　　不過而家唔見晒　一啲都　唔到啊　・等我去睇下　・・・
firered     　　度系沖涼房嚟噶　頭先我哋見　到啲污糟嘢　啊・好咩　　・　　啲污糟嘢啊　俾我哋兩個吓咗嚟沖涼房　呢　度　不過而家唔見晒　一啲都穩唔到啊　・等我去睇下　・・・
glm         　嗰度系沖涼房嚟㗎　頭先我哋見　到啲污糟嘢　啊・哦咩喎　・　嗰啲污糟嘢啊　俾我哋兩個客咗嚟沖涼房　呢　度　不過而家唔見曬　一啲都揾唔到喎　・等我去睇下　・・・
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      　嗰度係沖涼房嚟㗎｜頭先我哋見　到啲污糟嘢｜　・哦咩喎｜・　嗰啲污糟嘢啊　畀我哋兩個嚇咗嚟沖涼房｜呢一度　不過而家唔見晒｜一啲都搵唔到喎｜・等我去睇吓｜・・・
reference   　　　　　　　那邊　是浴　　室｜剛才我們見　到・些鬼怪｜・什　　　　　麼｜那些　　　鬼怪給我們兩　個嚇倒｜　　　進了浴室　那邊現在不見了｜・　　　　　　・・・
```

### Block 26

```text
whisper     　
mimo        　
qwen        　
sensevoice  　
firered     嗯
glm         　
            －
merged      　
reference   　

whisper     見唔見呀　
mimo        見唔見啊　
qwen        見唔見啊　
sensevoice  見唔見啊　
firered     見唔見啊　
glm         見唔見啊　
            －－－－－
merged      見唔見呀｜
reference   　　見到　

whisper     冇　呀嗰啲係梅屎嚟啫嘛　・係梅屎　呀咪唔係污糟嘢嚟咩　・・你　哋頭先喺外面凍光入屋咪眼花花囉　・・・
mimo        冇　啊嗰啲系黴屎嚟啫嘛　・系黴屎　啊乜唔系污糟嘢嚟咩　・・你　哋頭先喺外邊咁光入屋咪眼花花咯　・・・
qwen        冇　啊嗰啲系煤屎嚟啫嘛　・系煤屎　啊咪唔系污糟嘢嚟咩　・・你　哋頭先喺外邊咁光入屋咪眼花花咯　・・・
sensevoice  冇　啊嗰啲系梅市嚟啫嘛　・系梅市　啊乜唔系污糟嘢嚟咩　・・你　哋頭先喺外面咁光入屋咪眼花花咯　・・・
firered     冇　啊　啲系梅屎嚟啫嘛　・系梅屎　啊乜唔系污糟嘢嚟咩　・・你　哋頭先喺外面咁光入屋咪眼花花咯　・・・
glm         冇　啊嗰啲系門屎嚟啫嘛　・系門屎　啊咩唔系污糟嘢嚟咩　・・你　哋頭先喺外面陽光入屋咪眼花花咯　・・・
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      冇　呀嗰啲係煤屎嚟啫嘛｜・係煤屎　呀乜唔係污糟嘢嚟咩｜・・你　哋頭先喺外面咁光入屋咪眼花花囉｜・・・
reference   嗎｜　　　　沒有那些只　・是煤屎｜　　　是煤屎不是鬼　・・怪｜你們剛在外面　　　　那麼光進屋｜・・・
```

### Block 27

```text
whisper     話你哋知道啦當陽光曬入屋之後呢　乜嘢污糟辣太嘢　都會走晒㗎喇　唔使驚　　　㗎　・・・見光就走㗎喇　・・・梅　塔斯鬼走呀呀呀　唔見晒機會走呀呀　呀　・呀　　　　　　　　　　　　　　　　　呀
mimo        話你哋知道啦當用過洗液屋之後咧　乜嘢污糟邋遢嘢　都會走晒噶啦　唔使驚　　　噶　・・・見鬼就走噶啦　・・・維　他斯鬼走啦呀呀　唔見晒啲污糟嘢啦　咿　・呀　　　　　　　　　　　　　　　　　喂
qwen        話你哋知道啦當陽光晒入屋之後咧　乜嘢污糟邋遢嘢　都會走晒噶啦　唔使驚　　　嘅　・・・見光就走噶啦　・・・咪　嘆死鬼咒啦呀呀　唔見晒啲污糟邋遢　　　・呀　哈哈哈哈哈　哈哈哈哈哈哈哈哈哈哈各
sensevoice  話你哋知道啦當陽光晒入屋之後呢　乜嘢污糟邋遢嘢　都會走晒噶啦　唔使驚　　　噶　・・・見光就走噶啦　・・・煤　　炭鬼糟　　　　　　　　　　　　　　　・　　　　　　　　　　　　　　　　　　　
firered     話你哋知道啦當陽光晒入屋之後咧　乜嘢污糟邋遢嘢　都會走晒噶啦　唔使驚　　　噶　・・・見光就走噶啦　・・・煤　　炭鬼走啦　　　唔見晒啲污糟嘢啦　　　・　　　　　　　　　　　　　　　　　　喂
glm         話你哋知道啦當陽光曬入屋之後咧　乜嘢污糟亂塌嘢　都會走曬㗎啦　唔使驚　　　㗎　・・・見光就走㗎啦　・・・埋　貪死鬼走啦呀呀　唔見曬嘅污糟嘢啦　啦　・咦　　　　　　　　　　　　　　　　　　
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      話你哋知道啦當陽光曬入屋之後呢｜乜嘢污糟邋遢嘢　都會走晒㗎啦｜唔使驚　　　㗎｜・・・見光就走㗎啦｜・・・煤　　煤蟲走啦呀呀｜唔見晒啲污糟嘢啦｜呀｜・　　　　　　　　　　　　　　　　　　　
reference   　　　　　　告訴你們　　　當陽　光　　　曬進屋｜　　　　什麼　鬼怪都會跑光的｜・・・見光就　　跑　・・・的｜　　煤炭屎鬼跑　了鬼　　　怪全不　見　・了｜　　真好哈｜　　　　　　　　　　　

whisper     喂喂餵你哋唔好玩喇　乖乖啲快啲去做嘢　你哋識唔識得點樣上二樓呀　吓　揾條樓梯上去二樓度　將所有　窗打開　晒佢　　
mimo        喂喂喂你哋唔好玩啦　乖乖哋快啲去做嘢　你哋識唔識得點樣上二樓啊　吓　揾條樓梯上去二樓度　將所有　窗打開　晒　　　
qwen        位各位你哋唔好玩啊　乖乖哋快啲去做嘢　你哋識唔識得點樣上二樓啊　吓　揾條樓梯上去二樓度　將所有　窗打開　晒　　　
sensevoice  　　　　　　　　　　乖乖哋快　去做嘢　　　　　　　點　上二樓　　　　　　樓梯　去二樓　　　　　　　打　　　佢　打
firered     喂喂喂你哋唔好玩啦　乖乖哋快啲去做嘢　你哋識唔識得點樣上二樓啊　吓　穩條樓梯上去二樓度　將所有　窗打開　晒　　　
glm         喂喂餵你哋唔好玩啦　乖乖哋快啲去做嘢　你哋識唔識得點樣上二樓啊　嚇　揾條樓梯上去二樓度　將所有　窗打開　曬佢　　
            －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
merged      喂喂餵你哋唔好玩啦｜乖乖哋快啲去做嘢｜你哋識唔識得點樣上二樓呀　吓｜揾條樓梯上去二樓度｜將所有　窗打開　晒佢｜　
reference   　　　你們不要玩　　　　了快點去做事｜你　　們懂得　　上二樓嗎｜　　　　　快上　二樓　　將所有的窗打開｜　　　　

whisper     　　點打呀　・・・
mimo        佢　知道　　・・・
qwen        佢　知道啦　・・・
sensevoice  佢　知打　　・・・
firered     佢　知道啦　・・・
glm         佢　知道啦　・・・
            －－－－－－－－－
merged      佢｜知道啦｜・・・
reference   　　　　　　・・・
```

### Block 28

```text
whisper     冇喎　
mimo        冇啊　
qwen        冇啊　
sensevoice  冇啊　
firered     冇啊　
glm         冇啊　
            －－－
merged      冇啊｜
reference   沒有｜

whisper     冇喎搵頭先　
mimo        冇啊媽打開　
qwen        冇啊把門開　
sensevoice  冇啊梯　　　
firered     冇啊把打開　
glm         冇啊　　冇　
            －－－－－－
merged      冇啊門打開｜
reference   　　　沒有｜

whisper     唔　　　　　係喎　　　　
mimo        唔　　　　　系啊　　　　
qwen        唔　　　　　系啊　　　　
sensevoice  唔　　　　　系　　　　　
firered     唔　　　　　系啊　　　　
glm         啊　　　　　冇啊　冇啊　
            －－－－－－－－－－－－
merged      唔　　　　　係　　　啊｜
reference   樓梯呀｜在哪　兒｜　　　

whisper     　係　咪呢度呢　係咪　呢度　呢　冇喎有冇喎　・・・
mimo        　系　咪呢度咧　系咪　呢度　咧　冇啊系冇啊　・・・
qwen        　喺唔喺呢度咧　喺唔喺呢度　咧　冇啊有冇啊　・・・
sensevoice  　喺　咪呢度啦　　咪　呢度　都　冇　有冇啊　・・・
firered     　喺　埋呢度啦　喺埋　呢度　啦　冇啊阿媽喂　・・・
glm         喎系　咪你走啦　系咪　你走　啦　冇喎　冇喎　・・・
            －－－－－－－－－－－－－－－－－－－－－－－－－
merged      　係　咪呢度呢｜係咪　呢度　呢｜冇喎有冇喎｜・・・
reference   　　　　　　　　　　在哪兒｜　　　　沒有的｜・・・
```

### Block 29

```text
whisper     我搵得啦切子　・・・
mimo        我揾到啦晴晴　・・・
qwen        我揾得啦姐姐　・・・
sensevoice  我咪咗啦廁紙　・・・
firered     我穩到啦姐姐　・・・
glm         我問到了次子　・・・
            －－－－－－－－－－
merged      我搵到啦姐姐｜・・・
reference   　　　　　　　・・・
```

### Block 30

```text
whisper     咁黑㗎　　　・・會唔會又有　・・未　嘗　試　
mimo        咁好嘅　　　・・會唔會入藥　・・你睇下　先　
qwen        咁ｈｏ　ｔ噶・・會唔會又有　・・唔　貪　食　
sensevoice  咁黑　　　噶・・會唔會又有　・・你　攤　屎　
firered     敢不　　　好・・改我我有有　・・你　看　誰　
glm         咁刻　　　噶・・會唔會又有　・・冇　貪　死　
            －－－－－－－－－－－－－－－－－－－－－－
merged      咁黑㗎｜　　・・會唔會又有　・・煤屎㗎｜　　
reference   　　這　麼黑・・會不會又有｜・・煤　炭　屎｜

whisper     呀啲聲呀　・・・
mimo        啊會聲啊　・・・
qwen        啊咩聲啊　・・・
sensevoice  啊出聲啊　・・・
firered     　　　　　・・・
glm         啊你聽啊　・・・
            －－－－－－－－
merged      啊咩聲呀｜・・・
reference   　　　　　・・・
```

### Block 31

```text
whisper     還該揹我　・・啊　・・・
mimo        還敢擺我　・・呃　・・・
qwen        係該俾我　・・　　・・・
sensevoice  系街髀　　・・　　・・・
firered     還該陪我　・・　　・・・
glm         還敢揹我　・・　　・・・
            －－－－－－－－－－－－
merged      仲敢揹我｜・・　　・・・
reference   　　　雞　・・腿｜・・・
```

### Block 32

```text
whisper     梅太死鬼走啦呀呀　・・・　　
mimo        妹太　快走啦呀呀　・・・　　
qwen        煤炭市鬼走啦呀呀　・・・　　
sensevoice  冇睇使鬼咗啦呀呀　・・・　　
firered     煤炭死鬼走啦呀呀　・・・　　
glm         喂睇先快走啦呀呀　・・・　　
            －－－－－－－－－－－－－－
merged      煤炭死鬼走啦呀呀｜・・・　　
reference   煤　　　炭屎鬼跑　・・・了｜
```

### Block 33

Source errors: whisper: Segment 0 compression ratio 9.58 exceeds maximum 2.40.

```text
mimo        用絕招　啊　
qwen        用絕招　啊　
sensevoice  用絕招　啊　
firered     用絕招　啊　
glm         用住招　啊　
            －－－－－－
merged      用絕招　啊｜
reference   用絕招｜　　

mimo        嗯　・・・
qwen        　　・・・
sensevoice  　　・・・
firered     　　・・・
glm         嗯　・・・
            －－－－－
merged      嗯｜・・・
reference   　　・・・
```

### Block 34

```text
whisper     咁夠膽玩我哋兩個　等我　哋炮　製你先　
mimo        敢夠膽玩我哋兩個　等我　哋炮　製你先　
qwen        咁夠膽玩我哋兩個　等我　哋炮　製你先　
sensevoice  咁夠膽玩我哋兩個　等我　哋炮　製你先　
firered     咁夠膽玩我哋兩個　等我　哋炮　製你先　
glm         咁夠膽玩我哋兩個　等我　哋炮　製你先　
            －－－－－－－－－－－－－－－－－－－
merged      咁夠膽玩我哋兩個｜等我　哋炮　製你先｜
reference   　　　這麼大膽戲　弄我們兩個｜讓我應　
```
