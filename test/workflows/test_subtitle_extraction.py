#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of subtitle extraction workflows."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from scinoephile.core import ScinoephileError
from scinoephile.core.media import SubtitleStream
from scinoephile.workflows.subtitle_extraction import (
    SubtitleExtractionOutputKind,
    SubtitleExtractionOutputStatus,
    extract_subtitles,
)


def test_subtitle_extraction_output_kind_metadata():
    """Test subtitle extraction output kind enum metadata."""
    assert SubtitleExtractionOutputKind.SUBTITLE.code == "subtitle"
    assert SubtitleExtractionOutputKind.SUBTITLE.value == "subtitle"
    assert SubtitleExtractionOutputKind.SUBTITLE.description == "subtitle"
    assert str(SubtitleExtractionOutputKind.SUBTITLE) == "subtitle"
    assert SubtitleExtractionOutputKind.IMAGE_SERIES.code == "image-series"
    assert SubtitleExtractionOutputKind.IMAGE_SERIES.description == "image series"


def test_subtitle_extraction_output_status_metadata():
    """Test subtitle extraction output status enum metadata."""
    assert SubtitleExtractionOutputStatus.CREATED.code == "created"
    assert SubtitleExtractionOutputStatus.CREATED.value == "created"
    assert SubtitleExtractionOutputStatus.CREATED.description == "Created"
    assert str(SubtitleExtractionOutputStatus.CREATED) == "created"
    assert SubtitleExtractionOutputStatus.EXISTED.description == "Already existed"
    assert SubtitleExtractionOutputStatus.OVERWRITTEN.description == "Overwritten"


def test_extract_subtitles_extracts_matching_streams(tmp_path: Path):
    """Test subtitle extraction workflow exports matching streams.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"
    cache_dir_path = tmp_path / "cache"

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=[
                SubtitleStream(index=2, language="eng", codec_name="subrip"),
                SubtitleStream(index=3, language="jpn", codec_name="subrip"),
                SubtitleStream(index=4, language="zho", codec_name="subrip"),
            ],
        ) as get_subtitle_streams,
        patch(
            "scinoephile.workflows.subtitle_extraction.extract_subtitle_stream"
        ) as extract,
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["eng", "zho"],
            output_dir_path=output_dir_path,
            cache_dir_path=cache_dir_path,
        )

    get_subtitle_streams.assert_called_once_with(infile_path)
    assert extract.call_count == 2
    assert [output.path for output in result.outputs] == [
        output_dir_path / "eng-2.srt",
        output_dir_path / "zho-4.srt",
    ]
    assert [output.status for output in result.outputs] == [
        SubtitleExtractionOutputStatus.CREATED,
        SubtitleExtractionOutputStatus.CREATED,
    ]
    assert all(
        output.kind == SubtitleExtractionOutputKind.SUBTITLE
        for output in result.outputs
    )


def test_extract_subtitles_details_uses_detected_chinese_script(tmp_path: Path):
    """Test details mode uses detected Chinese script in filenames.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"
    cache_dir_path = tmp_path / "cache"

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=[
                SubtitleStream(index=4, language="zho", codec_name="subrip"),
            ],
        ) as get_subtitle_streams,
        patch(
            "scinoephile.workflows.subtitle_extraction.get_zho_subtitle_streams",
            return_value=[
                SubtitleStream(index=4, language="zho-Hant", codec_name="subrip"),
            ],
        ) as get_zho_subtitle_streams,
        patch("scinoephile.workflows.subtitle_extraction.extract_subtitle_stream"),
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["zho"],
            output_dir_path=output_dir_path,
            details=True,
            cache_dir_path=cache_dir_path,
        )

    get_subtitle_streams.assert_not_called()
    get_zho_subtitle_streams.assert_called_once_with(
        infile_path,
        cache_dir_path=cache_dir_path,
    )
    assert result.outputs[0].path == output_dir_path / "zho-Hant-4.srt"


