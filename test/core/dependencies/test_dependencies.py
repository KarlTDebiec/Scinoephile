#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of centralized optional dependency access."""

from __future__ import annotations

from scinoephile.core.dependencies import ocr, web


def test_dependency_exports_use_lazy_import_naming():
    """Test dependency helpers use the public lazy-import naming convention."""
    for module in (ocr, web):
        assert all(name.startswith("import_") for name in module.__all__)
