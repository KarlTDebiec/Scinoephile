#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.eng.get_eng_block_reviewed."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from scinoephile.core.llms import LLMProvider
from scinoephile.lang.eng.block_review import (
    get_eng_block_reviewed,
    get_eng_block_reviewer,
)
from test.data.t import get_t_eng_block_review_test_cases
from test.helpers import assert_series_equal


def test_get_eng_block_reviewed_t_from_verified_cases(
    request: pytest.FixtureRequest,
):
    """Test get_eng_block_reviewed with T verified block review cases.

    Arguments:
        request: pytest request for fixture lookup
    """
    provider = Mock(spec=LLMProvider)
    processor = get_eng_block_reviewer(
        test_cases=get_t_eng_block_review_test_cases(),
        provider=provider,
    )
    output = get_eng_block_reviewed(
        request.getfixturevalue("t_eng_fuse_clean_validate"),
        processor=processor,
    )

    assert_series_equal(
        output,
        request.getfixturevalue("t_eng_fuse_clean_validate_review"),
    )
    provider.chat_completion.assert_not_called()
