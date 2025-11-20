#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""KOB 中文 fusion test cases."""

from __future__ import annotations

from scinoephile.image.zhongwen.fusion import ZhongwenFusionTestCase

test_cases = [
    ZhongwenFusionTestCase(
        lens="少爺！\n準備好了",
        paddle="少爺！準備好了",
        ronghe="少爺！\n準備好了",
        beizhu="采用了Google Lens的汉字和标点，保留了PaddleOCR的换行格式，将“少爺！”和“準備好了”分为两行。",
        difficulty=1,
    ),
    ZhongwenFusionTestCase(
        lens="師爺，少爺寫的是甚麼？",
        paddle="師爺，少爺寫的是甚麼",
        ronghe="師爺，少爺寫的是甚麼？",
        beizhu="采用了Google Lens "
        "OCR的汉字和标点，保留了PaddleOCR的换行格式（本句无换行），最终结果在句末加上了问号。",
        difficulty=1,
        verified=True,
    ),
]  # test_cases
"""KOB 中文 fusion test cases."""


__all__ = [
    "test_cases",
]
