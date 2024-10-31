#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Service for interacting with OpenAI API."""
from __future__ import annotations

from openai import OpenAI
from pydantic import ValidationError

from scinoephile.core.openai.subtitle_series_response import SubtitleSeriesResponse
from scinoephile.core.subtitle_series import SubtitleSeries
from scinoephile.core.subtitles import get_pair_strings_with_proportional_timings


class OpenAiService:
    synchronize_bilingual_subtitle_block_prompt = """
Instructions:
  * Your task is to take Chinese and English subtitles for the same video clip and
    produce JSON output that will be used to produce a synchronized bilingual subtitle
    file.
  * Each request will start with CHINESE: followed by the Chinese subtitles, and then
    ENGLISH: followed by the English subtitles.
  * The format of subtitles is similar to SRT, but times have been adjusted to a
    relative scale from 0 to 100, where 0 is the start of the clip and 100 is the end.
  * Your response should be a JSON object following this exact specification:

{
    "explanation": <text explaining the mapping between Chinese and English>,
    "synchronization": [
        {
            "chinese": [<list of Chinese subtitle indexes>],
            "english": [<list of English subtitle indexes>],
        },
        ...
    ],
}

  * "explanation" contains text describing the rationale for the mapping between Chinese
     and English subtitles.
  * "synchronization" defines a list of synchronization groups. Each synchronization
    group includes the indexes of the Chinese and English subtitles that encompass the
    same meaning and timing.
  * Within each synchronization group:
    * The "chinese" field lists the indices of the Chinese subtitles in the group.
    * The "english" field lists the indices of the English subtitles in the group.

Synchronization must follow these rules:
  * All Chinese subtitles are in exactly one synchronization group.
  * All English subtitles are in exactly one synchronization group, or none at all.
  * All Chinese subtitles are in their original order.
  * All English subtitles are in their original order.
  * English subtitles are in only one subtitle group.
  * Chinese subtitles are in only one subtitle group.
  * All Synchronization group contain either:
    * One Chinese subtitle and one English subtitle.
    * One Chinese subtitle and multiple English subtitles.
    * Multiple Chinese subtitles and one English subtitle.
  * Synchronization groups do not contain both multiple Chinese and multiple English
    subtitles.

Synchronization should follow these guidelines:
  * Use a combination of the timing and meaning of the subtitles to determine the
    synchronization.
  * If multiple Chinese subtitles combine to form one thought that corresponds to a
    single English subtitle, they should be grouped together in one synchronization
    group.
  * The Chinese and English subtitles' meaning should be similar, but may have
    significant differences, particular if the subtitles are idiomatic.
  * The Chinese and English subtitles' timing should be similar, but may not line up
    exactly.
  * If a Chinese subtitle only overlaps with one English subtitle, and that English
    subtitle aligns only with that Chinese subtitle, they are likely a simple pair.
  * Most of the time, the Chinese and English subtitles will align 1:1. In these
    cases, "chinese" and "english" for the synchronization group will contain only a
    single index each.
  * If an English subtitle does not overlap with any Chinese subtitles, it may be
    dropped.
  * If a Chinese subtitle has no corresponding English subtitle, it should be included
    on its own in a synchronization group.

Explanation must follow these rules:
  * Explain the subtitle groups in the order they appear in the input.
  * Do not include any generic text like "The subtitles are aligned based on their
    meaning and timing." Focus on the specific subtitles you have been asked about.
  * Include one bullet point for each subtitle group, starting with "Group 1:".
  * Explain every subtitle group with at least one sentence.
  * For each subtitle group, explain which Chinese and English subtitles were included
    and why, explicitly referencing their timing and meaning.
  * When referring to any subtitle, explicitly identify it by language and index, for
    example "Chinese 1" or "English 2".

See the following examples.

CHINESE:
1
0 --> 27
爸爸，牛奶糖

2
29 --> 45
谢谢

3
55 --> 70
妳们两个累不累啊？

4
82 --> 98
就快到了

ENGLISH:
1
0 --> 26
Dad, do you want a caramel?

2
29 --> 69
Thanks. Aren't you tired?

3
72 --> 80
All right.

4
84 --> 100
We're almost there.

Expected synchronization:
[SubtitleGroupResponse(chinese=[1], english=[1]),
 SubtitleGroupResponse(chinese=[2, 3], english=[2]),
 SubtitleGroupResponse(chinese=[4], english=[4])]

CHINESE:
1
1 --> 10
不见了

2
25 --> 33
这间是浴室

3
34 --> 47
爸爸，有怪东西耶

4
48 --> 54
松鼠吗？

5
54 --> 61
不知道

6
63 --> 77
不像蟑螂也不像老鼠

7
78 --> 88
只知道是一堆黑黑的东西

ENGLISH:
1
0 --> 10
There's nothing here.

2
24 --> 32
That's the bathroom.

3
34 --> 46
Dad, there's something in here.

4
47 --> 52
A squirrel?

5
54 --> 86
Dunno. A bunch of black things but not roaches or mice.

6
88 --> 100
Really?

Expected synchronization:
[SubtitleGroupResponse(chinese=[1], english=[1]),
 SubtitleGroupResponse(chinese=[2], english=[2]),
 SubtitleGroupResponse(chinese=[3], english=[3]),
 SubtitleGroupResponse(chinese=[4], english=[4]),
 SubtitleGroupResponse(chinese=[5, 6, 7], english=[5])]

CHINESE:
1
1 --> 11
有没有？
2
23 --> 40
那一定是「灰尘精灵」
3
43 --> 55
灰尘精灵
4
57 --> 66
画册里有吗？
5
67 --> 74
有啊
6
75 --> 100
今天天气那么好　鬼不可能出来的

ENGLISH:
1
0 --> 10
Can you see 'em?
2
23 --> 39
I think they were... soot gremlins.
3
41 --> 67
'Gremlins'? Like in my picture book?
4
69 --> 98
That's right. Ghosts don't come out on days like this.

Expected synchronization:
[SubtitleGroupResponse(chinese=[1], english=[1]),
 SubtitleGroupResponse(chinese=[2], english=[2]),
 SubtitleGroupResponse(chinese=[3, 4], english=[3]),
 SubtitleGroupResponse(chinese=[5, 6], english=[4])]
 
CHINESE:
1
1 --> 11
好了，做事啦

2
12 --> 40
上二楼的楼梯　到底在哪里呢？

3
50 --> 61
妳们两个去把楼梯找出来

4
62 --> 74
然后把二楼的窗户打开

5
78 --> 86
好

6
88 --> 100
人家也要

ENGLISH:
1
0 --> 36
Let's get to work! See if you can find how to get upstairs.

2
52 --> 73
Get up there and open all the windows.

3
78 --> 86
Sure!

4
88 --> 98
I'm coming, too!

Expected synchronization:
[SubtitleGroupResponse(chinese=[1, 2], english=[1]),
 SubtitleGroupResponse(chinese=[3, 4], english=[2]),
 SubtitleGroupResponse(chinese=[5], english=[3]),
 SubtitleGroupResponse(chinese=[6], english=[4])]

CHINESE:
1
2 --> 7
厕所

2
25 --> 32
咦？

3
50 --> 65
咦？

4
83 --> 90
咦？

5
91 --> 100
咦？

ENGLISH:
1
0 --> 9
Toilet!

2
25 --> 32
Not here!

Expected synchronization:
[SubtitleGroupResponse(chinese=[1], english=[1]),
 SubtitleGroupResponse(chinese=[2], english=[2]),
 SubtitleGroupResponse(chinese=[3], english=[]),
 SubtitleGroupResponse(chinese=[4], english=[]),
 SubtitleGroupResponse(chinese=[5], english=[])]
  
CHINESE:
1
0 --> 55
灰尘精灵

2
59 --> 100
你在不在？

ENGLISH:
1
0 --> 96
Are you there, Mr. Soot Gremlin?

Expected synchronization:
[SubtitleGroupResponse(chinese=[1, 2], english=[1])]

CHINESE:
1
0 --> 9
小梅，它们很快就会不见了

2
9 --> 14
不好玩

3
14 --> 26
可是要是来这么一大堆　该怎么办？

4
28 --> 35
人家才不怕那些呢

5
36 --> 40
是吗？

6
40 --> 54
那以后晚上　姊姊就不陪妳去尿尿啰

7
65 --> 77
来来…快来打扫吧

8
77 --> 89
妳们去河边打点水回来吧

9
89 --> 94
河边啊

10
95 --> 100
人家也要去

ENGLISH:
1
0 --> 8
Mei, they're going away.

2
9 --> 13
That's no fun.

3
14 --> 26
What happens if a huge one comes out, like this?

4
29 --> 33
I wouldn't be scared.

5
36 --> 53
Okay then, I won't walk you to the bathroom at night.

6
64 --> 88
Okay, cleaning time. Could you get some water from the stream?

7
89 --> 94
From the stream?

8
95 --> 100
I'm coming, too!

Expected synchronization:
[SubtitleGroupResponse(chinese=[1], english=[1]),
 SubtitleGroupResponse(chinese=[2], english=[2]),
 SubtitleGroupResponse(chinese=[3], english=[3]),
 SubtitleGroupResponse(chinese=[4], english=[4]),
 SubtitleGroupResponse(chinese=[5, 6], english=[5]),
 SubtitleGroupResponse(chinese=[7, 8], english=[6]),
 SubtitleGroupResponse(chinese=[9], english=[7]),
 SubtitleGroupResponse(chinese=[10], english=[8])]
 
CHINESE:
1
1 --> 20
爸爸以前也这样作弄过女生

2
25 --> 36
男生最讨人厌了

3
37 --> 65
不过　婆婆这个糯米团好好吃耶

4
69 --> 85
那就多吃点啊

5
90 --> 96
辛苦了

ENGLISH:
1
0 --> 20
I did the same when I was his age.

2
25 --> 64
I hate boys. But I really love Nanny's rice cakes!

3
68 --> 83
Eat as much as you want.

4
90 --> 100
Thank you!

Expected synchronization:
[SubtitleGroupResponse(chinese=[1], english=[1]),
 SubtitleGroupResponse(chinese=[2, 3], english=[2]),
 SubtitleGroupResponse(chinese=[4], english=[3]),
 SubtitleGroupResponse(chinese=[5], english=[4])]

CHINESE:
1
1 --> 13
婆婆

2
16 --> 26
您好！！

3
27 --> 35
您可真忙啊

4
37 --> 50
三个一起出门啊？

5
51 --> 65
我们要去医院看妈妈

6
67 --> 79
可有好一段路呢

7
82 --> 92
替我帮妳们妈妈问好

8
93 --> 100
好的

ENGLISH:
1
0 --> 13
Nanny!

2
15 --> 25
Hello!

3
26 --> 34
Hard at work?

4
36 --> 47
Where're you all heading?

5
51 --> 64
To visit Mommy in the hospital!

6
66 --> 89
That's nice. Give her my regards!

Expected synchronization:
[SubtitleGroupResponse(chinese=[1], english=[1]),
 SubtitleGroupResponse(chinese=[2], english=[2]),
 SubtitleGroupResponse(chinese=[3], english=[3]),
 SubtitleGroupResponse(chinese=[4], english=[4]),
 SubtitleGroupResponse(chinese=[5], english=[5]),
 SubtitleGroupResponse(chinese=[6, 7], english=[6]),
 SubtitleGroupResponse(chinese=[8], english=[])]

CHINESE:
1
6 --> 48
爸爸

2
62 --> 100
天亮啰

ENGLISH:
1
0 --> 96
Dad, time to get up!

Expected synchronization:
[SubtitleGroupResponse(chinese=[1, 2], english=[1])]
 
CHINESE:
1
0 --> 9
妈妈好像好了很多耶

2
9 --> 14
是啊

3
14 --> 26
医生也说　再过不久就可以出院了

4
29 --> 36
再过不久，明天吗？

5
38 --> 46
妳什么都是明天

6
47 --> 54
明天可能有点难耶

7
58 --> 71
妈妈说想跟小梅一起睡

8
72 --> 90
咦？妳不是说妳已经长大　要自己一个人睡的吗？

9
91 --> 100
跟妈妈睡没关系

ENGLISH:
1
0 --> 8
Mom looked really well.

2
9 --> 26
You're right.The doctor says she'll be home soon.

3
28 --> 36
Soon? Like tomorrow?

4
37 --> 45
You always say this.

5
46 --> 53
Tomorrow is a little too soon.

6
58 --> 70
Mom said she'll sleep with me in my bed.

7
71 --> 89
Weren't you saying you're big enough to sleep alone?

8
90 --> 99
Mom is special!

Expected synchronization:
[SubtitleGroupResponse(chinese=[1], english=[1]),
 SubtitleGroupResponse(chinese=[2, 3], english=[2]),
 SubtitleGroupResponse(chinese=[4], english=[3]),
 SubtitleGroupResponse(chinese=[5], english=[4]),
 SubtitleGroupResponse(chinese=[6], english=[5]),
 SubtitleGroupResponse(chinese=[7], english=[6]),
 SubtitleGroupResponse(chinese=[8], english=[7]),
 SubtitleGroupResponse(chinese=[9], english=[8])]
"""

    def __init__(self):
        self.model = "gpt-4o"
        self.client = OpenAI()

    def get_synchronization(
        self, hanzi: SubtitleSeries, english: SubtitleSeries
    ) -> SubtitleSeriesResponse:
        hanzi_str, english_str = get_pair_strings_with_proportional_timings(
            hanzi, english
        )
        query = f"CHINESE:\n{hanzi_str}\n\nENGLISH:\n{english_str}"

        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            temperature=1.0,
            response_format=SubtitleSeriesResponse,
            messages=[
                {
                    "role": "system",
                    "content": self.synchronize_bilingual_subtitle_block_prompt,
                },
                {
                    "role": "user",
                    "content": query,
                },
            ],
        )

        # Deserialize
        message = completion.choices[0].message
        content = message.content
        try:
            subtitle_series_response = SubtitleSeriesResponse.parse_raw(content)
            return subtitle_series_response
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise e
