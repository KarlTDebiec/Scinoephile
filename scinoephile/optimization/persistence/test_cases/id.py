#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Identifiers for persisted LLM test cases."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping

__all__ = ["get_test_case_id"]


def get_test_case_id(
    query: Mapping[str, object],
    answer: Mapping[str, object],
    *,
    operation: str,
) -> str:
    """Compute canonical identifier for a test case.

    Arguments:
        query: query payload
        answer: answer payload
        operation: operation to which the test case belongs
    Returns:
        deterministic hexadecimal identifier
    Raises:
        ValueError: if operation is empty
    """
    if not operation.strip():
        raise ValueError("Operation must not be empty.")
    payload_json = json.dumps(
        {
            "answer": dict(answer),
            "operation": operation,
            "query": dict(query),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(payload_json.encode()).hexdigest()
    return digest
