#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.AnalysisCerCli."""

from __future__ import annotations

import pytest

from scinoephile.analysis import CharacterErrorRateResult
from scinoephile.cli.analysis.analysis_cer_cli import AnalysisCerCli
from scinoephile.cli.analysis.analysis_cli import AnalysisCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (AnalysisCerCli,),
        (AnalysisCli, AnalysisCerCli),
        (ScinoephileCli, AnalysisCli, AnalysisCerCli),
    ],
)
def test_analysis_cer_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test analysis cer CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (AnalysisCerCli,),
        (AnalysisCli, AnalysisCerCli),
        (ScinoephileCli, AnalysisCli, AnalysisCerCli),
    ],
)
def test_analysis_cer_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test analysis cer CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


@pytest.mark.parametrize(
    ("reference_path", "candidate_path", "expected_fixture_name"),
    [
        (
            "kob/output/yue-Hans/timewarp_clean_flatten.srt",
            "kob/output/yue-Hans_transcribe.srt",
            "kob_yue_hans_transcribe_expected_cer",
        ),
        (
            "kob/output/yue-Hans/timewarp_clean_flatten.srt",
            "kob/output/yue-Hans_transcribe_review_translate_block_review.srt",
            "kob_yue_hans_transcribe_review_translate_block_review_expected_cer",
        ),
    ],
)
def test_analysis_cer_cli(
    reference_path: str,
    candidate_path: str,
    expected_fixture_name: str,
    request: pytest.FixtureRequest,
    capsys: pytest.CaptureFixture,
):
    """Test analysis cer CLI output against expected CER values.

    Arguments:
        reference_path: path to reference subtitle fixture
        candidate_path: path to candidate subtitle fixture
        expected_fixture_name: fixture name containing expected CER result
        request: pytest fixture request object
        capsys: pytest stdout/stderr capture fixture
    """
    reference_infile_path = test_data_root / reference_path
    candidate_infile_path = test_data_root / candidate_path
    expected_result: CharacterErrorRateResult = request.getfixturevalue(
        expected_fixture_name
    )

    run_cli_with_args(
        AnalysisCerCli,
        f"--reference-infile {reference_infile_path} "
        f"--candidate-infile {candidate_infile_path}",
    )
    output = capsys.readouterr().out

    assert f"CER: {expected_result.cer}" in output
    assert f"Correct: {expected_result.correct}" in output
    assert f"Substitutions: {expected_result.substitutions}" in output
    assert f"Insertions: {expected_result.insertions}" in output
    assert f"Deletions: {expected_result.deletions}" in output
    assert f"Reference length: {expected_result.reference_length}" in output
