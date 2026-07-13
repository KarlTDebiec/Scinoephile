#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for extracting subtitle streams from media."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from shutil import copy2

from scinoephile.common.described_enum import DescribedEnum
from scinoephile.common.validation import val_child_path
from scinoephile.core import ScinoephileError
from scinoephile.core.media import SubtitleStream
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.zho.subtitles.streams import get_zho_subtitle_streams
from scinoephile.media.probe import get_subtitle_streams
from scinoephile.media.subtitles.cache import (
    cache_subtitles,
    get_subtitle_cache_path,
)

__all__ = [
    "SubtitleExtractionOutput",
    "SubtitleExtractionOutputKind",
    "SubtitleExtractionOutputStatus",
    "SubtitleExtractionResult",
    "extract_subtitles",
]

logger = getLogger(__name__)


class SubtitleExtractionOutputKind(DescribedEnum):
    """Kind of output produced by subtitle extraction."""

    SUBTITLE = ("subtitle", "subtitle")
    """Extracted or copied subtitle file."""
    IMAGE_SERIES = ("image-series", "image series")
    """Image directory rendered from a SUP subtitle file."""


class SubtitleExtractionOutputStatus(DescribedEnum):
    """Status of an output path handled by subtitle extraction."""

    CREATED = ("created", "Created")
    """Output did not exist and was created."""
    EXISTED = ("existed", "Already existed")
    """Output already existed and was left in place."""
    OVERWRITTEN = ("overwritten", "Overwritten")
    """Output already existed and was regenerated."""


@dataclass(frozen=True)
class SubtitleExtractionOutput:
    """Output path handled by the subtitle extraction workflow."""

    kind: SubtitleExtractionOutputKind
    """Kind of output."""
    status: SubtitleExtractionOutputStatus
    """Status of the output path."""
    stream: SubtitleStream
    """Subtitle stream associated with the output."""
    path: Path
    """Output path."""


@dataclass(frozen=True)
class SubtitleExtractionResult:
    """Result of a subtitle extraction workflow run."""

    infile_path: Path
    """Media input file."""
    outputs: list[SubtitleExtractionOutput]
    """Output paths handled by the workflow."""


def extract_subtitles(
    infile_path: Path,
    languages: Sequence[str],
    output_dir_path: Path,
    *,
    cache_dir_path: Path | None = None,
    details: bool = False,
    export_images: bool = False,
    overwrite: bool = False,
) -> SubtitleExtractionResult:
    """Extract matching subtitle streams from media.

    Arguments:
        infile_path: media input file
        languages: language tags to extract
        output_dir_path: directory to which matching subtitles will be extracted
        cache_dir_path: cache directory path
        details: whether to include expensive stream details
        export_images: whether to export SUP subtitles as image directories
        overwrite: whether to overwrite existing outputs
    Returns:
        subtitle extraction result
    """
    # Ensure the destination directory exists
    if not output_dir_path.exists():
        output_dir_path.mkdir(parents=True)
        logger.info(f"Created subtitle output directory: {output_dir_path}")

    # Handle standalone SUP files separately from containerized media
    if infile_path.suffix.lower() == ".sup":
        outputs = _extract_sup_file(
            infile_path,
            languages,
            output_dir_path,
            details=details,
            export_images=export_images,
            overwrite=overwrite,
            cache_dir_path=cache_dir_path,
        )
        return SubtitleExtractionResult(infile_path=infile_path, outputs=outputs)

    # Select matching subtitle streams from the media container
    requested_language_tags = set(languages)
    streams = [
        stream
        for stream in _get_workflow_subtitle_streams(
            infile_path,
            cache_dir_path=cache_dir_path,
            details=details,
        )
        if _language_matches(stream.language, requested_language_tags)
    ]

    # Determine subtitle file outputs and which streams need cache extraction
    outputs = []
    streams_to_extract = []
    for stream in streams:
        outfile_path = _get_subtitle_output_path(
            output_dir_path,
            stream.outfile_filename,
        )
        status = _get_stream_file_status(outfile_path, overwrite=overwrite)
        outputs.append(
            SubtitleExtractionOutput(
                kind=SubtitleExtractionOutputKind.SUBTITLE,
                status=status,
                stream=stream,
                path=outfile_path,
            )
        )
        if status != SubtitleExtractionOutputStatus.EXISTED:
            streams_to_extract.append(stream)

    # Cache all subtitle files that need extraction in one ffmpeg run
    if streams_to_extract:
        cache_subtitles(
            infile_path,
            streams_to_extract,
            cache_dir_path=cache_dir_path,
            render_images=False,
        )

    # Copy cached subtitle files into place and optionally render SUP image directories
    handled_outputs = []
    for output in outputs:
        if output.status != SubtitleExtractionOutputStatus.EXISTED:
            _copy_cached_stream_file(
                infile_path,
                output.stream,
                output.path,
                cache_dir_path=cache_dir_path,
            )
        handled_outputs.append(output)
        if output.stream.extension == "sup" and export_images:
            image_output = _try_extract_sup_image_series(
                output.stream,
                output.path,
                output.path.with_suffix(""),
                overwrite=overwrite,
            )
            if image_output is not None:
                handled_outputs.append(image_output)
    return SubtitleExtractionResult(infile_path=infile_path, outputs=handled_outputs)


