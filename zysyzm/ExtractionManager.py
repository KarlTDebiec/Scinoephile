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
import cv2
import numpy as np
from glob import iglob
from os import mkdir
from os.path import basename, expandvars, isdir
from IPython import embed
from PIL import Image, ImageChops
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

        indir = "${DROPBOX}/code/subtitles/mcdull_prince_de_la_bun/cmn-Hans"
        # indir = "${DROPBOX}/code/subtitles/mcdull_kung_fu_ding_ding_dong/cmn-Hans"
        # indir = "${DROPBOX}/code/subtitles/magnificent_mcdull/cmn-Hans"
        base_outdir = "${HOME}/desktop/docs/subtitles/"

        for infile in sorted(iglob("{0}/*.png".format(expandvars(indir)))):
            print(basename(infile))
            outdir = "{0}/{1}".format(expandvars(base_outdir),
                                      basename(infile).rstrip(".png"))
            # if not isdir(outdir):
            #     mkdir(outdir)
            outfile = "{0}.png".format(outdir)

            # image = Image.open(infile)
            # image = trim(image)
            # if np.abs(np.round(image.size[0]/72)
            #           - np.round(image.size[0]/72, 2)) >= 0.1:
            #     print("{0:17s}  {1:5.2f}  {2:5.2f}  {3}".format(
            #         basename(infile),
            #         np.round(image.size[0]/72),
            #         np.round(image.size[0]/72, 2),
            #         image.size))
            #     image.show()
            #     embed(display_banner=False)

            # image = Image.open(infile)
            # image.show()
            # input()

            image = cv2.imread(infile)
            # ret, thresh = cv2.threshold(image, 10, 255, cv2.THRESH_OTSU)
            # print("Threshold selected : ", ret)
            # cv2.imwrite("./debug.png", thresh)
            # image = Image.open("./debug.png")
            # image.show()
            # embed(display_banner=False)

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
            kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
            dilated = cv2.dilate(thresh, kernel, iterations=13)
            _, contours, hierarchy = cv2.findContours(dilated,
                                                      cv2.RETR_EXTERNAL,
                                                      cv2.CHAIN_APPROX_NONE)
            for contour in contours:
                # get rectangle bounding contour
                [x, y, w, h] = cv2.boundingRect(contour)

                # discard areas that are too large
                # if h > 300 and w > 300:
                #     continue

                # discard areas that are too small
                # if h < 40 or w < 40:
                #     continue

                # draw rectangle around contour on original image
                cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 2)
                roi = image[y:y + h, x:x + w]

                cv2.imwrite(outfile, image)

            # embed(display_banner=False)

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    ExtractionManager.main()
