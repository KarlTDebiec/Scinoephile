#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MNT 中文 fusion test cases."""

from __future__ import annotations

from scinoephile.image.zhongwen.fusion import ZhongwenFusionTestCase

# noinspection PyArgumentList
test_cases = [
    ZhongwenFusionTestCase(
        lens="《龙猫》",
        paddle="《龙猫",
        ronghe="《龙猫》",
        beizhu="包括了 Google Lens OCR 中存在但 PaddleOCR 中不存在的右引号。",
        difficulty=1,
        verified=True,
    ),
    ZhongwenFusionTestCase(
        lens="小美，\n快躲起来",
        paddle="小美，快躲起来",
        ronghe="小美，快躲起来",
        beizhu="省略了 Google Lens OCR 中存在但 PaddleOCR 中不存在的换行符。",
        difficulty=1,
        verified=True,
    ),
    ZhongwenFusionTestCase(
        lens="还以为是警察呢！",
        paddle="还以为是警察呢",
        ronghe="还以为是警察呢！",
        beizhu="包括了 Google Lens OCR 中存在但 PaddleOCR 中不存在的感叹号。",
        difficulty=1,
        verified=True,
    ),
]  # test_cases
"""MNT 中文 fusion test cases."""

__all__ = [
    "test_cases",
]
