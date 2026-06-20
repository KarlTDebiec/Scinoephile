#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.media.MediaProbeCli."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from pytest import CaptureFixture, raises

from scinoephile.cli.media.media_probe_cli import MediaProbeCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.media import AudioStream, SubtitleStream, VideoStream
from scinoephile.lang.zho.subtitles.analysis import ZhoSubtitleScriptAnalysis
from test.helpers import parametrize


def test_media_probe_cli_lists_all_streams(tmp_path: Path, capsys: CaptureFixture[str]):
    """Test media probe CLI lists all streams without packet counts.

    Arguments:
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with patch(
        "scinoephile.media.probe.ffmpeg.probe",
        return_value={
            "streams": [
                {
                    "index": 0,
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1920,
                    "height": 1080,
                },
                {
                    "index": 1,
                    "codec_type": "audio",
                    "codec_name": "aac",
                    "channels": 2,
                    "tags": {"language": "eng"},
                },
                {
                    "index": 2,
                    "codec_type": "subtitle",
                    "codec_name": "subrip",
                    "tags": {"language": "eng", "title": "SDH"},
                },
            ],
        },
    ):
        run_cli_with_args(MediaProbeCli, f"--infile {infile_path}")

    assert capsys.readouterr().out.splitlines() == [
        "Stream #0:0: Video: h264 (1920x1080)",
        "Stream #0:1(eng): Audio: aac (channels=2)",
        "Stream #0:2(eng): Subtitle: subrip (title=SDH)",
    ]


@parametrize(
    ("script", "language"),
    [
        ("zho-Hant", "zho-Hant"),
        (None, "zho-Unknown"),
    ],
)
def test_media_probe_cli_details_includes_chinese_script_in_stream_id(
    tmp_path: Path,
    capsys: CaptureFixture[str],
    script: str | None,
    language: str,
):
    """Test media probe CLI includes Chinese script analysis in stream ID.

    Arguments:
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
        script: detected script subtag, if determined
        language: expected stream language
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with (
        patch(
            "scinoephile.media.probe.ffmpeg.probe",
            return_value={
                "streams": [
                    {
                        "index": 2,
                        "codec_type": "subtitle",
                        "codec_name": "subrip",
                        "tags": {"language": "zho"},
                    },
                ],
            },
        ),
        patch(
            "scinoephile.lang.zho.subtitles.streams.analyze_zho_subtitle_stream_script"
        ) as analyze,
        patch("scinoephile.media.subtitles.details.get_subtitle_stream_stats") as stats,
        patch("scinoephile.media.subtitles.details.cache_subtitles"),
    ):
        analyze.return_value.script = script
        stats.return_value.event_count = 12
        stats.return_value.first_start_ms = 62_500
        stats.return_value.last_end_ms = 3_725_250
        run_cli_with_args(MediaProbeCli, f"--infile {infile_path} --details")

    assert capsys.readouterr().out.splitlines() == [
        (
            f"Stream #0:2({language}): Subtitle: subrip "
            "(subtitles=12, span=00:01:02-01:02:05)"
        ),
    ]


