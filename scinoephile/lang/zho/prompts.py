#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for standard Chinese."""

from __future__ import annotations

from abc import ABC
from inspect import isroutine
from typing import ClassVar

from scinoephile.core.llms import Prompt

from .script.conversion import OpenCCConfig, get_zho_text_converted

__all__ = ["PromptZhoHant"]


class PromptZhoHant(Prompt, ABC):
    """LLM correspondence text for traditional standard Chinese."""

    opencc_config: ClassVar[OpenCCConfig | None] = None
    """Config for converting Chinese characters from the parent class."""

    # Prompt
    schema_intro: ClassVar[str] = "你的回覆必須是一個具有以下結構的 JSON 對象："
    """Text preceding schema description."""

    few_shot_intro: ClassVar[str] = "下面是一些查詢及其預期答案的示例："
    """Text preceding few-shot examples."""

    few_shot_query_intro: ClassVar[str] = "示例查詢："
    """Text preceding each few-shot example query."""

    few_shot_answer_intro: ClassVar[str] = "預期答案："
    """Text preceding each few-shot expected answer."""

    # Answer validation errors
    answer_invalid_pre: ClassVar[str] = (
        "你之前的回覆不是有效的 JSON，或未符合預期的模式要求。錯誤詳情："
    )
    """Text preceding answer validation errors."""

    answer_invalid_post: ClassVar[str] = (
        "請重新嘗試，並僅返回一個符合該模式要求的有效 JSON 對象。"
    )
    """Text following answer validation errors."""

    # Test case validation errors
    test_case_invalid_pre: ClassVar[str] = (
        "你之前的回覆是符合答案模式的有效 JSON，但不適用於當前的特定查詢。錯誤詳情："
    )
    """Text preceding test case validation errors."""

    test_case_invalid_post: ClassVar[str] = "請根據錯誤信息對你的回覆進行相應修改。"
    """Text following test case validation errors."""

    def __init_subclass__(cls, **kwargs: object):
        """Automatically convert class attributes using OpenCC configuration.

        This metaclass hook automatically converts class attributes from the
        parent Chinese script to the target script when a subclass explicitly sets
        `opencc_config`.
        It walks through the method resolution order (MRO) and converts string values
        as well as strings within tuples, lists, and dictionaries inherited from
        parent classes that have not been explicitly overridden in the subclass.

        Arguments:
            **kwargs: Additional keyword arguments passed to parent __init_subclass__
        """
        super().__init_subclass__(**kwargs)

        config = cls.__dict__.get("opencc_config")
        if not isinstance(config, OpenCCConfig):
            return

        for base in cls.__mro__[1:]:
            for name, value in vars(base).items():
                # Skip private attributes
                if name.startswith("_"):
                    continue
                # Skip already overridden attributes
                if name in cls.__dict__:
                    continue
                # Skip methods and descriptors
                if isroutine(value):
                    continue
                # Skip classmethods, staticmethods, and properties
                if isinstance(value, (classmethod, staticmethod, property)):
                    continue

                new_value = cls._convert_value(value, config)
                if new_value is not value:
                    setattr(cls, name, new_value)

    @classmethod
    def _convert_value(cls, value: object, config: OpenCCConfig) -> object:
        """Convert value to target Chinese script using OpenCC configuration.

        Arguments:
            value: value to convert
            config: OpenCC configuration for conversion
        Returns:
            converted value
        """
        if isinstance(value, str):
            return get_zho_text_converted(value, config)
        if isinstance(value, tuple):
            return tuple(cls._convert_value(x, config) for x in value)
        if isinstance(value, list):
            return [cls._convert_value(x, config) for x in value]
        if isinstance(value, dict):
            return {k: cls._convert_value(val, config) for k, val in value.items()}
        return value
