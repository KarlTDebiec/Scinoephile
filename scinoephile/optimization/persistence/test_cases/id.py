#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Identifiers for persisted LLM test cases."""

from __future__ import annotations

import hashlib
import json

from scinoephile.core.llms import Answer, Query

__all__ = ["get_test_case_id"]


def get_test_case_id(query: Query, answer: Answer) -> str:
    """Compute canonical identifier for a test case.

    Arguments:
        query: query payload
        answer: answer payload
    Returns:
        deterministic hexadecimal identifier
    """
    query_json = json.dumps(
        query.model_dump(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    answer_json = json.dumps(
        answer.model_dump(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(f"{query_json}\n{answer_json}".encode()).hexdigest()
    return digest
