#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared command-line helpers for subtitle audits."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path

from scinoephile.core.llms import Manager, TestCase
from scinoephile.core.llms.utils import load_test_cases_from_json
from scinoephile.llms.review import ReviewManager

__all__ = [
    "load_audit_test_cases",
    "load_review_test_cases",
    "write_audit_report",
]


def load_audit_test_cases(
    parser: ArgumentParser,
    json_path: Path,
    manager_cls: type[Manager],
    *,
    workflow_name: str,
) -> list[TestCase]:
    """Load test cases from workflow JSON.

    Arguments:
        parser: parser used to report user-facing errors
        json_path: test-case JSON path
        manager_cls: manager defining the test-case model
        workflow_name: workflow name used in errors
    Returns:
        loaded test cases
    """
    try:
        return load_test_cases_from_json(
            json_path,
            manager_cls,
            manager_cls.base_prompt,
        )
    except (KeyError, OSError, TypeError, UnicodeError, ValueError) as exc:
        parser.error(f"Unable to load {workflow_name} JSON: {exc}")


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
    return load_audit_test_cases(
        parser,
        json_path,
        ReviewManager,
        workflow_name="review",
    )


def write_audit_report(
    parser: ArgumentParser,
    report: str,
    outfile_path: Path | None,
    overwrite: bool,
):
    """Write a report to stdout or a file.

    Arguments:
        parser: parser used to report user-facing errors
        report: Markdown report
        outfile_path: optional output file path
        overwrite: whether to overwrite an existing output file
    """
    if outfile_path is None:
        if overwrite:
            parser.error("--overwrite may only be used with --outfile")
        print(report, end="")
        return
    if outfile_path.exists() and not overwrite:
        parser.error(f"File exists: {outfile_path}; use --overwrite to replace it")
    try:
        outfile_path.write_text(report, encoding="utf-8")
    except OSError as exc:
        parser.error(str(exc))
