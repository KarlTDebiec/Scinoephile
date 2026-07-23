#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Identifiers for persisted LLM test cases."""

from __future__ import annotations

import hashlib
import json

from pydantic import JsonValue

from scinoephile.core.llms import Manager

__all__ = ["get_test_case_id"]


def get_test_case_id(
    query: dict[str, JsonValue],
    answer: dict[str, JsonValue],
    manager_cls: type[Manager],
) -> str:
    """Compute canonical identifier for a test case.

    Arguments:
        query: query payload
        answer: answer payload
        manager_cls: manager defining the test case's operation
    Returns:
        deterministic hexadecimal identifier
    """
    payload_json = json.dumps(
        {
            "answer": dict(answer),
            "operation": manager_cls.operation,
            "query": dict(query),
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(payload_json.encode()).hexdigest()
