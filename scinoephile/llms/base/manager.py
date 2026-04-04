#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Compatibility wrapper for LLM manager interfaces."""

from __future__ import annotations

from scinoephile.core.llms import manager as _manager
from scinoephile.core.llms.manager import Manager

TestCaseClsKwargs = _manager.TestCaseClsKwargs

__all__ = ["Manager", "TestCaseClsKwargs"]