def _copy_cached_stream_file(
    infile_path: Path,
    stream: SubtitleStream,
    outfile_path: Path,
    *,
    cache_dir_path: Path | None,
) -> Path:
    """Copy a cached subtitle stream file into place.

    Arguments:
        infile_path: media input file
        stream: subtitle stream to copy
        outfile_path: output subtitle path
        cache_dir_path: cache directory path
    Returns:
        output subtitle path
    """
    # Resolve the cached subtitle path for the extracted stream
    stream_path = get_subtitle_cache_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )

    # Copy from cache unless the requested output already is the cached file
    if stream_path != outfile_path:
        if not outfile_path.parent.exists():
            outfile_path.parent.mkdir(parents=True)
            logger.info(f"Created subtitle output directory: {outfile_path.parent}")
        copy2(stream_path, outfile_path)
        logger.info(f"Extracted subtitle stream to {outfile_path}")
    return outfile_path


def _get_workflow_subtitle_streams(
    infile_path: Path,
    *,
    cache_dir_path: Path | None,
    details: bool,
) -> list[SubtitleStream]:
    """Get subtitle streams with optional workflow-level detail enrichment.

    Arguments:
        infile_path: media input file
        cache_dir_path: cache directory path
        details: whether to include expensive stream details
    Returns:
        subtitle streams
    """
    # Use downstream Chinese script analysis only when details are requested
    if details:
        return get_zho_subtitle_streams(
            infile_path,
            cache_dir_path=cache_dir_path,
        )
    return get_subtitle_streams(infile_path)


def _language_matches(language: str | None, requested_language_tags: set[str]) -> bool:
    """Return whether a stream language matches requested language tags.

    Arguments:
        language: stream language tag
        requested_language_tags: requested language tags
    Returns:
        whether the language matches exactly or by base language code
    """
    if language is None:
        return False
    if language in requested_language_tags:
        return True
    return language.split("-", 1)[0] in requested_language_tags


def _get_stream_file_status(
    outfile_path: Path,
    *,
    overwrite: bool,
) -> SubtitleExtractionOutputStatus:
    """Get the status to report for a subtitle stream file.

    Arguments:
        outfile_path: output subtitle path
        overwrite: whether to overwrite existing output
    Returns:
        output status
    """
    # Reuse or overwrite existing subtitle files according to caller preference
    if outfile_path.exists():
        if overwrite:
            return SubtitleExtractionOutputStatus.OVERWRITTEN
        return SubtitleExtractionOutputStatus.EXISTED

    # Report missing subtitle files as created
    return SubtitleExtractionOutputStatus.CREATED


def _extract_sup_file(
    infile_path: Path,
    languages: Sequence[str],
    output_dir_path: Path,
    *,
    cache_dir_path: Path | None,
    details: bool,
    export_images: bool,
    overwrite: bool,
) -> list[SubtitleExtractionOutput]:
    """Extract or copy a SUP subtitle input file.

    Arguments:
        infile_path: SUP input file
        languages: language tags to extract
        output_dir_path: output directory
        cache_dir_path: cache directory path
        details: whether to include expensive stream details
        export_images: whether to export SUP subtitles as image directories
        overwrite: whether to overwrite existing outputs
    Returns:
        outputs handled for the SUP file
    """
    # Probe the standalone SUP file and optionally enrich stream details
    streams = _get_workflow_subtitle_streams(
        infile_path,
        cache_dir_path=cache_dir_path,
        details=details,
    )
    if not streams:
        raise ScinoephileError(f"No subtitle streams found in {infile_path}")

    # Determine the output SUP filename from detected stream metadata
    requested_language_tags = set(languages)
    stream = streams[0]
    if stream.language is not None and not _language_matches(
        stream.language,
        requested_language_tags,
    ):
        return []
    outfile_name = infile_path.name
    if stream.language is not None and "-" in stream.language:
        outfile_name = f"{stream.language}{infile_path.suffix}"
    outfile_path = _get_subtitle_output_path(output_dir_path, outfile_name)

    # Copy the SUP file and report its output status
    status = _copy_sup_file(
        infile_path,
        outfile_path,
        overwrite=overwrite,
    )
    outputs = [
        SubtitleExtractionOutput(
            kind=SubtitleExtractionOutputKind.SUBTITLE,
            status=status,
            stream=stream,
            path=outfile_path,
        )
    ]

    # Optionally render the SUP file as an image directory
    if stream.extension == "sup" and export_images:
        outputs.append(
            _extract_sup_image_series(
                stream,
                outfile_path,
                output_dir_path / infile_path.stem,
                overwrite=overwrite,
            )
        )
    return outputs


