#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Identifiers for persisted LLM test cases."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping

from pydantic import JsonValue

from scinoephile.core.llms import OperationSpec

__all__ = ["get_test_case_id"]


def get_test_case_id(
    query: Mapping[str, JsonValue],
    answer: Mapping[str, JsonValue],
    spec: OperationSpec,
) -> str:
    """Compute canonical identifier for a test case.

    Arguments:
        query: query payload
        answer: answer payload
        spec: operation to which the test case belongs
    Returns:
        deterministic hexadecimal identifier
    """
    payload_json = json.dumps(
        {
            "answer": dict(answer),
            "operation": spec.operation,
            "query": dict(query),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload_json.encode()).hexdigest()
