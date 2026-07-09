#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Identifiers for persisted LLM test cases."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping

from scinoephile.core.llms import Answer, Query

__all__ = ["get_test_case_id"]


def get_test_case_id(
    query: Query | Mapping[str, object],
    answer: Answer | Mapping[str, object],
    *,
    operation: str,
    variant: str,
) -> str:
    """Compute canonical identifier for a test case.

    Arguments:
        query: query payload
        answer: answer payload
        operation: operation to which the test case belongs
        variant: stable schema variant within the operation
    Returns:
        deterministic hexadecimal identifier
    Raises:
        ValueError: if operation or variant is empty
    """
    if not operation.strip():
        raise ValueError("Operation must not be empty.")
    if not variant.strip():
        raise ValueError("Variant must not be empty.")
    if isinstance(query, Query):
        query_payload = query.model_dump(mode="json")
    else:
        query_payload = dict(query)
    if isinstance(answer, Answer):
        answer_payload = answer.model_dump(mode="json")
    else:
        answer_payload = dict(answer)
    payload_json = json.dumps(
        {
            "answer": answer_payload,
            "operation": operation,
            "query": query_payload,
            "variant": variant,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(payload_json.encode()).hexdigest()
    return digest
