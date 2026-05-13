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
from scinoephile.core import ScinoephileError
from scinoephile.core.media import SubtitleStream
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.zho.subtitles.streams import get_zho_subtitle_streams
from scinoephile.media.probe import get_subtitle_streams
from scinoephile.media.subtitles.extraction import extract_subtitle_stream

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
    extract_sup: bool = False,
    overwrite: bool = False,
) -> SubtitleExtractionResult:
    """Extract matching subtitle streams from media.

    Arguments:
        infile_path: media input file
        languages: ISO 639 language codes to extract
        output_dir_path: directory to which matching subtitles will be extracted
        cache_dir_path: cache directory path
        details: whether to include expensive stream details
        extract_sup: whether to convert extracted SUP subtitles to image directories
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
            output_dir_path,
            details=details,
            extract_sup=extract_sup,
            overwrite=overwrite,
            cache_dir_path=cache_dir_path,
        )
        return SubtitleExtractionResult(infile_path=infile_path, outputs=outputs)

    # Select matching subtitle streams from the media container
    language_codes = set(languages)
    streams = [
        stream
        for stream in _get_workflow_subtitle_streams(
            infile_path,
            cache_dir_path=cache_dir_path,
            details=details,
        )
        if stream.language is not None
        and stream.language.split("-", 1)[0] in language_codes
    ]

    # Extract each selected stream and collect reported outputs
    outputs = []
    for stream in streams:
        outputs.extend(
            _extract_stream(
                infile_path,
                stream,
                output_dir_path,
                extract_sup=extract_sup,
                overwrite=overwrite,
                cache_dir_path=cache_dir_path,
            )
        )
    return SubtitleExtractionResult(infile_path=infile_path, outputs=outputs)


def _extract_stream(
    infile_path: Path,
    stream: SubtitleStream,
    output_dir_path: Path,
    *,
    cache_dir_path: Path | None,
    extract_sup: bool,
    overwrite: bool,
) -> list[SubtitleExtractionOutput]:
    """Extract one matching subtitle stream.

    Arguments:
        infile_path: media input file
        stream: subtitle stream to extract
        output_dir_path: output directory
        cache_dir_path: cache directory path
        extract_sup: whether to convert SUP subtitles to image directories
        overwrite: whether to overwrite existing outputs
    Returns:
        outputs handled for the stream
    """
    outfile_path = output_dir_path / stream.outfile_filename

    # Extract the subtitle file and report its output status
    status = _extract_stream_file(
        infile_path,
        stream,
        outfile_path,
        cache_dir_path=cache_dir_path,
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

    # Optionally render SUP subtitles as image directories
    if stream.extension == "sup" and extract_sup:
        outputs.append(
            _extract_sup_image_series(
                stream,
                outfile_path,
                outfile_path.with_suffix(""),
                overwrite=overwrite,
            )
        )
    return outputs


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


def _extract_stream_file(
    infile_path: Path,
    stream: SubtitleStream,
    outfile_path: Path,
    *,
    cache_dir_path: Path | None,
    overwrite: bool,
) -> SubtitleExtractionOutputStatus:
    """Extract a subtitle stream file and return its output status.

    Arguments:
        infile_path: media input file
        stream: subtitle stream to extract
        outfile_path: output subtitle path
        cache_dir_path: cache directory path
        overwrite: whether to overwrite existing output
    Returns:
        output status
    """
    # Reuse or overwrite existing subtitle files according to caller preference
    if outfile_path.exists():
        if overwrite:
            extract_subtitle_stream(
                infile_path,
                stream,
                outfile_path,
                cache_dir_path=cache_dir_path,
            )
            return SubtitleExtractionOutputStatus.OVERWRITTEN
        return SubtitleExtractionOutputStatus.EXISTED

    # Extract missing subtitle files
    extract_subtitle_stream(
        infile_path,
        stream,
        outfile_path,
        cache_dir_path=cache_dir_path,
    )
    return SubtitleExtractionOutputStatus.CREATED


def _extract_sup_file(
    infile_path: Path,
    output_dir_path: Path,
    *,
    cache_dir_path: Path | None,
    details: bool,
    extract_sup: bool,
    overwrite: bool,
) -> list[SubtitleExtractionOutput]:
    """Extract or copy a SUP subtitle input file.

    Arguments:
        infile_path: SUP input file
        output_dir_path: output directory
        cache_dir_path: cache directory path
        details: whether to include expensive stream details
        extract_sup: whether to convert SUP subtitles to image directories
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
    stream = streams[0]
    outfile_name = infile_path.name
    if stream.language is not None and "-" in stream.language:
        outfile_name = f"{stream.language}{infile_path.suffix}"
    outfile_path = output_dir_path / outfile_name

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
    if stream.extension == "sup" and extract_sup:
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
