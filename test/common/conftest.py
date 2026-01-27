#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Configuration of tests of scinoephile.common."""

from __future__ import annotations

import sys

from scinoephile.common import package_root

# Enables tests of common module to import from this package's instance of common
sys.path.insert(0, str(package_root))
