#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.media.MediaExtractSubsCli."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import ANY, Mock, patch

import pytest

from scinoephile.cli.media.media_cli import MediaCli
from scinoephile.cli.media.media_extract_subs_cli import MediaExtractSubsCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.media import SubtitleStream
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (MediaExtractSubsCli,),
        (MediaCli, MediaExtractSubsCli),
        (ScinoephileCli, MediaCli, MediaExtractSubsCli),
    ],
)
def test_media_extract_subs_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test media extract_subs CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (MediaExtractSubsCli,),
        (MediaCli, MediaExtractSubsCli),
        (ScinoephileCli, MediaCli, MediaExtractSubsCli),
    ],
)
def test_media_extract_subs_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test media extract_subs CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


def test_media_extract_subs_cli(tmp_path: Path):
    """Test media extract_subs CLI exports matching streams."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"

    with (
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.get_subtitle_streams",
            return_value=[
                SubtitleStream(index=2, language="eng", codec_name="subrip"),
                SubtitleStream(index=3, language="jpn", codec_name="subrip"),
                SubtitleStream(index=4, language="zho", codec_name="subrip"),
            ],
        ) as get_subtitle_streams,
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.extract_subtitle_stream"
        ) as extract,
        patch("scinoephile.cli.media.media_extract_subs_cli.cache_subtitle_streams"),
    ):
        run_cli_with_args(
            MediaExtractSubsCli,
            f"--infile {infile_path} --languages eng zho -o {output_dir_path}",
        )

    get_subtitle_streams.assert_called_once_with(
        infile_path.resolve(),
    )
    assert extract.call_count == 2
    assert extract.call_args_list[0].args[0] == infile_path.resolve()
    assert extract.call_args_list[0].args[1].index == 2
    assert extract.call_args_list[0].args[2] == output_dir_path.resolve() / "eng-2.srt"
    assert extract.call_args_list[1].args[0] == infile_path.resolve()
    assert extract.call_args_list[1].args[1].index == 4
    assert extract.call_args_list[1].args[2] == output_dir_path.resolve() / "zho-4.srt"


def test_media_extract_subs_cli_name_uses_hyphen():
    """Test media extract-subs CLI command name uses a hyphen."""
    assert MediaExtractSubsCli.name() == "extract-subs"


def test_media_extract_subs_cli_details_uses_detected_chinese_script(
    tmp_path: Path,
):
    """Test media extract-subs details mode uses detected Chinese script in filenames.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"

    with (
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.get_subtitle_streams",
            return_value=[
                SubtitleStream(
                    index=4,
                    language="zho",
                    codec_name="subrip",
                ),
            ],
        ) as get_subtitle_streams,
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.get_zho_streams",
            return_value=[
                SubtitleStream(
                    index=4,
                    language="zho-Hant",
                    codec_name="subrip",
                ),
            ],
        ) as get_zho_streams,
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.extract_subtitle_stream"
        ) as extract,
        patch("scinoephile.cli.media.media_extract_subs_cli.cache_subtitle_streams"),
    ):
        run_cli_with_args(
            MediaExtractSubsCli,
            f"--infile {infile_path} --languages zho -o {output_dir_path} --details",
        )

    get_subtitle_streams.assert_not_called()
    get_zho_streams.assert_called_once_with(
        infile_path.resolve(),
        cache_dir_path=ANY,
    )
    extract.assert_called_once()
    assert extract.call_args.args[2] == output_dir_path.resolve() / "zho-Hant-4.srt"


