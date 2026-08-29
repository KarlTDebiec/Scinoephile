#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

"""Repository-wide docstring structure enforcement."""

from __future__ import annotations

import ast
from pathlib import Path

from scinoephile.common import package_root
from test.helpers.files import get_python_files
from test.style.docs.checks import DocstringViolation, get_docstring_violations

DOCSTRING_BASELINE_PATH = Path(__file__).with_name("docstring_violations.txt")
"""Path to the checked-in docstring violation baseline."""


def test_python_docstrings_follow_repository_structure():
    """Test Python docstring violations match the exact checked-in baseline."""
    violations: list[DocstringViolation] = []
    for file_path in get_python_files(package_root.parent):
        tree = ast.parse(
            file_path.read_text(encoding="utf-8"), filename=file_path.as_posix()
        )
        violations.extend(
            get_docstring_violations(
                file_path=file_path.relative_to(package_root.parent), tree=tree
            )
        )

    violations_by_fingerprint = {
        violation.fingerprint: violation for violation in violations
    }
    actual_fingerprints = set(violations_by_fingerprint)
    expected_fingerprints = set(
        DOCSTRING_BASELINE_PATH.read_text(encoding="utf-8").splitlines()
    )
    unexpected_fingerprints = sorted(actual_fingerprints - expected_fingerprints)
    resolved_fingerprints = sorted(expected_fingerprints - actual_fingerprints)

    failure_sections = []
    if unexpected_fingerprints:
        failure_sections.append(
            "Unexpected docstring violations (fix these, do not add them to the "
            "baseline):\n"
            + "\n".join(
                str(violations_by_fingerprint[fingerprint])
                for fingerprint in unexpected_fingerprints
            )
        )
    if resolved_fingerprints:
        failure_sections.append(
            "Resolved docstring violations (remove these from the baseline):\n"
            + "\n".join(resolved_fingerprints)
        )
    assert not failure_sections, "\n\n".join(failure_sections)
