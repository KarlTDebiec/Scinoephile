#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.ExtractionManager.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import numpy as np
from glob import iglob
from os import mkdir
from os.path import basename, expandvars, isdir
from IPython import embed
from PIL import Image, ImageChops, ImageDraw
from zysyzm.CLToolBase import CLToolBase


################################### CLASSES ###################################
class ExtractionManager(CLToolBase):
    """ Extracts characters from image-based subtitles """

    # region Instance Variables
    help_message = ("Extracts characters from image-based subtitles")

    # endregion

    # region Builtins
    def __call__(self):
        def trim(image):
            background = Image.new(image.mode, image.size,
                                   image.getpixel((0, 0)))
            diff = ImageChops.difference(image, background)
            diff = ImageChops.add(diff, diff, 2.0, -100)
            bbox = diff.getbbox()
            if bbox:
                return image.crop(bbox)

        def resize_image(image, new_size):
            x = int(np.floor((new_size[0] - image.size[0]) / 2))
            y = int(np.floor((new_size[1] - image.size[1]) / 2))
            new_image = Image.new(image.mode, new_size, image.getpixel((0, 0)))
            new_image.paste(image, (x, y, x + image.size[0], y + image.size[1]))
            return new_image

        indir = expandvars("${DROPBOX}/code/subtitles/mcdull_prince_de_la_bun/cmn-Hans")
        # indir = "${DROPBOX}/code/subtitles/mcdull_kung_fu_ding_ding_dong/cmn-Hans"
        # indir = "${DROPBOX}/code/subtitles/magnificent_mcdull/cmn-Hans"
        base_outdir = expandvars("${HOME}/desktop/docs/subtitles/")
        threshold = 0.04

        if self.verbosity >= 1:
            print(f"Processing subtitle image files in '{indir}'")
            print(f"Saving individual character files to '{base_outdir}'")

        for infile in sorted(iglob("{0}/*.png".format(indir))):
            if self.verbosity >= 1:
                print(f"Processing '{basename(infile)}'")
            outdir = "{0}/{1}".format(base_outdir,
                                      basename(infile).rstrip(".png"))
            if not isdir(outdir):
                mkdir(outdir)

            # Open image
            image = Image.open(infile).convert("LA")
            image = trim(image)
            draw = ImageDraw.Draw(image)

            # Identify blank columns containing only white pixels
            raw = np.asarray(image)[:, :, 0]
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

            while True:
                # Estimate location of next boundary between characters
                next_boundary = char_boundaries[-1] + char_width
                if next_boundary >= image.size[0] - (char_width / 2):
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
            char_boundaries = np.append(char_boundaries, image.size[0])

            outfile = f"{outdir}/full.png"
            for boundary in char_boundaries[1:]:
                draw.line((boundary, 0, boundary, image.size[1]),
                          fill=0, width=2)
            image.save(outfile)

            for i in range(len(char_boundaries) - 1):
                char = image.crop((char_boundaries[i], 0,
                                   char_boundaries[i + 1], image.size[1]))
                char = trim(trim(char))
                if char is not None:
                    char = resize_image(char, (80,80))
                    char.save(f"{outdir}/{i:02d}.png")

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    ExtractionManager.main()
