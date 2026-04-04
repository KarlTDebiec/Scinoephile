#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Compatibility wrapper for LLM utility helpers."""

from __future__ import annotations

from scinoephile.core.llms.utils import (
    load_test_cases_from_json,
    save_test_cases_to_json,
)

__all__ = ["load_test_cases_from_json", "save_test_cases_to_json"]
