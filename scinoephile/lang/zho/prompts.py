#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for 中文."""

from __future__ import annotations

from abc import ABC
from inspect import isroutine
from typing import Any, ClassVar

from scinoephile.llms.base import Prompt

from .conversion import OpenCCConfig, get_zho_text_converted

__all__ = ["ZhoHansPrompt"]


class ZhoHansPrompt(Prompt, ABC):
    """LLM correspondence text for 简体中文."""

    opencc_config: ClassVar[OpenCCConfig | None] = None
    """Config with which to convert characters from 简体中文 present in parent class."""

    # Prompt
    schema_intro: ClassVar[str] = "你的回复必须是一个具有以下结构的 JSON 对象："
    """Text preceding schema description."""

    few_shot_intro: ClassVar[str] = "下面是一些查询及其预期答案的示例："
    """Text preceding few-shot examples."""

    few_shot_query_intro: ClassVar[str] = "示例查询："
    """Text preceding each few-shot example query."""

    few_shot_answer_intro: ClassVar[str] = "预期答案："
    """Text preceding each few-shot expected answer."""

    # Answer validation errors
    answer_invalid_pre: ClassVar[str] = (
        "你之前的回复不是有效的 JSON，或未符合预期的模式要求。错误详情："
    )
    """Text preceding answer validation errors."""

    answer_invalid_post: ClassVar[str] = (
        "请重新尝试，并仅返回一个符合该模式要求的有效 JSON 对象。"
    )
    """Text following answer validation errors."""

    # Test case validation errors
    test_case_invalid_pre: ClassVar[str] = (
        "你之前的回复是符合答案模式的有效 JSON，但不适用于当前的特定查询。错误详情："
    )
    """Text preceding test case validation errors."""

    test_case_invalid_post: ClassVar[str] = "请根据错误信息对你的回复进行相应修改。"
    """Text following test case validation errors."""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Automatically convert class attributes using OpenCC configuration.

        This metaclass hook automatically converts class attributes from simplified
        to traditional Chinese (or vice versa) when a subclass sets `opencc_config`.
        It walks through the method resolution order (MRO) and converts string values
        as well as strings within tuples, lists, and dictionaries inherited from
        parent classes that have not been explicitly overridden in the subclass.

        Arguments:
            **kwargs: Additional keyword arguments passed to parent __init_subclass__
        """
        super().__init_subclass__(**kwargs)

        if cls.opencc_config is None:
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

                new_value = cls._convert_value(value, cls.opencc_config)
                if new_value is not value:
                    setattr(cls, name, new_value)

    @classmethod
    def _convert_value(cls, value: Any, config: OpenCCConfig) -> Any:
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
