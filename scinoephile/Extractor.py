#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Extracts burned-in subtitles."""
from __future__ import annotations

from scinoephile import CLToolBase


class Extractor(CLToolBase):
    """Extracts burned-in subtitles."""

    # region Builtins

    def __init__(self, infile, **kwargs):
        """
        Initializes command-line tool and compiles list of operations.

        Args:
            **kwargs: Additional keyword arguments
        """
        from os.path import expandvars

        from scinoephile import is_readable

        super().__init__(**kwargs)

        # Compile input operations
        infile = expandvars(str(infile))
        if is_readable(infile):
            self.infile = infile
        else:
            raise IOError(f"MP4 infile '{infile}' cannot be read")

    def __call__(self):
        """Performs operations."""
        import cv2

        cap = cv2.VideoCapture(self.infile)

        n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # endregion

    # region Public Properties

    @property
    def infile(self):
        """list: Infile"""
        if not hasattr(self, "_infile"):
            self._infile = None
        return self._infile

    @infile.setter
    def infile(self, value):
        # TODO: Validate
        self._infile = value

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, **kwargs):
        """
        Constructs argument parser.

        Returns:
            parser (argparse.ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__, **kwargs)

        # Input
        parser_input = parser.add_argument_group("input arguments")
        parser_input.add_argument(
            "-if", "--infile", help="MP4 infile", metavar="FILE", required=True
        )

        return parser

    # endregion


if __name__ == "__main__":
    Extractor.main()
