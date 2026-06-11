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


def test_extract_subtitles_extracts_matching_streams(tmp_path: Path):
    """Test subtitle extraction workflow exports matching streams.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"
    cache_dir_path = tmp_path / "cache"
    cache_eng_path = cache_dir_path / "eng-2.srt"
    cache_zho_path = cache_dir_path / "zho-4.srt"
    streams = [
        SubtitleStream(index=2, language="eng", codec_name="subrip"),
        SubtitleStream(index=3, language="jpn", codec_name="subrip"),
        SubtitleStream(index=4, language="zho", codec_name="subrip"),
    ]

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=streams,
        ) as get_subtitle_streams,
        patch(
            "scinoephile.workflows.subtitle_extraction.cache_subtitles"
        ) as cache_subtitles,
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_cache_path",
            side_effect=[cache_eng_path, cache_zho_path],
        ),
        patch("scinoephile.workflows.subtitle_extraction.copy2") as copy,
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["eng", "zho"],
            output_dir_path=output_dir_path,
            cache_dir_path=cache_dir_path,
        )

    get_subtitle_streams.assert_called_once_with(infile_path)
    cache_subtitles.assert_called_once_with(
        infile_path,
        [streams[0], streams[2]],
        cache_dir_path=cache_dir_path,
    )
    assert copy.call_args_list[0].args == (
        cache_eng_path,
        output_dir_path / "eng-2.srt",
    )
    assert copy.call_args_list[1].args == (
        cache_zho_path,
        output_dir_path / "zho-4.srt",
    )
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
    cache_path = cache_dir_path / "zho-Hant-4.srt"

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
        patch("scinoephile.workflows.subtitle_extraction.cache_subtitles"),
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_cache_path",
            return_value=cache_path,
        ),
        patch("scinoephile.workflows.subtitle_extraction.copy2"),
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


def test_extract_subtitles_matches_script_qualified_language_tag(tmp_path: Path):
    """Test subtitle extraction matches script-qualified language tags.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"
    cache_dir_path = tmp_path / "cache"
    cache_path = cache_dir_path / "zho-Hant-4.srt"
    stream = SubtitleStream(index=4, language="zho-Hant", codec_name="subrip")

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=[stream],
        ),
        patch("scinoephile.workflows.subtitle_extraction.cache_subtitles"),
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_cache_path",
            return_value=cache_path,
        ),
        patch("scinoephile.workflows.subtitle_extraction.copy2") as copy,
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["zho-Hant"],
            output_dir_path=output_dir_path,
            cache_dir_path=cache_dir_path,
        )

    copy.assert_called_once_with(cache_path, output_dir_path / "zho-Hant-4.srt")
    assert result.outputs[0].stream is stream


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
            "scinoephile.workflows.subtitle_extraction.cache_subtitles"
        ) as cache_subtitles,
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["eng"],
            output_dir_path=output_dir_path,
        )

    cache_subtitles.assert_not_called()
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
    cache_path = tmp_path / "cache" / "eng-2.srt"
    stream = SubtitleStream(index=2, language="eng", codec_name="subrip")

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=[stream],
        ),
        patch(
            "scinoephile.workflows.subtitle_extraction.cache_subtitles"
        ) as cache_subtitles,
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_cache_path",
            return_value=cache_path,
        ),
        patch("scinoephile.workflows.subtitle_extraction.copy2") as copy,
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["eng"],
            output_dir_path=output_dir_path,
            overwrite=True,
        )

    cache_subtitles.assert_called_once_with(
        infile_path,
        [stream],
        cache_dir_path=None,
    )
    copy.assert_called_once_with(cache_path, outfile_path)
    assert result.outputs[0].status == SubtitleExtractionOutputStatus.OVERWRITTEN


def test_extract_subtitles_extracts_sup_streams_to_image_dirs(tmp_path: Path):
    """Test subtitle extraction workflow converts SUP streams to image directories.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"
    cache_dir_path = tmp_path / "cache"
    cache_eng_path = cache_dir_path / "eng-2.srt"
    cache_zho_path = cache_dir_path / "zho-3.sup"
    image_series = Mock()
    streams = [
        SubtitleStream(index=2, language="eng", codec_name="subrip"),
        SubtitleStream(index=3, language="zho", codec_name="hdmv_pgs_subtitle"),
    ]

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=streams,
        ),
        patch(
            "scinoephile.workflows.subtitle_extraction.cache_subtitles"
        ) as cache_subtitles,
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_cache_path",
            side_effect=[cache_eng_path, cache_zho_path],
        ),
        patch("scinoephile.workflows.subtitle_extraction.copy2"),
        patch(
            "scinoephile.workflows.subtitle_extraction.ImageSeries.load",
            return_value=image_series,
        ) as load,
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["eng", "zho"],
            output_dir_path=output_dir_path,
            cache_dir_path=cache_dir_path,
            export_images=True,
        )

    cache_subtitles.assert_called_once_with(
        infile_path,
        streams,
        cache_dir_path=cache_dir_path,
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
            export_images=True,
            overwrite=True,
        )

    copy.assert_not_called()
    load.assert_called_once_with(infile_path)
    image_series.save.assert_called_once_with(tmp_path / "source")
    assert [output.status for output in result.outputs] == [
        SubtitleExtractionOutputStatus.EXISTED,
        SubtitleExtractionOutputStatus.CREATED,
    ]


def test_extract_subtitles_skips_sup_file_with_nonmatching_language(tmp_path: Path):
    """Test subtitle extraction workflow skips SUP inputs with nonmatching language.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "source.sup"
    infile_path.touch()

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=[
                SubtitleStream(
                    index=0,
                    language="eng",
                    codec_name="hdmv_pgs_subtitle",
                ),
            ],
        ),
        patch("scinoephile.workflows.subtitle_extraction.copy2") as copy,
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["zho"],
            output_dir_path=tmp_path,
            export_images=True,
        )

    copy.assert_not_called()
    assert result.outputs == []


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