def _copy_sup_file(
    infile_path: Path,
    outfile_path: Path,
    *,
    overwrite: bool,
) -> SubtitleExtractionOutputStatus:
    """Copy a SUP input file into place and return its output status.

    Arguments:
        infile_path: SUP input file
        outfile_path: output subtitle path
        overwrite: whether to overwrite existing output
    Returns:
        output status
    """
    outfile_is_infile = outfile_path.resolve() == infile_path.resolve()

    # Reuse or overwrite an existing SUP file according to caller preference
    if outfile_path.exists():
        if overwrite and not outfile_is_infile:
            copy2(infile_path, outfile_path)
            return SubtitleExtractionOutputStatus.OVERWRITTEN
        return SubtitleExtractionOutputStatus.EXISTED

    # Copy missing SUP files unless the output is already the input
    if not outfile_is_infile:
        copy2(infile_path, outfile_path)
    return SubtitleExtractionOutputStatus.CREATED


def _get_subtitle_output_path(output_dir_path: Path, outfile_name: str) -> Path:
    """Build a contained subtitle output path.

    Arguments:
        output_dir_path: subtitle output directory
        outfile_name: proposed subtitle output filename
    Returns:
        contained subtitle output path
    Raises:
        ScinoephileError: if the filename could escape the output directory
    """
    try:
        return val_child_path(output_dir_path, outfile_name)
    except ValueError as exc:
        raise ScinoephileError(
            f"Unsafe subtitle output filename from stream metadata: {outfile_name!r}"
        ) from exc


def _extract_sup_image_series(
    stream: SubtitleStream,
    infile_path: Path,
    output_dir_path: Path,
    *,
    overwrite: bool,
) -> SubtitleExtractionOutput:
    """Convert a SUP subtitle file to an image directory.

    Arguments:
        stream: subtitle stream associated with the SUP file
        infile_path: SUP subtitle file
        output_dir_path: output image directory
        overwrite: whether to overwrite existing output
    Returns:
        output handled for the image directory
    """
    # Reuse or overwrite existing image directories according to caller preference
    if output_dir_path.exists():
        if overwrite:
            ImageSeries.load(infile_path).save(output_dir_path)
            status = SubtitleExtractionOutputStatus.OVERWRITTEN
        else:
            status = SubtitleExtractionOutputStatus.EXISTED
    else:
        ImageSeries.load(infile_path).save(output_dir_path)
        status = SubtitleExtractionOutputStatus.CREATED

    return SubtitleExtractionOutput(
        kind=SubtitleExtractionOutputKind.IMAGE_SERIES,
        status=status,
        stream=stream,
        path=output_dir_path,
    )


def _try_extract_sup_image_series(
    stream: SubtitleStream,
    infile_path: Path,
    output_dir_path: Path,
    *,
    overwrite: bool,
) -> SubtitleExtractionOutput | None:
    """Convert a SUP subtitle file to images, warning on parse failures.

    Arguments:
        stream: subtitle stream associated with the SUP file
        infile_path: SUP subtitle file
        output_dir_path: output image directory
        overwrite: whether to overwrite existing output
    Returns:
        output handled for the image directory, if rendering succeeded
    """
    try:
        return _extract_sup_image_series(
            stream,
            infile_path,
            output_dir_path,
            overwrite=overwrite,
        )
    except (OSError, RuntimeError, ScinoephileError, ValueError) as exc:
        logger.warning(
            f"Could not export SUP image series for stream #{stream.index}: {exc}"
        )
        return None
