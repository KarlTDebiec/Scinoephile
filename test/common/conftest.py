#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Configuration for common module tests."""

from __future__ import annotations

import sys
from pathlib import Path

# Add the scinoephile package directory to sys.path
# This allows importing 'common' module when tests are in test/common/
# When common module is copied to other projects, adjust this path accordingly
package_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(package_root / "scinoephile"))
