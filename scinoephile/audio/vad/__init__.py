#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Voice activity detection for audio processing.

Package hierarchy (modules may import from any above):
* exceptions / identity / trace
* cache / intervals / provider
* pyannote / silero / speech_block / ten
* detector
"""

from __future__ import annotations

from .cache import VoiceActivityCache
from .detector import VadImplementation, VoiceActivityDetector
from .exceptions import VoiceActivityError
from .speech_block import SpeechBlock, SpeechBlockSettings, SpeechBlockSplitter
from .trace import VoiceActivityTrace

__all__ = [
    "SpeechBlock",
    "SpeechBlockSettings",
    "SpeechBlockSplitter",
    "VadImplementation",
    "VoiceActivityCache",
    "VoiceActivityDetector",
    "VoiceActivityError",
    "VoiceActivityTrace",
]
