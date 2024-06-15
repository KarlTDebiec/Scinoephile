#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

import json
from pprint import pformat
from typing import Any

from openai import OpenAI

from scinoephile.core import (
    SubtitleSeries,
    get_subtitle_blocks_for_synchronization,
)


class OpenAiService:
    synchronize_bilingual_subtitle_block_prompt = """
Instructions:

* Each request will start with CHINESE: followed by a series of Chinese subtitles in SRT format, and then ENGLISH: followed by a series of English subtitles in SRT format.
* Provide a JSON response describing the synchronization of the Chinese and English subtitles.
* Special attention is needed for cases where the two languages do not align perfectly in number or content.
* The subtitle index may not align between the two languages, as one language may have subtitles not present in the other.
* The timing may not align between the two languages, as they may originate from different sources with different timing.
* Use the text of the subtitles as the primary guide for alignment, considering your understanding of both languages. The meaning of the subtitles should roughly align, though there may be variations between the sets of subtitles.
* You may expect to see a consistent offset. For example, the English subtitles may consistently be 4 seconds ahead of the Chinese subtitles.
* In some cases, two Chinese subtitles may have a single corresponding English subtitle. In this case, the set of two Chinese and one English subtitle form a single element in the JSON response.
* In some cases, one Chinese subtitle may have two corresponding English subtitles. In this case, the set of one Chinese and two English subtitles form a single element in the JSON response.
* In some cases, a Chinese subtitle may have no corresponding English subtitle. In this case, the Chinese subtitle should form a single element in the JSON response.
* In some cases, an English subtitle may have no corresponding Chinese subtitle. In this case, there should be no element in the JSON response. Exclude such instances from the JSON response.
* When judging if a Chinese subtitle has no corresponding English subtitle, consider both the meaning and the timing, after accounting for the apparent offset.
* When judging if an English subtitle has no corresponding Chinese subtitle, consider both the meaning and the timing, after accounting for the apparent offset.
* These types of anomalies should be relatively infrequent. Most subtitles will match 1:1, even if the meaning is a little different.
* Provide explanations for each anomaly separately from the synchronization elements. Do not include the explanations within the synchronization elements.
* Ensure that all Chinese subtitles are included in the response, even if they do not have a corresponding English subtitle. English subtitles without a corresponding Chinese subtitle should be excluded from the synchronization elements.
* Prioritize exact 1:1 mapping of Chinese and English subtitles where possible, only diverging when absolutely necessary.
* Combine multiple subtitles into one element only when a clear 1:1 mapping is not possible and the meanings and timings make it necessary. Avoid combining subtitles if clear 1:1 mappings are possible.
* Ensure all Chinese subtitles are represented in the synchronization output, even if no corresponding English subtitle exists. English subtitles should only be included if there is a corresponding Chinese subtitle.

Here are some examples to help you understand the task better:

1. Given the following input:

CHINESE:

2
00:02:32,152 --> 00:02:34,029
爸爸，牛奶糖

3
00:02:34,154 --> 00:02:35,197
謝謝

4
00:02:35,906 --> 00:02:36,907
妳們兩個累不累啊？

5
00:02:37,741 --> 00:02:38,867
就快到了

6
00:02:50,796 --> 00:02:51,588
小梅，快躲起來

ENGLISH:

25
00:02:36,120 --> 00:02:37,872
Dad, do you want a caramel?

26
00:02:38,080 --> 00:02:40,833
Thanks. Aren't you tired?

27
00:02:41,040 --> 00:02:41,552
All right.

28
00:02:41,880 --> 00:02:42,949
We're almost there.

29
00:02:54,440 --> 00:02:55,350
Mei, hide!

The expected output is:

{
    "explanation":
        [
            "'謝謝' and '妳們兩個累不累啊？' correspond to 'Thanks. Aren't you tired?'",
            "No corresponding Chinese for 'All right.'",
        ],
    "synchronization": 
        [
            {
                "chinese": [2],
                "end": ["chinese", 2],
                "english": [25],
                "start": ["chinese", 2],
            },
            {
                "chinese": [3, 4],
                "end": ["chinese", 4],
                "english": [26],
                "start": ["chinese", 3],
            },
            {
                "chinese": [5],
                "end": ["chinese", 5],
                "english": [28],
                "start": ["chinese", 5],
            },
            {
                "chinese": [6],
                "end": ["chinese", 6],
                "english": [29],
                "start": ["chinese", 6],
            },
        ]
}

2. Given the following input:

CHINESE:

35
00:06:12,789 --> 00:06:14,624
那叫做樟樹

36
00:06:16,627 --> 00:06:17,503
樟樹耶

37
00:06:17,628 --> 00:06:18,629
樟樹

38
00:06:31,475 --> 00:06:32,351
橡果子

39
00:06:34,144 --> 00:06:36,229
我看一下

ENGLISH:

58
00:06:16,600 --> 00:06:18,318
It's a camphor tree.

59
00:06:20,440 --> 00:06:22,396
Camphor tree...

60
00:06:31,680 --> 00:06:32,590
Oops!

61
00:06:35,480 --> 00:06:36,276
An acorn!

62
00:06:38,040 --> 00:06:39,712
Show me.

The expected output is:

{
    "explanation":
        [
            "'樟樹' has no corresponding English",
            "No corresponding Chinese for 'Oops!'",
        ],
    "synchronization":
        [
            {
                "chinese": [35],
                "end": ["chinese", 35],
                "english": [58],
                "start": ["chinese", 35],
            },
            {
                "chinese": [36],
                "end": ["chinese", 36],
                "english": [59],
                "start": ["chinese", 36],
            },
            {
                "chinese": [37],
                "end": ["chinese", 37],
                "english": [],
                "start": ["chinese", 37],
            },
            {
                "chinese": [38],
                "end": ["chinese", 38],
                "english": [61],
                "start": ["chinese", 38],
            },
            {
                "chinese": [39],
                "end": ["chinese", 39],
                "english": [62],
                "start": ["chinese", 39],
            },
        ]
}

3. Given the following input:

CHINESE:

50
00:07:16,353 --> 00:07:18,355
這要搬到哪兒呢？

51
00:07:18,981 --> 00:07:21,150
放這裡，我這就開門

52
00:07:21,358 --> 00:07:23,151
小月，妳去把後門打開

53
00:07:23,277 --> 00:07:24,028
好

54
00:07:24,152 --> 00:07:25,737
去了就看得到

ENGLISH:

73
00:07:20,280 --> 00:07:22,236
Where shall I put this?

74
00:07:22,840 --> 00:07:27,436
Here, I'll get the door for you. Satsuki, open up the kitchen.

75
00:07:28,080 --> 00:07:29,479
It's just round the back.

The expected output is:

{
    "explanation":
        [
            "'放這裡，我這就開門' and '小月，妳去把後門打開' correspond to 'Here, I'll get the door for you. Satsuki, open up the kitchen.'",
            "'好' has no corresponding English",
        ],
    "synchronization":
        [
            {
                "chinese": [50],
                "end": ["chinese", 50],
                "english": [73],
                "start": ["chinese", 50],
            },
            {
                "chinese": [51, 52],
                "end": ["chinese", 52],
                "english": [74],
                "start": ["chinese", 51],
            },
            {
                "chinese": [53],
                "end": ["chinese", 53],
                "english": [],
                "start": ["chinese", 53],
            },
            {
                "chinese": [54],
                "end": ["chinese", 54],
                "english": [75],
                "start": ["chinese", 54],
            },
        ]
}

4. Given the following input:

CHINESE:

62
00:08:39,228 --> 00:08:41,021
爸爸，有怪東西耶

63
00:08:41,146 --> 00:08:41,980
松鼠嗎？

64
00:08:42,105 --> 00:08:43,106
不知道

65
00:08:43,273 --> 00:08:45,400
不像蟑螂也不像老鼠

66
00:08:45,526 --> 00:08:46,944
只知道是一堆黑黑的東西

67
00:09:00,290 --> 00:09:01,416
有沒有？

68
00:09:02,709 --> 00:09:04,502
那一定是「灰塵精靈」

69
00:09:04,920 --> 00:09:06,213
灰塵精靈

70
00:09:06,380 --> 00:09:07,381
畫冊裡有嗎？

ENGLISH:

83
00:08:43,120 --> 00:08:44,792
Dad, there's something in here.

84
00:08:45,000 --> 00:08:45,716
A squirrel?

85
00:08:45,960 --> 00:08:50,590
Dunno. A bunch of black things but not roaches or mice.

86
00:08:50,840 --> 00:08:52,592
Really?

87
00:09:04,160 --> 00:09:05,229
Can you see 'em?

88
00:09:06,680 --> 00:09:08,398
I think they were... soot gremlins.

89
00:09:08,680 --> 00:09:11,433
'Gremlins’? Like in my picture book?

The expected output is:

{
    "explanation":
        [
            "'不知道', '不像蟑螂也不像老鼠', and '只知道是一堆黑黑的東西' correspond to 'Dunno. A bunch of black things but not roaches or mice.'",
            "No corresponding Chinese for 'Really?'",
            "'灰塵精靈' and '畫冊裡有嗎？' correspond to ''Gremlins'? Like in my picture book?'",
        ],
    "synchronization":
        [
            {
                "chinese": [62],
                "end": ["chinese", 62],
                "english": [83],
                "start": ["chinese", 62],
            },
            {
                "chinese": [63],
                "end": ["chinese", 63],
                "english": [84],
                "start": ["chinese", 63],
            },
            {
                "chinese": [64, 65, 66],
                "end": ["chinese", 66],
                "english": [85],
                "start": ["chinese", 64],
            },
            {
                "chinese": [67],
                "end": ["chinese", 67],
                "english": [87],
                "start": ["chinese", 67],
            },
            {
                "chinese": [68],
                "end": ["chinese", 68],
                "english": [88],
                "start": ["chinese", 68],
            },
            {
                "chinese": [69, 70],
                "end": ["chinese", 70],
                "english": [89],
                "start": ["chinese", 69],
            },
        ]
}
"""

    def __init__(self):
        self.model = "gpt-4o"
        self.client = OpenAI()

    def synchronize_bilingual_subtitles(
        self,
        hanzi: SubtitleSeries,
        english: SubtitleSeries,
    ) -> SubtitleSeries:
        # 1
        #   Get subtitles 0-15 from hanzi, and the amount of time that they cover
        #   Get the corresponding subtitles from english
        #   Prompt LLM to synchronize the subtitles
        #   Ensure that the output can be parsed into a SubtitleSeries

        # 2
        #   Get subtitles 11-25 from hanzi, and the amount of time that they cover
        #   Get the corresponding subtitles from english
        #   Prompt LLM to synchronize the subtitles
        #   Ensure that the output can be parsed into a SubtitleSeries

        # 3
        #   Validate that subtitles 11-14 are the same from both queries
        #   If not, prompt LLM to reconcile the two

        # 4
        #   Get subtitles 21-35 from hanzi, and the amount of time that they cover
        #   Get the corresponding subtitles from english
        #   Prompt LLM to synchronize the subtitles
        #   Ensure that the output can be parsed into a SubtitleSeries

        # 5
        #   Validate that subtitles 21-24 are the same from both queries
        #   If not, prompt LLM to reconcile the two

        block_size = 16
        overlap = 12

        start_index = 0
        end_index = 0

        bilingual = SubtitleSeries()
        blocks = get_subtitle_blocks_for_synchronization(
            hanzi, english, block_size, overlap
        )
        last_bilingual_block = None
        for i, (hanzi_block, english_block) in enumerate(blocks):
            print(f"Processing block {i + 1}/{len(blocks)}")
            bilingual_block = self.get_synchronization(hanzi_block, english_block)

            if last_bilingual_block:
                overlap_previous_events = last_bilingual_block.events[-overlap:]
                overlap_current_events = bilingual_block.events[:overlap]
                if overlap_previous_events != overlap_current_events:
                    print(
                        f"Mismatch between last and current block:\n\n",
                        f"{pformat(overlap_previous_events)}\n\n",
                        f"{pformat(overlap_current_events)}",
                    )

            bilingual.events.extend(bilingual_block.events[: (block_size - overlap)])

            last_bilingual_block = bilingual_block

        return bilingual

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

    def check_bilingual_subtitle_block(
        self, hanzi: SubtitleSeries, english: SubtitleSeries
    ) -> SubtitleSeries:
        pass
