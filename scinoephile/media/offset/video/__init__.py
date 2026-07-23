#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Video offset detection from sampled frame comparisons.

Package hierarchy (modules may import from any above):
* video_frame_sample / video_metadata / video_offset_aggregate / video_offset_candidate
* video_offset_window_result
* video_offset_result
* detection
"""

from __future__ import annotations

from .video_offset_result import VideoOffsetResult

__all__ = ["VideoOffsetResult"]
