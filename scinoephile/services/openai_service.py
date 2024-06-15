#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Service for interacting with OpenAI API."""
from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from scinoephile.core import SubtitleSeries


class OpenAiService:
    synchronize_bilingual_subtitle_block_prompt = """
Instructions:
* Each request will start with CHINESE: followed by a series of Chinese subtitles in SRT format, and then ENGLISH: followed by a series of English subtitles in SRT format.
* You are tasked with synchronizing Chinese and English subtitles. Your response should be a JSON object following this exact specification:
{
    "explanation": [<list of explanations of ONLY subtitles that did not map cleanly 1:1; specific examples of situations that warrant explanation are outlined below>],
    "synchronization":
        [
            {
                "chinese": [<list of Chinese subtitle indexes>],
                "english": [<list of English subtitle indexes>],
                "start": ["chinese", <starting Chinese subtitle index>],
                "end": ["chinese", <ending Chinese subtitle index>]
            },
            ...
        ]
}
*"chinese" and "english" fields should contain lists of indices of the corresponding subtitles that match.
*"start" and "end" fields should specify the range of the Chinese subtitles that correspond to the English subtitles.
*Ensure the "start" and "end" fields are correctly set using the indices from the "chinese" list.
*IMPORTANT: DO NOT include any additional fields or modify this structure in any way. Adhere strictly to the given format.
* Special attention is needed for cases where the two languages do not align perfectly in number or content.
* The subtitle index may not align between the two languages, as one language may have subtitles not present in the other.
* The timing may not align between the two languages, as they may originate from different sources with different timing.
* Use the text of the subtitles as the primary guide for alignment, considering your understanding of both languages. The meaning of the subtitles should roughly align, though there may be variations between the sets of subtitles.
* Exclude any timing offset information from the synchronization elements. Only include subtitle indices in the synchronization output.

Special Cases Handling:
* Multiple Chinese to Single English: Two Chinese subtitles may correspond to a single English subtitle. Include both Chinese and the single English subtitle in one element.
* Single Chinese to Multiple English: One Chinese subtitle may correspond to two English subtitles. Include the Chinese and both English subtitles in one element.
* Chinese without English: If a Chinese subtitle has no corresponding English subtitle, include it as a single element.
* English without Chinese: Exclude English subtitles with no corresponding Chinese subtitle from the synchronization elements.
* Anomalies should be infrequent. Most subtitles will match 1:1, even if the meaning is slightly different.
* Provide explanations for each anomaly separately from the synchronization elements. Do not include the explanations within the synchronization elements.
* Ensure all Chinese subtitles are included in the response, even if they do not have a corresponding English subtitle. Exclude English subtitles without a corresponding Chinese subtitle from the synchronization elements.
* Prioritize exact 1:1 mapping of Chinese and English subtitles where possible. Only combine subtitles when a clear 1:1 mapping is not possible due to differences in meaning or timing.
* Ensure all Chinese subtitles are represented in the synchronization output, even if no corresponding English subtitle exists. English subtitles should only be included if there is a corresponding Chinese subtitle.

Here are some examples to help you understand the task better:

1. Given the following input:

CHINESE:

1
00:02:32,152 --> 00:02:34,029
爸爸，牛奶糖

2
00:02:34,154 --> 00:02:35,197
谢谢

3
00:02:35,906 --> 00:02:36,907
妳们两个累不累啊？

4
00:02:37,741 --> 00:02:38,867
就快到了

5
00:02:50,796 --> 00:02:51,588
小梅，快躲起来

ENGLISH:

1
00:02:32,152 --> 00:02:33,904
Dad, do you want a caramel?

2
00:02:34,112 --> 00:02:36,865
Thanks. Aren't you tired?

3
00:02:37,072 --> 00:02:37,584
All right.

4
00:02:37,912 --> 00:02:38,981
We're almost there.

5
00:02:50,472 --> 00:02:51,382
Mei, hide!

The expected output is:

{
    "explanation":
        [
            "'谢谢' and '妳们两个累不累啊？' correspond to 'Thanks. Aren't you tired?'",
            "No corresponding Chinese for 'All right.'",
        ],
    "synchronization": 
        [
            {
                "chinese": [1],
                "end": ["chinese", 1],
                "english": [1],
                "start": ["chinese", 1],
            },
            {
                "chinese": [2, 3],
                "end": ["chinese", 3],
                "english": [2],
                "start": ["chinese", 2],
            },
            {
                "chinese": [4],
                "end": ["chinese", 4],
                "english": [4],
                "start": ["chinese", 4],
            },
            {
                "chinese": [5],
                "end": ["chinese", 5],
                "english": [5],
                "start": ["chinese", 5],
            },
        ],
}

2. Given the following input:

CHINESE:

34
00:06:12,789 --> 00:06:14,624
那叫做樟树

35
00:06:16,627 --> 00:06:17,503
樟树耶

36
00:06:17,628 --> 00:06:18,629
樟树

37
00:06:31,475 --> 00:06:32,351
橡果子

38
00:06:34,144 --> 00:06:36,229
我看一下

ENGLISH:

34
00:06:12,632 --> 00:06:14,350
It's a camphor tree.

35
00:06:16,472 --> 00:06:18,428
Camphor tree...

36
00:06:27,712 --> 00:06:28,622
Oops!

37
00:06:31,512 --> 00:06:32,308
An acorn!

38
00:06:34,072 --> 00:06:35,744
Show me.

The expected output is:

{
    "explanation":
        [
            "'樟树' has no corresponding English",
            "No corresponding Chinese for 'Oops!'",
        ],
    "synchronization":
        [
            {
                "chinese": [34],
                "end": ["chinese", 34],
                "english": [34],
                "start": ["chinese", 34],
            },
            {
                "chinese": [35],
                "end": ["chinese", 35],
                "english": [35],
                "start": ["chinese", 35],
            },
            {
                "chinese": [36],
                "end": ["chinese", 36],
                "english": [],
                "start": ["chinese", 36],
            },
            {
                "chinese": [37],
                "end": ["chinese", 37],
                "english": [37],
                "start": ["chinese", 37],
            },
            {
                "chinese": [38],
                "end": ["chinese", 38],
                "english": [38],
                "start": ["chinese", 38],
            },
        ],
}

3. Given the following input:

CHINESE:

49
00:07:16,353 --> 00:07:18,355
这要搬到哪儿呢？

50
00:07:18,981 --> 00:07:21,150
放这里，我这就开门

51
00:07:21,358 --> 00:07:23,151
小月，妳去把后门打开

52
00:07:23,277 --> 00:07:24,028
好

53
00:07:24,152 --> 00:07:25,737
去了就看得到

ENGLISH:

49
00:07:16,312 --> 00:07:18,268
Where shall I put this?

50
00:07:18,872 --> 00:07:23,468
Here, I'll get the door for you. Satsuki, open up the kitchen.

51
00:07:24,112 --> 00:07:25,511
It's just round the back.

The expected output is:

{
    "explanation":
        [
            "'放这里，我这就开门' and '小月，妳去把后门打开' correspond to 'Here, I'll get the door for you. Satsuki, open up the kitchen.'",
            "'好' has no corresponding English",
        ],
    "synchronization":
        [
            {
                "chinese": [49],
                "end": ["chinese", 49],
                "english": [49],
                "start": ["chinese", 49],
            },
            {
                "chinese": [50, 51],
                "end": ["chinese", 51],
                "english": [50],
                "start": ["chinese", 50],
            },
            {
                "chinese": [52],
                "end": ["chinese", 52],
                "english": [],
                "start": ["chinese", 52],
            },
            {
                "chinese": [53],
                "end": ["chinese", 53],
                "english": [51],
                "start": ["chinese", 53],
            },
        ],
}

4. Given the following input:

CHINESE:

61
00:08:39,228 --> 00:08:41,021
爸爸，有怪东西耶

62
00:08:41,146 --> 00:08:41,980
松鼠吗？

63
00:08:42,105 --> 00:08:43,106
不知道

64
00:08:43,273 --> 00:08:45,400
不像蟑螂也不像老鼠

65
00:08:45,526 --> 00:08:46,944
只知道是一堆黑黑的东西

66
00:09:00,290 --> 00:09:01,416
有没有？

67
00:09:02,709 --> 00:09:04,502
那一定是「灰尘精灵」

68
00:09:04,920 --> 00:09:06,213
灰尘精灵

69
00:09:06,380 --> 00:09:07,381
画册里有吗？

ENGLISH:

59
00:08:39,152 --> 00:08:40,824
Dad, there's something in here.

60
00:08:41,032 --> 00:08:41,748
A squirrel?

61
00:08:41,992 --> 00:08:46,622
Dunno. A bunch of black things but not roaches or mice.

62
00:08:46,872 --> 00:08:48,624
Really?

63
00:09:00,192 --> 00:09:01,261
Can you see 'em?

64
00:09:02,712 --> 00:09:04,430
I think they were... soot gremlins.

65
00:09:04,712 --> 00:09:07,465
'Gremlins'? Like in my picture book?

The expected output is:

{
    "explanation":
        [
            "'不知道', '不像蟑螂也不像老鼠', and '只知道是一堆黑黑的东西' correspond to 'Dunno. A bunch of black things but not roaches or mice.'",
            "No corresponding Chinese for 'Really?'",
            "'灰尘精灵' and '画册里有吗？' correspond to ''Gremlins'? Like in my picture book?'",
        ],
    "synchronization":
        [
            {
                "chinese": [61],
                "end": ["chinese", 61],
                "english": [59],
                "start": ["chinese", 61],
            },
            {
                "chinese": [62],
                "end": ["chinese", 62],
                "english": [60],
                "start": ["chinese", 62],
            },
            {
                "chinese": [63, 64, 65],
                "end": ["chinese", 65],
                "english": [61],
                "start": ["chinese", 63],
            },
            {
                "chinese": [66],
                "end": ["chinese", 66],
                "english": [63],
                "start": ["chinese", 66],
            },
            {
                "chinese": [67],
                "end": ["chinese", 67],
                "english": [64],
                "start": ["chinese", 67],
            },
            {
                "chinese": [68, 69],
                "end": ["chinese", 69],
                "english": [65],
                "start": ["chinese", 68],
            },
        ]
}
"""

    def __init__(self):
        self.model = "gpt-4o"
        self.client = OpenAI()

    def get_synchronization(
        self, hanzi: SubtitleSeries, english: SubtitleSeries
    ) -> dict[str, Any]:
        query = (
            f"CHINESE:\n\n"
            f"{hanzi.to_string('srt')}\n\n"
            f"ENGLISH:\n\n"
            f"{english.to_string('srt')}"
        )

        completion = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
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

        response = completion.choices[0].message.content
        parsed_response = json.loads(response)

        return parsed_response
