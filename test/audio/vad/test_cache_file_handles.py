#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""File ownership regressions for malformed voice activity cache archives."""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, NoReturn
from unittest.mock import patch
from zipfile import BadZipFile

from pydub import AudioSegment

from scinoephile.audio.vad import VoiceActivityCache
from scinoephile.core.cache.artifact import remove_cache_artifact
from scinoephile.core.cache.identity import CacheIdentity


def test_vad_cache_closes_input_before_discarding_a_failed_archive(tmp_path: Path):
    """Close the cache file even when NumPy fails before returning its context manager.

    Arguments:
        tmp_path: temporary cache root
    """
    cache = VoiceActivityCache(tmp_path)
    audio = AudioSegment.silent(duration=100, frame_rate=16000)
    cache_identity: CacheIdentity = {"model": "test"}
    cache_path = cache.get_path(audio, cache_identity)
    cache_path.write_bytes(b"PK\x03\x04not a zip")
    opened_files: list[BinaryIO] = []

    def fail_archive_open(cache_file: BinaryIO, *, allow_pickle: bool) -> NoReturn:
        """Retain the input handle and fail before yielding an archive object.

        Arguments:
            cache_file: caller-owned binary input
            allow_pickle: NumPy pickle-loading policy
        Raises:
            BadZipFile: to simulate failure while constructing the archive
        """
        assert not allow_pickle
        assert not cache_file.closed
        opened_files.append(cache_file)
        raise BadZipFile("failed while opening archive")

    def discard_closed_file(artifact_path: Path) -> bool:
        """Check file ownership before executing the real invalid-entry removal.

        Arguments:
            artifact_path: malformed cache file to discard
        Returns:
            whether the artifact was removed
        """
        assert len(opened_files) == 1
        assert opened_files[0].closed
        return remove_cache_artifact(artifact_path)

    with (
        patch("scinoephile.audio.vad.cache.np.load", side_effect=fail_archive_open),
        patch(
            "scinoephile.audio.vad.cache.remove_cache_artifact",
            side_effect=discard_closed_file,
        ),
    ):
        assert cache.load(audio, cache_identity) is None

    assert opened_files[0].closed
    assert not cache_path.exists()
