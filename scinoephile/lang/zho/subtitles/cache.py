#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Chinese subtitle script analysis cache."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from logging import getLogger
from pathlib import Path
from typing import cast

from scinoephile.common.file import open_atomic_text_file
from scinoephile.core.cache.namespace import get_cache_namespace_dir_path
from scinoephile.core.media import SubtitleStream

from .analysis_result import ZhoSubtitleScriptAnalysis

__all__ = ["ZhoSubtitleScriptAnalysisCache"]

logger = getLogger(__name__)


class ZhoSubtitleScriptAnalysisCache:
    """Caches Chinese subtitle script analysis results."""

    def __init__(self, cache_root_path: Path, overwrite: bool = False):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache
            overwrite: whether to replace matching cache files
        """
        self.cache_dir_path = get_cache_namespace_dir_path(
            cache_root_path,
            "media",
            "subtitle-analysis",
        )
        """Directory in which cached script analyses are stored."""

        self.overwrite = overwrite
        """Whether matching cache files should be replaced."""

    def get_path(
        self,
        infile_path: Path,
        stream: SubtitleStream,
        sample_size: int,
        ocr_languages: Sequence[str],
    ) -> Path:
        """Get a script analysis cache path.

        Arguments:
            infile_path: media input file
            stream: subtitle stream
            sample_size: OCR sample size
            ocr_languages: OCR language codes
        Returns:
            script analysis cache path
        """
        resolved_path = infile_path.resolve()
        stat = resolved_path.stat()
        payload = {
            "path": str(resolved_path),
            "size": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
            "stream_index": stream.index,
            "codec_name": stream.codec_name,
            "sample_size": sample_size,
            "ocr_languages": tuple(ocr_languages),
        }
        encoded_payload = json.dumps(payload, sort_keys=True).encode("utf-8")
        cache_key = hashlib.sha256(encoded_payload).hexdigest()
        return self.cache_dir_path / f"{cache_key}.json"

    def load(
        self,
        infile_path: Path,
        stream: SubtitleStream,
        sample_size: int,
        ocr_languages: Sequence[str],
    ) -> ZhoSubtitleScriptAnalysis | None:
        """Load a cached script analysis.

        Invalid cache files are discarded and treated as cache misses.

        Arguments:
            infile_path: media input file
            stream: subtitle stream
            sample_size: OCR sample size
            ocr_languages: OCR language codes
        Returns:
            cached script analysis, if present and valid
        """
        cache_path = self.get_path(
            infile_path,
            stream,
            sample_size,
            ocr_languages,
        )
        if self.overwrite and cache_path.exists():
            cache_path.unlink()
            logger.info(f"Removed subtitle script analysis cache: {cache_path}")
        if not cache_path.exists():
            return None

        # Validate the matching entry, discarding invalid data as a cache miss
        try:
            with cache_path.open("r", encoding="utf-8") as file:
                payload: object = json.load(file)
            analysis = self._deserialize(payload)
        except (OSError, TypeError, UnicodeError, ValueError) as exc:
            cache_path.unlink(missing_ok=True)
            logger.warning(
                f"Discarded invalid subtitle script analysis cache {cache_path}: {exc}"
            )
            return None

        cache_path.touch()
        logger.info(f"Loaded subtitle script analysis from cache: {cache_path}")
        return analysis

    def save(
        self,
        infile_path: Path,
        stream: SubtitleStream,
        sample_size: int,
        ocr_languages: Sequence[str],
        analysis: ZhoSubtitleScriptAnalysis,
    ) -> Path:
        """Save a script analysis to the cache.

        Arguments:
            infile_path: media input file
            stream: subtitle stream
            sample_size: OCR sample size
            ocr_languages: OCR language codes
            analysis: script analysis to cache
        Returns:
            saved cache path
        """
        cache_path = self.get_path(
            infile_path,
            stream,
            sample_size,
            ocr_languages,
        )
        with open_atomic_text_file(cache_path) as file:
            json.dump(asdict(analysis), file, ensure_ascii=False, sort_keys=True)
        logger.info(f"Saved subtitle script analysis to cache: {cache_path}")
        return cache_path

    @staticmethod
    def _deserialize(payload: object) -> ZhoSubtitleScriptAnalysis:
        """Deserialize and validate a cached script analysis.

        Arguments:
            payload: decoded JSON payload
        Returns:
            validated script analysis
        """
        if not isinstance(payload, Mapping):
            raise ValueError("Subtitle script analysis cache must contain an object")
        values = cast(Mapping[str, object], payload)

        # Validate optional textual fields
        script = values.get("script")
        failure_reason = values.get("failure_reason")
        if script is not None and not isinstance(script, str):
            raise ValueError("Subtitle script analysis script must be a string or null")
        if failure_reason is not None and not isinstance(failure_reason, str):
            raise ValueError(
                "Subtitle script analysis failure reason must be a string or null"
            )

        # Validate required count fields
        counts = [
            values.get("simplified_count"),
            values.get("traditional_count"),
            values.get("shared_count"),
        ]
        if any(
            not isinstance(count, int) or isinstance(count, bool) for count in counts
        ):
            raise ValueError("Subtitle script analysis counts must be integers")

        # Validate collection fields before narrowing their types
        sample_indexes = values.get("sample_indexes")
        ocr_languages = values.get("ocr_languages")
        if not isinstance(sample_indexes, list) or any(
            not isinstance(index, int) or isinstance(index, bool)
            for index in sample_indexes
        ):
            raise ValueError("Subtitle script analysis sample indexes must be integers")
        if not isinstance(ocr_languages, list) or any(
            not isinstance(language, str) for language in ocr_languages
        ):
            raise ValueError("Subtitle script analysis OCR languages must be strings")

        simplified_count, traditional_count, shared_count = cast(list[int], counts)
        validated_sample_indexes = cast(list[int], sample_indexes)
        validated_ocr_languages = cast(list[str], ocr_languages)
        return ZhoSubtitleScriptAnalysis(
            script=script,
            simplified_count=simplified_count,
            traditional_count=traditional_count,
            shared_count=shared_count,
            sample_indexes=tuple(validated_sample_indexes),
            ocr_languages=tuple(validated_ocr_languages),
            failure_reason=failure_reason,
        )