def test_media_extract_subs_cli_output_dir_caches_matching_streams_together(
    tmp_path: Path,
):
    """Test media extract-subs caches matching streams in one batch before extraction.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"
    cache_dir_path = tmp_path / "cache"

    with (
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.get_subtitle_streams",
            return_value=[
                SubtitleStream(index=2, language="eng", codec_name="subrip"),
                SubtitleStream(index=3, language="zho", codec_name="subrip"),
            ],
        ),
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.cache_subtitle_streams"
        ) as cache,
        patch("scinoephile.cli.media.media_extract_subs_cli.extract_subtitle_stream"),
    ):
        run_cli_with_args(
            MediaExtractSubsCli,
            f"--infile {infile_path} --languages eng zho -o {output_dir_path} "
            f"--cache-dir {cache_dir_path}",
        )

    cache.assert_called_once()
    assert [stream.index for stream in cache.call_args.args[1]] == [2, 3]
    assert cache.call_args.kwargs == {"cache_dir_path": cache_dir_path.resolve()}


def test_media_extract_subs_cli_details_uses_stream_probe(tmp_path: Path):
    """Test media extract_subs CLI details mode passes through to stream probing."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"

    with (
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.get_subtitle_streams",
            return_value=[
                SubtitleStream(
                    index=2,
                    language="eng",
                    codec_name="subrip",
                    subtitle_count=42,
                ),
            ],
        ) as get_subtitle_streams,
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.get_zho_streams",
            return_value=[
                SubtitleStream(
                    index=2,
                    language="eng",
                    codec_name="subrip",
                    subtitle_count=42,
                ),
            ],
        ) as get_zho_streams,
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.extract_subtitle_stream"
        ) as extract,
        patch("scinoephile.cli.media.media_extract_subs_cli.cache_subtitle_streams"),
    ):
        run_cli_with_args(
            MediaExtractSubsCli,
            f"--infile {infile_path} --languages ENG --details -o {output_dir_path}",
        )

    get_subtitle_streams.assert_not_called()
    get_zho_streams.assert_called_once_with(
        infile_path.resolve(),
        cache_dir_path=ANY,
    )
    extract.assert_called_once()


def test_media_extract_subs_cli_requires_output_dir(tmp_path: Path):
    """Test media extract_subs CLI requires an output directory."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with (
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.get_subtitle_streams",
            return_value=[
                SubtitleStream(index=2, language="eng", codec_name="subrip"),
            ],
        ),
        pytest.raises(SystemExit) as excinfo,
    ):
        run_cli_with_args(MediaExtractSubsCli, f"--infile {infile_path}")

    assert excinfo.value.code == 2


def test_media_extract_subs_cli_creates_missing_output_dir(
    tmp_path: Path,
):
    """Test media extract_subs CLI logs when creating a missing output directory."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"

    with (
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.get_subtitle_streams",
            return_value=[
                SubtitleStream(index=2, language="eng", codec_name="subrip"),
            ],
        ),
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.extract_subtitle_stream"
        ) as extract,
        patch("scinoephile.cli.media.media_extract_subs_cli.cache_subtitle_streams"),
        patch("scinoephile.cli.media.media_extract_subs_cli.logger") as logger,
    ):
        run_cli_with_args(
            MediaExtractSubsCli,
            f"--infile {infile_path} --languages eng -o {output_dir_path}",
        )

    assert output_dir_path.exists()
    logger.info.assert_called_once_with(
        f"Created subtitle output directory: {output_dir_path.resolve()}"
    )
    extract.assert_called_once()


def test_media_extract_subs_cli_overwrites_existing_file(tmp_path: Path):
    """Test media extract_subs CLI overwrite exports existing matching streams."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"
    output_dir_path.mkdir()
    outfile_path = output_dir_path / "eng-2.srt"
    outfile_path.touch()

    with (
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.get_subtitle_streams",
            return_value=[
                SubtitleStream(index=2, language="eng", codec_name="subrip"),
            ],
        ),
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.extract_subtitle_stream"
        ) as extract,
        patch("scinoephile.cli.media.media_extract_subs_cli.cache_subtitle_streams"),
    ):
        run_cli_with_args(
            MediaExtractSubsCli,
            f"--infile {infile_path} --languages eng -o {output_dir_path} --overwrite",
        )

    extract.assert_called_once()
    assert extract.call_args.args[2] == outfile_path.resolve()


def test_media_extract_subs_cli_extracts_sup_streams_to_image_dirs(tmp_path: Path):
    """Test media extract_subs CLI converts SUP streams and extracts non-SUP streams."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"
    image_series = Mock()

    with (
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.get_subtitle_streams",
            return_value=[
                SubtitleStream(index=2, language="eng", codec_name="subrip"),
                SubtitleStream(index=3, language="zho", codec_name="hdmv_pgs_subtitle"),
            ],
        ),
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.extract_subtitle_stream"
        ) as extract,
        patch("scinoephile.cli.media.media_extract_subs_cli.cache_subtitle_streams"),
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.ImageSeries.load",
            return_value=image_series,
        ) as load,
    ):
        run_cli_with_args(
            MediaExtractSubsCli,
            f"--infile {infile_path} --languages eng zho -o {output_dir_path} "
            "--extract-sup",
        )

    assert extract.call_count == 2
    assert extract.call_args_list[0].args[2] == output_dir_path.resolve() / "eng-2.srt"
    assert extract.call_args_list[1].args[2] == output_dir_path.resolve() / "zho-3.sup"
    load.assert_called_once_with(output_dir_path.resolve() / "zho-3.sup")
    image_series.save.assert_called_once_with(output_dir_path.resolve() / "zho-3")


