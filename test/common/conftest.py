#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Configure imports for the portable common tests."""

from __future__ import annotations

import sys
from importlib.util import find_spec
from pathlib import Path

from pytest import UsageError

test_dir_path = Path(__file__).resolve().parent
sys.path.insert(0, str(test_dir_path))

# A conventional checkout places the source and test trees side by side
common_init_paths = list(test_dir_path.parents[1].glob("*/common/__init__.py"))
if len(common_init_paths) == 1:
    sys.path.insert(0, str(common_init_paths[0].parents[1]))
else:
    common_spec = find_spec("common")
    if (
        common_spec is None
        or common_spec.origin is None
        or common_spec.submodule_search_locations is None
    ):
        raise UsageError("Add the directory containing common to PYTHONPATH")
