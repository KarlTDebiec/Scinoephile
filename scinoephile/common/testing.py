#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Testing."""

from __future__ import annotations

import sys
from inspect import getfile
from unittest.mock import patch

from .command_line_interface import CommandLineInterface


def run_cli_with_args(cli: type[CommandLineInterface], args: str = ""):
    """Run CommandLineInterface as if from shell with provided args.

    Arguments:
        cli: CommandLineInterface to run
        args: Arguments to pass
    """
    with patch.object(sys, "argv", [getfile(cli)] + args.split()):
        cli.main()
