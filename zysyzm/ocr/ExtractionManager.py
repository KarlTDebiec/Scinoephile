#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.ocr.ExtractionManager.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from zysyzm import CLToolBase
from zysyzm.ocr import resize_image, trim_image


################################### CLASSES ###################################
class ExtractionManager(CLToolBase):
    """Extracts individual characters from image-based subtitles"""

    # region Instance Variables
    help_message = ("Tool for extracting individual characters from"
                    "image-based subtitles")

    # endregion

    # region Builtins
    def __init__(self, input_directory=None, output_directory=None, **kwargs):
        """
        Initializes tool

        Args:
            input_directory (str): Path to directory containing input subtitle
              images
            output_directory (str): Path to directory for output character
              images
            kwargs (dict): Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.input_directory = input_directory
        self.output_directory = output_directory

    def __call__(self):
        """Core logic"""
        import numpy as np
        from os import mkdir
        from os.path import basename, isdir
        from PIL import Image, ImageDraw

        threshold = 0.04

        if self.verbosity >= 1:
            print("Processing subtitle image files in "
                  f"'{self.input_directory}'")
            print("Saving character image files  to "
                  f"'{self.output_directory}'")

        # Loop over subtitles
        for infile in self.input_images:
            if self.verbosity >= 1:
                print(f"Processing '{basename(infile)}'")

            # Open image
            subtitle_img = trim_image(Image.open(infile).convert("LA"))
            subtitle_output_directory = \
                f"{self.output_directory}/{basename(infile).rstrip('.png')}"
            if not isdir(subtitle_output_directory):
                mkdir(subtitle_output_directory)
            subtitle_outfile = f"{subtitle_output_directory}/full.png"

            # Identify blank columns containing only white pixels
            raw = np.asarray(subtitle_img)[:, :, 0]
            nonwhite_pixels_in_column = (raw < raw.max()).sum(axis=0)
            blank_columns = np.where(nonwhite_pixels_in_column == 0)[0]
            if len(blank_columns) == 0:
                if self.verbosity >= 1:
                    print("    Whitespace between characters could not be "
                          f"found for '{basename(infile)}'; skipping")
                continue

            # Identify boundaries between characters
            char_boundaries = np.array([0])
            char_width = 75

            # Loop over characters in subtitle
            while True:
                # Estimate location of next boundary between characters
                next_boundary = char_boundaries[-1] + char_width
                if next_boundary >= subtitle_img.size[0] - (char_width / 2):
                    break

                # Identify blank columns closest to estimated boundary
                delta = np.abs(blank_columns - next_boundary) / next_boundary
                try:
                    close = np.where(delta < threshold)[0]
                    if close.size == 0:
                        close = np.where(delta < threshold * 2)[0]
                    if close.size == 0:
                        close = np.where(delta < threshold * 3)[0]
                    if close.size == 0:
                        # Look for half-width characters
                        next_boundary -= 37
                        delta = np.abs(blank_columns - next_boundary
                                       ) / next_boundary
                        close = np.where(delta < threshold)[0]
                        if close.size == 0:
                            close = np.where(delta < threshold * 2)[0]
                        if close.size == 0:
                            close = np.where(delta < threshold * 3)[0]
                        if close.size == 0:
                            # Last-ditch check for very thin characters
                            next_boundary -= 10
                            delta = np.abs(blank_columns - next_boundary
                                           ) / next_boundary
                            close = np.where(delta < threshold)[0]
                            if close.size == 0:
                                close = np.where(delta < threshold * 2)[0]
                            if close.size == 0:
                                close = np.where(delta < threshold * 3)[0]
                    boundary_index = int(np.median(close))
                except ValueError as e:
                    if self.verbosity >= 1:
                        print("    Problem finding spaces between characters "
                              f"for '{basename(infile)}; breaking")
                    break
                boundary = blank_columns[boundary_index]

                # Add to list of boundaries, refine estimate of character
                #   width, and estimate location of next boundary
                char_boundaries = np.append(char_boundaries, boundary)
                char_widths = (char_boundaries[1:] - char_boundaries[:-1])
                full_width_chars = np.extract(char_widths > 56, char_widths)
                if full_width_chars.size >= 1:
                    char_width = np.mean(full_width_chars)
                else:
                    char_width = 75
                next_boundary = char_boundaries[-1] + char_width
            char_boundaries = np.append(char_boundaries, subtitle_img.size[0])

            # Write annotated subtitle image
            draw = ImageDraw.Draw(subtitle_img)
            for boundary in char_boundaries[1:]:
                draw.line((boundary, 0, boundary, subtitle_img.size[1]),
                          fill=0, width=2)
            subtitle_img.save(subtitle_outfile)

            # Write individual character images
            j = 0
            for i in range(len(char_boundaries) - 1):
                char = subtitle_img.crop((char_boundaries[i],
                                          0,
                                          char_boundaries[i + 1],
                                          subtitle_img.size[1]))
                char = trim_image(trim_image(char))  # Unclear why 2X needed
                if char is not None:
                    char = resize_image(char, (80, 80))
                    char.save(f"{subtitle_output_directory}/{j:02d}.png")
                    j += 1

    # endregion

    # region Properties
    @property
    def input_directory(self):
        """str: Path to directory containing input subtitle images"""
        if not hasattr(self, "_input_directory"):
            self._input_directory = None
        return self._input_directory

    @input_directory.setter
    def input_directory(self, value):
        from os.path import expandvars, isdir

        if not isinstance(value, str) and value is not None:
            raise ValueError()
        else:
            value = expandvars(value)
            if not isdir(value):
                raise ValueError()
        self._input_directory = value

    @property
    def input_images(self):
        from glob import iglob

        return sorted(iglob("{0}/*.png".format(self.input_directory)))

    @property
    def output_directory(self):
        """str: Path to directory for output character images"""
        if not hasattr(self, "_output_directory"):
            self._output_directory = None
        return self._output_directory

    @output_directory.setter
    def output_directory(self, value):
        from os import makedirs
        from os.path import expandvars, isdir

        if not isinstance(value, str) and value is not None:
            raise ValueError()
        else:
            value = expandvars(value)
            if not isdir(value):
                try:
                    makedirs(value)
                except Exception as e:
                    raise ValueError()
        self._output_directory = value

    # endregion

    # region Class Methods
    @classmethod
    def construct_argparser(cls, parser=None):
        """
        Constructs argument parser

        Returns:
            parser (argparse.ArgumentParser): Argument parser
        """
        import argparse

        # Prepare parser
        if isinstance(parser, argparse.ArgumentParser):
            parser = parser
        elif isinstance(parser, argparse._SubParsersAction):
            parser = parser.add_parser(name="extraction",
                                       description=cls.help_message,
                                       help=cls.help_message)
        elif parser is None:
            parser = argparse.ArgumentParser(description=cls.help_message)
        super().construct_argparser(parser)

        # Input
        parser_inp = parser.add_argument_group("input arguments")
        parser_inp.add_argument("-i", "--input_directory",
                                type=str, required=True,
                                help="path to input directory")

        # Output
        parser_out = parser.add_argument_group("output arguments")
        parser_out.add_argument("-o", "--output_directory",
                                type=str, required=True,
                                help="path to output directory")

        return parser
    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    ExtractionManager.main()
