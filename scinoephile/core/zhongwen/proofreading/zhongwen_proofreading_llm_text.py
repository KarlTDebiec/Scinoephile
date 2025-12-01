#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text strings to be used for LLM correspondence for 中文 proofreading."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.core.zhongwen.abcs import ZhongwenLLMText


class ZhongwenProofreadingLLMText(ZhongwenLLMText):
    """Text strings to be used for LLM correspondence for 中文 proofreading."""

    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        你负责校对由 OCR 识别生成的中文字幕。
        你的任务仅限于纠正 OCR 识别错误（例如错字、漏字、字符混淆等），
        不得进行任何风格或语法上的润色，也不要添加或修改标点符号。
        对于每一条字幕，如有需要修改，请提供修改后的完整字幕，并附上一条说明所作修改的备注。
        如果不需要修改，请将修改后的字幕和备注都留空字符串。""")
    """Base system prompt."""

    answer_example_xiugai_description: ClassVar[str] = (
        "字幕 {idx} 的修改结果，如无需修改则为空字符串。"
    )

    answer_example_beizhu_description: ClassVar[str] = (
        "关于字幕 {idx} 修改的备注说明，如无需修改则为空字符串。"
    )