def test_extract_subtitles_reports_existing_outputs(tmp_path: Path):
    """Test subtitle extraction workflow reports existing files.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"
    output_dir_path.mkdir()
    outfile_path = output_dir_path / "eng-2.srt"
    outfile_path.touch()

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=[
                SubtitleStream(index=2, language="eng", codec_name="subrip"),
            ],
        ),
        patch(
            "scinoephile.workflows.subtitle_extraction.extract_subtitle_stream"
        ) as extract,
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["eng"],
            output_dir_path=output_dir_path,
        )

    extract.assert_not_called()
    assert result.outputs[0].path == outfile_path
    assert result.outputs[0].status == SubtitleExtractionOutputStatus.EXISTED


def test_extract_subtitles_reports_overwritten_outputs(tmp_path: Path):
    """Test subtitle extraction workflow reports overwritten files.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"
    output_dir_path.mkdir()
    outfile_path = output_dir_path / "eng-2.srt"
    outfile_path.touch()

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=[
                SubtitleStream(index=2, language="eng", codec_name="subrip"),
            ],
        ),
        patch(
            "scinoephile.workflows.subtitle_extraction.extract_subtitle_stream"
        ) as extract,
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["eng"],
            output_dir_path=output_dir_path,
            overwrite=True,
        )

    extract.assert_called_once()
    assert extract.call_args.args[2] == outfile_path
    assert result.outputs[0].status == SubtitleExtractionOutputStatus.OVERWRITTEN


def test_extract_subtitles_extracts_sup_streams_to_image_dirs(tmp_path: Path):
    """Test subtitle extraction workflow converts SUP streams to image directories.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"
    image_series = Mock()

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=[
                SubtitleStream(index=2, language="eng", codec_name="subrip"),
                SubtitleStream(index=3, language="zho", codec_name="hdmv_pgs_subtitle"),
            ],
        ),
        patch("scinoephile.workflows.subtitle_extraction.extract_subtitle_stream"),
        patch(
            "scinoephile.workflows.subtitle_extraction.ImageSeries.load",
            return_value=image_series,
        ) as load,
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["eng", "zho"],
            output_dir_path=output_dir_path,
            extract_sup=True,
        )

    assert [output.kind for output in result.outputs] == [
        SubtitleExtractionOutputKind.SUBTITLE,
        SubtitleExtractionOutputKind.SUBTITLE,
        SubtitleExtractionOutputKind.IMAGE_SERIES,
    ]
    assert result.outputs[-1].path == output_dir_path / "zho-3"
    assert result.outputs[-1].status == SubtitleExtractionOutputStatus.CREATED
    load.assert_called_once_with(output_dir_path / "zho-3.sup")
    image_series.save.assert_called_once_with(output_dir_path / "zho-3")


def test_extract_subtitles_extracts_sup_file_to_image_dir_in_place(tmp_path: Path):
    """Test subtitle extraction workflow converts SUP input files in place.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "source.sup"
    infile_path.touch()
    image_series = Mock()

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.ImageSeries.load",
            return_value=image_series,
        ) as load,
        patch("scinoephile.workflows.subtitle_extraction.copy2") as copy,
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=[
                SubtitleStream(
                    index=0,
                    language=None,
                    codec_name="hdmv_pgs_subtitle",
                ),
            ],
        ),
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["zho"],
            output_dir_path=tmp_path,
            extract_sup=True,
            overwrite=True,
        )

    copy.assert_not_called()
    load.assert_called_once_with(infile_path)
    image_series.save.assert_called_once_with(tmp_path / "source")
    assert [output.status for output in result.outputs] == [
        SubtitleExtractionOutputStatus.EXISTED,
        SubtitleExtractionOutputStatus.CREATED,
    ]


def test_extract_subtitles_rejects_sup_file_without_subtitle_streams(tmp_path: Path):
    """Test subtitle extraction workflow rejects SUP files without subtitle streams.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "source.sup"
    infile_path.touch()

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=[],
        ),
        pytest.raises(ScinoephileError, match="No subtitle streams found"),
    ):
        extract_subtitles(
            infile_path=infile_path,
            languages=["zho"],
            output_dir_path=tmp_path,
        )
