#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interfaces for cache operations.

Package hierarchy (modules may import from any above):
* output
* cache_clear_cli / cache_list_cli / cache_prune_cli / cache_stats_cli
* cache_cli
"""

from __future__ import annotations

from .cache_cli import CacheCli

__all__ = ["CacheCli"]
