#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Service for interacting with OpenAI API."""
from __future__ import annotations

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from scinoephile.core import SubtitleSeries


class SubtitleGroupResponse(BaseModel):
    chinese: list[int]
    english: list[int]


class SubtitleSeriesResponse(BaseModel):
    explanation: list[str]
    synchronization: list[SubtitleGroupResponse]


class OpenAiService:
    synchronize_bilingual_subtitle_block_prompt = """
Instructions:
* Each request will start with CHINESE: followed by a series of Chinese subtitles in SRT
  format, and then ENGLISH: followed by a series of English subtitles in SRT format.
* You are tasked with mapping the English subtitles to their corresponding Chinese
  subtitles, based on their meaning and timing.
* Your response should be a JSON object following this exact specification:

{
    "synchronization": [
        {
            "chinese": [<list of Chinese subtitle indexes>],
            "english": [<list of English subtitle indexes>],
        },
        ...
    ]
    "explanation": [<list of explanations of ONLY subtitles that did not map cleanly
      1:1; specific examples of situations that warrant explanation are list below>],
}

* "synchronization" defines a list of synchronization groups. Each group contains a
  group of Chinese and English subtitles that contain the same meaning.
* Within each synchronization group:
    * The "chinese" field lists the indices of the Chinese subtitles in the group.
    * The "english" field lists the indices of the English subtitles in the group
* The following rules should never be violated:
  * A Chinese subtitle should never be skipped.
  * Chinese subtitles should never be reordered.
  * English subtitles should never be reordered.
* The following guidelines should be followed:
  * Use the text of the subtitles as the primary guide for alignment, considering your
    understanding of both languages. The meaning of the subtitles should roughly align,
    though there may be variations between the sets of subtitles.
  * Timing should roughly align between Chinese and English sources, but may not be
    exact.
  * Most of the time, the Chinese and English subtitles will align 1:1. In these cases,
    "chinese" and "english" for the synchronization group will contain only a single
    index each.
  * English subtitles may be skipped if there is no corresponding Chinese subtitle. This
    should be relatively rare.

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
* Do not skip any Chinese subtitles.

Here are some examples to help you understand the task better:

1. Given the following input:

CHINESE:

1
00:00:00,000 --> 00:00:01,877
爸爸，牛奶糖

2
00:00:02,002 --> 00:00:03,045
谢谢

3
00:00:03,754 --> 00:00:04,755
妳们两个累不累啊？

4
00:00:05,589 --> 00:00:06,715
就快到了

5
00:00:18,644 --> 00:00:19,436
小梅，快躲起来

ENGLISH:

1
00:00:00,000 --> 00:00:01,752
Dad, do you want a caramel?

2
00:00:01,960 --> 00:00:04,713
Thanks. Aren't you tired?

3
00:00:04,920 --> 00:00:05,432
All right.

4
00:00:05,760 --> 00:00:06,829
We're almost there.

5
00:00:18,320 --> 00:00:19,230
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
                "english": [1],
            },
            {
                "chinese": [2, 3],
                "english": [2],
            },
            {
                "chinese": [4],
                "english": [4],
            },
            {
                "chinese": [5],
                "english": [5],
            },
        ],
}

2. Given the following input:

CHINESE:

1
00:00:00,157 --> 00:00:01,992
那叫做樟树

2
00:00:03,995 --> 00:00:04,871
樟树耶

3
00:00:04,996 --> 00:00:05,997
樟树

4
00:00:18,843 --> 00:00:19,719
橡果子

5
00:00:21,512 --> 00:00:23,597
我看一下

ENGLISH:

1
00:00:00,000 --> 00:00:01,718
It's a camphor tree.

2
00:00:03,840 --> 00:00:05,796
Camphor tree...

3
00:00:15,080 --> 00:00:15,990
Oops!

4
00:00:18,880 --> 00:00:19,676
An acorn!

5
00:00:21,440 --> 00:00:23,112
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
                "chinese": [1],
                "english": [1],
            },
            {
                "chinese": [2],
                "english": [2],
            },
            {
                "chinese": [3],
                "english": [],
            },
            {
                "chinese": [4],
                "english": [4],
            },
            {
                "chinese": [5],
                "english": [5],
            },
        ],
}

3. Given the following input:

CHINESE:

1
00:00:00,041 --> 00:00:02,043
这要搬到哪儿呢？

2
00:00:02,669 --> 00:00:04,838
放这里，我这就开门

3
00:00:05,046 --> 00:00:06,839
小月，妳去把后门打开

4
00:00:06,965 --> 00:00:07,716
好

5
00:00:07,840 --> 00:00:09,425
去了就看得到

ENGLISH:

1
00:00:00,000 --> 00:00:01,956
Where shall I put this?

2
00:00:02,560 --> 00:00:07,156
Here, I'll get the door for you. Satsuki, open up the kitchen.

3
00:00:07,800 --> 00:00:09,199
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
                "chinese": [1],
                "english": [1],
            },
            {
                "chinese": [2, 3],
                "english": [2],
            },
            {
                "chinese": [4],
                "english": [],
            },
            {
                "chinese": [5],
                "english": [3],
            },
        ],
}

4. Given the following input:

CHINESE:

1
00:00:00,076 --> 00:00:01,869
爸爸，有怪东西耶

2
00:00:01,994 --> 00:00:02,828
松鼠吗？

3
00:00:02,953 --> 00:00:03,954
不知道

4
00:00:04,121 --> 00:00:06,248
不像蟑螂也不像老鼠

5
00:00:06,374 --> 00:00:07,792
只知道是一堆黑黑的东西

6
00:00:21,138 --> 00:00:22,264
有没有？

7
00:00:23,557 --> 00:00:25,350
那一定是「灰尘精灵」

8
00:00:25,768 --> 00:00:27,061
灰尘精灵

9
00:00:27,228 --> 00:00:28,229
画册里有吗？

ENGLISH:

1
00:00:00,000 --> 00:00:01,672
Dad, there's something in here.

2
00:00:01,880 --> 00:00:02,596
A squirrel?

3
00:00:02,840 --> 00:00:07,470
Dunno. A bunch of black things but not roaches or mice.

4
00:00:07,720 --> 00:00:09,472
Really?

5
00:00:21,040 --> 00:00:22,109
Can you see 'em?

6
00:00:23,560 --> 00:00:25,278
I think they were... soot gremlins.

7
00:00:25,560 --> 00:00:28,313
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
                "chinese": [1],
                "english": [1],
            },
            {
                "chinese": [2],
                "english": [2],
            },
            {
                "chinese": [3, 4, 5],
                "english": [3],
            },
            {
                "chinese": [6],
                "english": [5],
            },
            {
                "chinese": [7],
                "english": [6],
            },
            {
                "chinese": [8, 9],
                "english": [7],
            },
        ]
}
"""

    def __init__(self):
        self.model = "gpt-4o"
        self.client = OpenAI()

    def get_synchronization(
        self, hanzi: SubtitleSeries, english: SubtitleSeries
    ) -> SubtitleSeriesResponse:
        query = (
            f"CHINESE:\n\n"
            f"{hanzi.to_string('srt')}\n\n"
            f"ENGLISH:\n\n"
            f"{english.to_string('srt')}"
        )

        completion = self.client.beta.chat.completions.parse(
            model=self.model,
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
