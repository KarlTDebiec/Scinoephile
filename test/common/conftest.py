#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Configuration for common module tests."""

from __future__ import annotations

import sys
from pathlib import Path

# Add the parent package directory to sys.path to allow importing 'common'
# This assumes the structure: <package>/{common/, test/common/}
# When copying to other projects, ensure the parent directory containing
# 'common' is added to sys.path
project_root = Path(__file__).parent.parent.parent
package_dir = project_root / "scinoephile"
sys.path.insert(0, str(package_dir))
