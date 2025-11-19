#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""KOB 中文 fusion test cases."""

from __future__ import annotations

from scinoephile.image.zhongwen.fusion import ZhongwenFusionTestCase

test_cases = [
    ZhongwenFusionTestCase(
        lens="少爺！\n準備好了",
        paddle="少爺！準備好了",
        ronghe="少爺！準備好了",
        beizhu="Google Lens 中存在但 PaddleOCR 中不存在的换行符将被忽略。",
        difficulty=1,
        prompt=True,
        verified=True,
    ),
    ZhongwenFusionTestCase(
        lens="師爺，少爺寫的是甚麼？",
        paddle="師爺，少爺寫的是甚麼",
        ronghe="師爺，少爺寫的是甚麼？",
        beizhu="包含 Google Lens 中存在但 PaddleOCR 中不存在的问号。",
        difficulty=1,
        prompt=True,
        verified=True,
    ),
    ZhongwenFusionTestCase(
        lens="你唸反了，\n老爺",
        paddle="你唸反了，老爺",
        ronghe="你唸反了，老爺",
        beizhu="忽略了 Google Lens 中存在但 PaddleOCR 中不存在的换行符。",
        difficulty=1,
        verified=True,
    ),
    ZhongwenFusionTestCase(
        lens="爹，\n我們蘇察哈爾家",
        paddle="我們蘇察哈爾家",
        ronghe="爹，我們蘇察哈爾家",
        beizhu="包括 Google Lens 中存在但 PaddleOCR 中不存在的〝爹〞；以及省略 Google Lens 中存在但 "
        "PaddleOCR 中不存在的换行符。",
        difficulty=1,
        prompt=True,
        verified=True,
    ),
    ZhongwenFusionTestCase(
        lens="爹，這可是非同少可",
        paddle="爹，  這可是非同少可",
        ronghe="爹，這可是非同少可",
        beizhu="PaddleOCR 中存在但 Google Lens 中不存在的空格将被忽略。",
        difficulty=1,
        prompt=True,
        verified=True,
    ),
    ZhongwenFusionTestCase(
        lens="阿燦，\n先把它裱起來",
        paddle="阿燦，先把它裱起來",
        ronghe="阿燦，先把它裱起來",
        beizhu="Google Lens 中存在但 PaddleOCR 中不存在的换行符被省略，保留了 PaddleOCR 的连贯格式。",
        difficulty=1,
        verified=True,
    ),
    ZhongwenFusionTestCase(
        lens="師爺，把它掛在最當眼的地方",
        paddle="師爺  把它掛在最當眼的地方",
        ronghe="師爺，把它掛在最當眼的地方",
        beizhu="PaddleOCR 中存在但 Google Lens 中不存在的空格将被忽略，保留 Google Lens 的标点符号。",
        difficulty=1,
        verified=True,
    ),
    ZhongwenFusionTestCase(
        lens="這樣吧，\n師爺",
        paddle="這樣吧 師爺",
        ronghe="這樣吧，師爺",
        beizhu="采用 Google Lens 中的逗号，省略 Google Lens 中存在但 PaddleOCR 中不存在的换行符。",
        difficulty=1,
        verified=True,
    ),
    ZhongwenFusionTestCase(
        lens="你先揹著它簪花掛紅，遊行威風一下",
        paddle="你先指著它簪花掛紅，遊行威風一下",
        ronghe="你先揹著它簪花掛紅，遊行威風一下",
        beizhu="采用 Google Lens 识别的“揹著”替换 PaddleOCR 的“指著”，因 Google Lens "
        "在汉字识别上更可靠。",
        difficulty=1,
    ),
    ZhongwenFusionTestCase(
        lens="阿燦，來⋯坐⋯",
        paddle="阿燦，來·坐·",
        ronghe="阿燦，來⋯坐⋯",
        beizhu="采用 Google Lens 中的省略号“⋯”替换 PaddleOCR 中的间隔号“·”，以保证标点准确。",
        difficulty=1,
    ),
    ZhongwenFusionTestCase(
        lens="那壽頭真是⋯",
        paddle="那壽頭真是·",
        ronghe="那壽頭真是⋯",
        beizhu="采用 Google Lens 中的省略号“⋯”，替换 PaddleOCR 中的“·”，以保证标点准确。",
        difficulty=1,
    ),
    ZhongwenFusionTestCase(
        lens="過來，\n過來",
        paddle="過來，過來",
        ronghe="過來，過來",
        beizhu="Google Lens 中存在但 PaddleOCR 中不存在的换行符被省略，保留了 PaddleOCR 的连贯格式。",
        difficulty=1,
    ),
    ZhongwenFusionTestCase(
        lens="老爺，\n甚麼事？",
        paddle="老爺，甚麼事？",
        ronghe="老爺，甚麼事？",
        beizhu="Google Lens 中存在但 PaddleOCR 中不存在的换行符被省略，保留了 Google Lens "
        "的汉字和标点。",
        difficulty=1,
    ),
]  # test_cases
"""KOB 中文 fusion test cases."""


__all__ = [
    "test_cases",
]
