#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.media.MediaExtractSubsCli."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from scinoephile.cli.media.media_extract_subs_cli import MediaExtractSubsCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import ScinoephileError
from scinoephile.core.media import SubtitleStream
from scinoephile.workflows.subtitle_extraction import (
    SubtitleExtractionOutput,
    SubtitleExtractionOutputKind,
    SubtitleExtractionOutputStatus,
    SubtitleExtractionResult,
)


def test_media_extract_subs_cli_passes_arguments_to_workflow(tmp_path: Path):
    """Test media extract-subs CLI passes parsed arguments to the workflow.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"
    cache_dir_path = tmp_path / "cache"

    with patch(
        "scinoephile.cli.media.media_extract_subs_cli.extract_subtitles",
        return_value=SubtitleExtractionResult(
            infile_path=infile_path.resolve(),
            outputs=[],
        ),
    ) as extract:
        run_cli_with_args(
            MediaExtractSubsCli,
            f"--infile {infile_path} --languages eng zho -o {output_dir_path} "
            f"--details --extract-sup --overwrite --cache-dir {cache_dir_path}",
        )

    extract.assert_called_once_with(
        infile_path=infile_path.resolve(),
        languages=["eng", "zho"],
        output_dir_path=output_dir_path.resolve(),
        cache_dir_path=cache_dir_path.resolve(),
        details=True,
        extract_sup=True,
        overwrite=True,
    )


def test_media_extract_subs_cli_renders_grouped_outputs(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    """Test media extract-subs CLI renders workflow output groups.

    Arguments:
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"
    stream = SubtitleStream(index=2, language="eng", codec_name="subrip")
    result = SubtitleExtractionResult(
        infile_path=infile_path.resolve(),
        outputs=[
            SubtitleExtractionOutput(
                kind=SubtitleExtractionOutputKind.SUBTITLE,
                status=SubtitleExtractionOutputStatus.CREATED,
                stream=stream,
                path=output_dir_path.resolve() / "eng-2.srt",
            ),
            SubtitleExtractionOutput(
                kind=SubtitleExtractionOutputKind.IMAGE_SERIES,
                status=SubtitleExtractionOutputStatus.EXISTED,
                stream=stream,
                path=output_dir_path.resolve() / "eng-2",
            ),
        ],
    )

    with patch(
        "scinoephile.cli.media.media_extract_subs_cli.extract_subtitles",
        return_value=result,
    ):
        run_cli_with_args(
            MediaExtractSubsCli,
            f"--infile {infile_path} --languages eng -o {output_dir_path}",
        )

    subtitle_path = output_dir_path.resolve() / "eng-2.srt"
    image_series_path = output_dir_path.resolve() / "eng-2"
    assert capsys.readouterr().out.splitlines() == [
        "Created:",
        f"  subtitle: {stream.description} -> {subtitle_path}",
        "Already existed:",
        f"  image series: {stream.description} -> {image_series_path}",
    ]


def test_media_extract_subs_cli_maps_workflow_errors_to_parser_errors(
    tmp_path: Path,
):
    """Test media extract-subs CLI maps workflow errors to parser errors.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "source.sup"
    infile_path.touch()

    with (
        patch(
            "scinoephile.cli.media.media_extract_subs_cli.extract_subtitles",
            side_effect=ScinoephileError("No subtitle streams found"),
        ),
        pytest.raises(SystemExit) as excinfo,
    ):
        run_cli_with_args(MediaExtractSubsCli, f"--infile {infile_path} -o {tmp_path}")

    assert excinfo.value.code == 2


def test_media_extract_subs_cli_requires_output_dir(tmp_path: Path):
    """Test media extract_subs CLI requires an output directory.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with pytest.raises(SystemExit) as excinfo:
        run_cli_with_args(MediaExtractSubsCli, f"--infile {infile_path}")

    assert excinfo.value.code == 2
