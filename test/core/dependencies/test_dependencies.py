#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of centralized optional dependency access."""

from __future__ import annotations

from importlib import import_module
from pkgutil import iter_modules

from scinoephile.core import dependencies


def test_dependency_exports_use_lazy_import_naming():
    """Test dependency helpers use the public lazy-import naming convention."""
    module_names = sorted(
        module_info.name
        for module_info in iter_modules(
            dependencies.__path__, f"{dependencies.__name__}."
        )
        if not module_info.name.rsplit(".", 1)[-1].startswith("_")
    )

    assert module_names
    for module_name in module_names:
        module = import_module(module_name)
        exports = getattr(module, "__all__", None)
        assert isinstance(exports, list)
        assert all(name.startswith("import_") for name in exports)
