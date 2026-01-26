#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Configuration for common module tests."""

from __future__ import annotations

import sys
from pathlib import Path

# Add the parent package directory to sys.path to allow importing 'common'
# This assumes the structure: <package>/{common/, test/common/}
# When copying to other projects, ensure test/common/ is at the same level
# relative to the common module as it is here
test_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(test_dir))

# Try to import from the expected location
try:
    import common  # noqa: F401
except ModuleNotFoundError:
    # If that fails, try adding the parent of common to the path
    # This handles cases where common is in a subdirectory like project/common
    common_parent = test_dir / "scinoephile"
    if common_parent.exists():
        sys.path.insert(0, str(common_parent))
