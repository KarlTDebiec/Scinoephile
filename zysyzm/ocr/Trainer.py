#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.ocr.Trainer.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from zysyzm import CLToolBase


################################### CLASSES ###################################
class Trainer(CLToolBase):
    """Trains model"""

    # region Instance Variables
    help_message = ("Tool for training model")

    # endregion

    # region Builtins
    def __init__(self, **kwargs):
        """
        Initializes tool

        Args:
            kwargs (dict): Additional keyword arguments
        """
        super().__init__(**kwargs)

    def __call__(self):
        """Core logic"""
        pass

    # endregion

#################################### MAIN #####################################
if __name__ == "__main__":
    Trainer.main()
