#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Compatibility wrapper for LLM tool types."""

from __future__ import annotations

from scinoephile.core.llms import tools as _tools

LLMToolSpec = _tools.LLMToolSpec
ToolHandler = _tools.ToolHandler

__all__ = ["LLMToolSpec", "ToolHandler"]
