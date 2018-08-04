#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.ocr.__init__.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################## FUNCTIONS ##################################
def trim_image(image):
    """
    Trims outer rows and columns of an image based on background color

    Args:
        image (): source image

    Returns (): trimmed image

    """
    from PIL import Image, ImageChops

    background = Image.new(image.mode, image.size,
                           image.getpixel((0, 0)))
    diff = ImageChops.difference(image, background)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()

    if bbox:
        return image.crop(bbox)


def resize_image(image, new_size):
    """
    Resizes an image, keeping current contents centered

    Args:
        image (): source image
        new_size (tuple(int, int)): New width and height

    Returns (): resized image

    """
    import numpy as np
    from PIL import Image

    x = int(np.floor((new_size[0] - image.size[0]) / 2))
    y = int(np.floor((new_size[1] - image.size[1]) / 2))
    new_image = Image.new(image.mode, new_size, image.getpixel((0, 0)))
    new_image.paste(image, (x, y, x + image.size[0], y + image.size[1]))

    return new_image
