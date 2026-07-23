#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of subtitle extraction workflows."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from PIL import Image
from pytest import LogCaptureFixture, raises

from scinoephile.core import ScinoephileError
from scinoephile.core.media import SubtitleStream
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle
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
    cache_eng_path.parent.mkdir()
    cache_eng_path.write_text("english", encoding="utf-8")
    cache_zho_path.write_text("chinese", encoding="utf-8")
    streams = [
        SubtitleStream(index=2, language="eng", codec_name="subrip"),
        SubtitleStream(index=3, language="jpn", codec_name="subrip"),
        SubtitleStream(index=4, language="zho", codec_name="subrip"),
    ]

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=streams,
        ),
        patch("scinoephile.workflows.subtitle_extraction.cache_subtitles"),
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_cache_path",
            side_effect=[cache_eng_path, cache_zho_path],
        ),
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["eng", "zho"],
            output_dir_path=output_dir_path,
            cache_dir_path=cache_dir_path,
        )

    assert [output.path for output in result.outputs] == [
        output_dir_path / "eng-2.srt",
        output_dir_path / "zho-4.srt",
    ]
    assert (output_dir_path / "eng-2.srt").read_text(encoding="utf-8") == "english"
    assert (output_dir_path / "zho-4.srt").read_text(encoding="utf-8") == "chinese"
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
    cache_path.parent.mkdir()
    cache_path.write_text("traditional", encoding="utf-8")

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=[
                SubtitleStream(index=4, language="zho", codec_name="subrip"),
            ],
        ),
        patch(
            "scinoephile.workflows.subtitle_extraction.get_zho_subtitle_streams",
            return_value=[
                SubtitleStream(index=4, language="zho-Hant", codec_name="subrip"),
            ],
        ),
        patch("scinoephile.workflows.subtitle_extraction.cache_subtitles"),
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_cache_path",
            return_value=cache_path,
        ),
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["zho"],
            output_dir_path=output_dir_path,
            details=True,
            cache_dir_path=cache_dir_path,
        )

    assert result.outputs[0].path == output_dir_path / "zho-Hant-4.srt"
    assert result.outputs[0].path.read_text(encoding="utf-8") == "traditional"


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
    cache_path.parent.mkdir()
    cache_path.write_text("traditional", encoding="utf-8")
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
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["zho-Hant"],
            output_dir_path=output_dir_path,
            cache_dir_path=cache_dir_path,
        )

    assert result.outputs[0].path == output_dir_path / "zho-Hant-4.srt"
    assert result.outputs[0].path.read_text(encoding="utf-8") == "traditional"
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
    cache_path.parent.mkdir()
    cache_path.write_text("replacement", encoding="utf-8")
    stream = SubtitleStream(index=2, language="eng", codec_name="subrip")

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
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["eng"],
            output_dir_path=output_dir_path,
            overwrite=True,
        )

    assert result.outputs[0].path == outfile_path
    assert result.outputs[0].status == SubtitleExtractionOutputStatus.OVERWRITTEN
    assert outfile_path.read_text(encoding="utf-8") == "replacement"


def test_extract_subtitles_rejects_unsafe_stream_language(tmp_path: Path):
    """Test stream metadata cannot escape the subtitle output directory.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=[
                SubtitleStream(
                    index=2,
                    language="eng-../../../escaped",
                    codec_name="subrip",
                ),
            ],
        ),
        patch(
            "scinoephile.workflows.subtitle_extraction.cache_subtitles"
        ) as cache_subtitles,
        raises(ScinoephileError, match="Unsafe subtitle output filename"),
    ):
        extract_subtitles(
            infile_path=infile_path,
            languages=["eng"],
            output_dir_path=output_dir_path,
        )

    cache_subtitles.assert_not_called()
    assert not (tmp_path / "escaped-2.srt").exists()


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
    cache_eng_path.parent.mkdir()
    cache_eng_path.write_text("english", encoding="utf-8")
    cache_zho_path.write_bytes(b"sup")
    image_series = _image_series()
    streams = [
        SubtitleStream(index=2, language="eng", codec_name="subrip"),
        SubtitleStream(index=3, language="zho", codec_name="hdmv_pgs_subtitle"),
    ]

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=streams,
        ),
        patch("scinoephile.workflows.subtitle_extraction.cache_subtitles"),
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_cache_path",
            side_effect=[cache_eng_path, cache_zho_path],
        ),
        patch(
            "scinoephile.workflows.subtitle_extraction.ImageSeries.load",
            return_value=image_series,
        ),
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["eng", "zho"],
            output_dir_path=output_dir_path,
            cache_dir_path=cache_dir_path,
            export_images=True,
        )

    assert [output.kind for output in result.outputs] == [
        SubtitleExtractionOutputKind.SUBTITLE,
        SubtitleExtractionOutputKind.SUBTITLE,
        SubtitleExtractionOutputKind.IMAGE_SERIES,
    ]
    assert result.outputs[-1].path == output_dir_path / "zho-3"
    assert result.outputs[-1].status == SubtitleExtractionOutputStatus.CREATED
    assert (output_dir_path / "zho-3" / "index.html").exists()


def test_extract_subtitles_skips_sup_parsing_when_not_exporting_images(tmp_path: Path):
    """Test extraction skips SUP image parsing when image export is disabled.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"
    cache_dir_path = tmp_path / "cache"
    cache_srt_path = cache_dir_path / "eng-8.srt"
    cache_sup_path = cache_dir_path / "eng-10.sup"
    cache_srt_path.parent.mkdir()
    cache_srt_path.write_text("english", encoding="utf-8")
    cache_sup_path.write_bytes(b"sup")
    streams = [
        SubtitleStream(index=8, language="eng", codec_name="subrip"),
        SubtitleStream(index=10, language="eng", codec_name="hdmv_pgs_subtitle"),
    ]

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=streams,
        ),
        patch("scinoephile.workflows.subtitle_extraction.cache_subtitles"),
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_cache_path",
            side_effect=[cache_srt_path, cache_sup_path],
        ),
        patch(
            "scinoephile.workflows.subtitle_extraction.ImageSeries.load",
            side_effect=ValueError("SUP segment data is truncated."),
        ) as load,
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["eng"],
            output_dir_path=output_dir_path,
            cache_dir_path=cache_dir_path,
        )

    load.assert_not_called()
    assert [output.path for output in result.outputs] == [
        output_dir_path / "eng-8.srt",
        output_dir_path / "eng-10.sup",
    ]
    assert (output_dir_path / "eng-8.srt").read_text(encoding="utf-8") == "english"
    assert (output_dir_path / "eng-10.sup").read_bytes() == b"sup"


