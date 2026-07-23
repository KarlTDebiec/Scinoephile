#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Utilities for subtitle audit command-line interfaces."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path

from scinoephile.core.llms import TestCase
from scinoephile.llms.review import ReviewManager

from .audit_cli_base import AuditCliBase

__all__ = ["load_review_test_cases"]


def load_review_test_cases(
    parser: ArgumentParser,
    json_path: Path | None,
) -> Sequence[TestCase]:
    """Load optional review test cases from JSON.

    Arguments:
        parser: parser used to report user-facing errors
        json_path: optional review JSON path
    Returns:
        loaded review test cases
    """
    if json_path is None:
        return ()
    return AuditCliBase.load_test_cases(
        parser,
        json_path,
        ReviewManager,
        workflow_name="review",
    )