def test_media_extract_subs_cli_extracts_sup_file_to_image_dir(tmp_path: Path):
    """Test media extract_subs CLI converts SUP input files and copies the source."""
    infile_path = tmp_path / "source.sup"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"
    image_series = Mock()

    with (
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.ImageSeries.load",
            return_value=image_series,
        ) as load,
        patch("scinoephile.cli.media.media_extract_subs_cli.copy2") as copy,
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.get_subtitle_streams",
            return_value=[
                SubtitleStream(
                    index=0,
                    language=None,
                    codec_name="hdmv_pgs_subtitle",
                ),
            ],
        ) as get_subtitle_streams,
    ):
        run_cli_with_args(
            MediaExtractSubsCli,
            f"--infile {infile_path} -o {output_dir_path} --extract-sup",
        )

    get_subtitle_streams.assert_called_once_with(
        infile_path.resolve(),
    )
    load.assert_called_once_with(output_dir_path.resolve() / "source.sup")
    image_series.save.assert_called_once_with(output_dir_path.resolve() / "source")
    copy.assert_called_once_with(
        infile_path.resolve(),
        output_dir_path.resolve() / "source.sup",
    )


def test_media_extract_subs_cli_extracts_sup_file_to_image_dir_in_place(tmp_path: Path):
    """Test media extract_subs CLI converts SUP input files in place."""
    infile_path = tmp_path / "source.sup"
    infile_path.touch()
    image_series = Mock()

    with (
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.ImageSeries.load",
            return_value=image_series,
        ) as load,
        patch("scinoephile.cli.media.media_extract_subs_cli.copy2") as copy,
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.get_subtitle_streams",
            return_value=[
                SubtitleStream(
                    index=0,
                    language=None,
                    codec_name="hdmv_pgs_subtitle",
                ),
            ],
        ),
    ):
        run_cli_with_args(
            MediaExtractSubsCli,
            f"--infile {infile_path} -o {tmp_path} --extract-sup --overwrite",
        )

    copy.assert_not_called()
    load.assert_called_once_with(infile_path.resolve())
    image_series.save.assert_called_once_with(tmp_path.resolve() / "source")


def test_media_extract_subs_cli_rejects_sup_file_without_subtitle_streams(
    tmp_path: Path,
):
    """Test media extract_subs CLI rejects SUP input files without subtitle streams."""
    infile_path = tmp_path / "source.sup"
    infile_path.touch()

    with (
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.get_subtitle_streams",
            return_value=[],
        ),
        pytest.raises(SystemExit) as excinfo,
    ):
        run_cli_with_args(MediaExtractSubsCli, f"--infile {infile_path} -o {tmp_path}")

    assert excinfo.value.code == 2


def test_media_extract_subs_cli_rejects_export_argument(tmp_path: Path):
    """Test media extract_subs CLI rejects the removed export argument."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with pytest.raises(SystemExit) as excinfo:
        run_cli_with_args(MediaExtractSubsCli, f"--infile {infile_path} --export")

    assert excinfo.value.code == 2


def test_media_extract_subs_cli_extract_sup_requires_output_dir(tmp_path: Path):
    """Test media extract_subs CLI rejects SUP extraction without output directory."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with pytest.raises(SystemExit) as excinfo:
        run_cli_with_args(
            MediaExtractSubsCli,
            f"--infile {infile_path} --extract-sup",
        )

    assert excinfo.value.code == 2


def test_media_extract_subs_cli_overwrite_requires_output_dir(tmp_path: Path):
    """Test media extract_subs CLI rejects overwrite without output directory."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with pytest.raises(SystemExit) as excinfo:
        run_cli_with_args(
            MediaExtractSubsCli,
            f"--infile {infile_path} --overwrite",
        )

    assert excinfo.value.code == 2