def test_extract_subtitles_warns_when_sup_image_export_fails(
    tmp_path: Path,
    caplog: LogCaptureFixture,
):
    """Test extraction keeps subtitle files when SUP image export fails.

    Arguments:
        tmp_path: temporary directory provided by pytest
        caplog: pytest log capture fixture
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"
    cache_dir_path = tmp_path / "cache"
    cache_srt_path = cache_dir_path / "eng-8.srt"
    cache_sup_path = cache_dir_path / "eng-10.sup"
    cache_srt_path.parent.mkdir()
    cache_srt_path.write_text("english", encoding="utf-8")
    cache_sup_path.write_bytes(b"sup")
    streams = [
        SubtitleStream(index=8, language="eng", codec_name="subrip"),
        SubtitleStream(index=10, language="eng", codec_name="hdmv_pgs_subtitle"),
    ]

    caplog.set_level(
        "WARNING",
        logger="scinoephile.workflows.subtitle_extraction",
    )
    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=streams,
        ),
        patch("scinoephile.workflows.subtitle_extraction.cache_subtitles"),
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_cache_path",
            side_effect=[cache_srt_path, cache_sup_path],
        ),
        patch(
            "scinoephile.workflows.subtitle_extraction.ImageSeries.load",
            side_effect=ScinoephileError(
                "Unable to load ImageSeries from eng-10.sup: "
                "SUP segment data is truncated."
            ),
        ),
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["eng"],
            output_dir_path=output_dir_path,
            cache_dir_path=cache_dir_path,
            export_images=True,
        )

    assert [output.path for output in result.outputs] == [
        output_dir_path / "eng-8.srt",
        output_dir_path / "eng-10.sup",
    ]
    assert (output_dir_path / "eng-8.srt").read_text(encoding="utf-8") == "english"
    assert (output_dir_path / "eng-10.sup").read_bytes() == b"sup"
    assert "Could not export SUP image series for stream #10" in caplog.text


def test_extract_subtitles_extracts_sup_file_to_image_dir_in_place(tmp_path: Path):
    """Test subtitle extraction workflow converts SUP input files in place.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "source.sup"
    infile_path.touch()
    image_series = _image_series()

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.ImageSeries.load",
            return_value=image_series,
        ),
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

    assert (tmp_path / "source" / "index.html").exists()
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
    ):
        result = extract_subtitles(
            infile_path=infile_path,
            languages=["zho"],
            output_dir_path=tmp_path,
            export_images=True,
        )

    assert result.outputs == []


def test_extract_subtitles_rejects_unsafe_sup_language(tmp_path: Path):
    """Test SUP stream metadata cannot escape the subtitle output directory.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "source.sup"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"

    with (
        patch(
            "scinoephile.workflows.subtitle_extraction.get_subtitle_streams",
            return_value=[
                SubtitleStream(
                    index=0,
                    language="eng-../../../escaped",
                    codec_name="hdmv_pgs_subtitle",
                ),
            ],
        ),
        raises(ScinoephileError, match="Unsafe subtitle output filename"),
    ):
        extract_subtitles(
            infile_path=infile_path,
            languages=["eng"],
            output_dir_path=output_dir_path,
        )

    assert not (tmp_path / "escaped.sup").exists()


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
        raises(ScinoephileError, match="No subtitle streams found"),
    ):
        extract_subtitles(
            infile_path=infile_path,
            languages=["zho"],
            output_dir_path=tmp_path,
        )


def _image_series() -> ImageSeries:
    """Build a small image subtitle series for SUP export tests.

    Returns:
        image subtitle series
    """
    return ImageSeries(
        events=[
            ImageSubtitle(
                start=1000,
                end=2000,
                img=Image.new("RGBA", (10, 8), (255, 255, 255, 0)),
            )
        ]
    )
