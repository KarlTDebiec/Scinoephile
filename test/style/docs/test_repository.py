#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

"""Repository-wide docstring structure enforcement."""

from __future__ import annotations

import ast

from scinoephile.common import package_root
from test.helpers.files import get_python_files
from test.style.docs.checks import DocstringViolation, get_docstring_violations


def test_python_docstrings_follow_repository_structure():
    """Test Python docstrings satisfy every repository structure rule."""
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

    assert not violations, "Fix docstring violations:\n" + "\n".join(
        str(violation) for violation in violations
    )