def test_media_probe_cli_details_preserves_non_subtitle_streams(
    tmp_path: Path,
    capsys: CaptureFixture[str],
):
    """Test media probe CLI detail mode still lists non-subtitle streams.

    Arguments:
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with (
        patch(
            "scinoephile.cli.media.media_probe_cli.get_streams",
            return_value=[
                VideoStream(
                    index=0,
                    codec_type="video",
                    codec_name="h264",
                    width=1920,
                    height=1080,
                ),
                AudioStream(
                    index=1,
                    codec_type="audio",
                    codec_name="aac",
                    language="eng",
                    channels=2,
                ),
                SubtitleStream(
                    index=2,
                    codec_type="subtitle",
                    codec_name="subrip",
                    language="zho",
                ),
            ],
        ),
        patch(
            "scinoephile.cli.media.media_probe_cli.get_zho_subtitle_streams",
            return_value=[
                SubtitleStream(
                    index=2,
                    codec_type="subtitle",
                    codec_name="subrip",
                    language="zho-Hant",
                    subtitle_count=12,
                    first_start_ms=62_500,
                    last_end_ms=3_725_250,
                ),
            ],
        ),
    ):
        run_cli_with_args(MediaProbeCli, f"--infile {infile_path} --details")

    assert capsys.readouterr().out.splitlines() == [
        "Stream #0:0: Video: h264 (1920x1080)",
        "Stream #0:1(eng): Audio: aac (channels=2)",
        (
            "Stream #0:2(zho-Hant): Subtitle: subrip "
            "(subtitles=12, span=00:01:02-01:02:05)"
        ),
    ]


def test_media_probe_cli_details_omits_unreadable_subtitle_stats(
    tmp_path: Path,
    capsys: CaptureFixture[str],
):
    """Test media probe CLI survives unreadable subtitle stats.

    Arguments:
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with (
        patch(
            "scinoephile.media.probe.ffmpeg.probe",
            return_value={
                "streams": [
                    {
                        "index": 2,
                        "codec_type": "subtitle",
                        "codec_name": "hdmv_pgs_subtitle",
                        "tags": {"language": "ita", "title": "SDH"},
                    },
                ],
            },
        ),
        patch(
            "scinoephile.media.subtitles.details.get_subtitle_stream_stats",
            side_effect=ValueError("Malformed SUP data"),
        ),
        patch("scinoephile.media.subtitles.details.cache_subtitles"),
    ):
        run_cli_with_args(MediaProbeCli, f"--infile {infile_path} --details")

    assert capsys.readouterr().out.splitlines() == [
        "Stream #0:2(ita): Subtitle: hdmv_pgs_subtitle (title=SDH)",
    ]


def test_media_probe_cli_force_check_script_checks_standalone_sup(
    tmp_path: Path,
    capsys: CaptureFixture[str],
):
    """Test forced script checking treats a standalone SUP file as Chinese.

    Arguments:
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
    """
    infile_path = tmp_path / "source.sup"
    infile_path.touch()
    cache_dir_path = tmp_path / "cache"

    def analyze_script(*args: object, **kwargs: object) -> ZhoSubtitleScriptAnalysis:
        """Return script analysis after checking analyzer inputs."""
        assert args[0] == infile_path
        stream = args[1]
        assert isinstance(stream, SubtitleStream)
        assert stream.index == 0
        assert stream.codec_name == "hdmv_pgs_subtitle"
        assert stream.language == "zho"
        assert kwargs == {"cache_dir_path": cache_dir_path}
        return ZhoSubtitleScriptAnalysis(script="zho-Hant")

    with (
        patch(
            "scinoephile.cli.media.media_probe_cli.get_streams",
            side_effect=AssertionError("ffprobe should not be used"),
        ),
        patch(
            "scinoephile.cli.media.media_probe_cli.analyze_zho_subtitle_stream_script",
            side_effect=analyze_script,
        ) as analyze,
    ):
        run_cli_with_args(
            MediaProbeCli,
            (
                f"--infile {infile_path} --cache-dir {cache_dir_path} "
                "--force-check-script"
            ),
        )

    assert capsys.readouterr().out.splitlines() == [
        "Stream #0:0(zho-Hant): Subtitle: hdmv_pgs_subtitle",
    ]
    analyze.assert_called_once()


def test_media_probe_cli_force_check_script_rejects_non_sup(
    tmp_path: Path,
    capsys: CaptureFixture[str],
):
    """Test forced script checking rejects non-SUP inputs.

    Arguments:
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            MediaProbeCli,
            f"--infile {infile_path} --force-check-script",
        )

    assert "--force-check-script requires a SUP infile" in capsys.readouterr().err
