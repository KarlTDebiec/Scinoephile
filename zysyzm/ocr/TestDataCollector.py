#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.ocr.TestDataCollector.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from zysyzm.ocr import OCRCLToolBase


################################### CLASSES ###################################
class TestDataCollector(OCRCLToolBase):
    """Collects test data based on interim model"""

    # region Instance Variables
    help_message = ("Tool for collecting test data based on interim model")

    # endregion

    # region Builtins
    def __init__(self, **kwargs):
        """
        Initializes tool

        Args:
            kwargs (dict): Additional keyword arguments
        """
        super().__init__(**kwargs)

        # self.src_input_directory = \
        #     "/Users/kdebiec/Desktop/docs/subtitles/magnificent_mcdull"
        # self.tst_output_suffix = "00"
        # self.skip_chars = "国军第此性业政美"
        # self.src_input_directory = \
        #     "/Users/kdebiec/Desktop/docs/subtitles/mcdull_kung_fu_ding_ding_dong"
        # self.tst_output_suffix = "01"
        # self.skip_chars = "着性政战政"
        self.src_input_directory = \
            "/Users/kdebiec/Desktop/docs/subtitles/mcdull_prince_de_la_bun"
        self.tst_output_suffix = "02"
        self.skip_chars = "着军"

        self.n_chars = 244
        self.tst_output_directory = \
            "/Users/kdebiec/Desktop/docs/subtitles/tst"
        self.model_infile = "/Users/kdebiec/Desktop/docs/subtitles/model.h5"



    def __call__(self):
        """Core logic"""
        import numpy as np
        import tensorflow as tf
        from tensorflow import keras
        from os.path import isfile
        from shutil import copyfile
        from PIL import Image

        if self.model_infile is not None:
            # Reload model
            if self.verbosity >= 1:
                print(f"Loading model from {self.model_infile}")
            model = keras.models.load_model(self.model_infile)
            model.compile(optimizer=tf.train.AdamOptimizer(),
                          loss='sparse_categorical_crossentropy',
                          metrics=['accuracy'])

        # Make predictions for source images
        src_img, src_infiles = self.load_unlabeled_data(self.src_input_directory)

        src_pred = model.predict(src_img)

        for char in self.chars[:self.n_chars]:
            tstfile = f"{self.tst_output_directory}/" \
                      f"{char}_{self.tst_output_suffix}.png"
            if char in self.skip_chars:
                if self.verbosity >= 1:
                    print(f"skipping {char}")
            elif isfile(tstfile):
                if self.verbosity >= 1:
                    print(f"{tstfile} already exists")
            else:
                scores = src_pred[:, self.chars_to_labels(char)]
                for index in np.argsort(scores)[::-1]:
                    if scores[index] < 0.99:
                        continue
                    print(f"{char} {index:5d} {scores[index]:4.2f}" \
                          f"{src_infiles[index]}")
                    image = Image.open(src_infiles[index])
                    image.show()
                    match = input(f"Is this an image of {char}?")
                    if match.lower().startswith("y"):
                        if self.verbosity >= 1:
                            print(f"copying {src_infiles[index]} to {tstfile}")
                        copyfile(src_infiles[index], tstfile)
                        break

        # Interactive prompt
        if self.interactive:
            from IPython import embed
            embed()

    # endregion

    # region Properties
    @property
    def model_infile(self):
        """str: Path to input model file"""
        if not hasattr(self, "_model_infile"):
            self._model_infile = None
        return self._model_infile

    @model_infile.setter
    def model_infile(self, value):
        from os.path import expandvars, isfile

        if not isinstance(value, str) and value is not None:
            raise ValueError()
        else:
            value = expandvars(value)
            if not isfile(value):
                raise ValueError()
        self._model_infile = value

    @property
    def n_chars(self):
        """int: Number of characters to seek test data for"""
        if not hasattr(self, "_n_chars"):
            self._n_chars = 21
        return self._n_chars

    @n_chars.setter
    def n_chars(self, value):
        if not isinstance(value, int) and value is not None:
            try:
                value = int(value)
            except Exception as e:
                raise ValueError()
        if value < 1 and value is not None:
            raise ValueError()
        self._n_chars = value

    @property
    def src_input_directory(self):
        """str: Directory of unlabeled source character images"""
        if not hasattr(self, "_src_input_directory"):
            self._src_input_directory = None
        return self._src_input_directory

    @src_input_directory.setter
    def src_input_directory(self, value):
        from os.path import expandvars, isdir

        if not isinstance(value, str) and value is not None:
            raise ValueError()
        elif isinstance(value, str):
            value = expandvars(value)
            if not isdir(value):
                raise ValueError()
        self._src_input_directory = value

    @property
    def skip_chars(self):
        """list(str): Characters to skip search for"""
        if not hasattr(self, "_skip_chars"):
            self._skip_chars = []
        return self._skip_chars

    @skip_chars.setter
    def skip_chars(self, value):
        if not isinstance(value, list) and value is not None:
            try:
                value = list(value)
            except Exception as e:
                raise ValueError()
        self._skip_chars = value

    @property
    def tst_output_directory(self):
        """str: Directory for output labeled test character images"""
        if not hasattr(self, "_tst_output_directory"):
            self._tst_output_directory = None
        return self._tst_output_directory

    @tst_output_directory.setter
    def tst_output_directory(self, value):
        from os import makedirs
        from os.path import expandvars, isdir

        if not isinstance(value, str) and value is not None:
            raise ValueError()
        elif isinstance(value, str):
            value = expandvars(value)
            if not isdir(value):
                try:
                    makedirs(value)
                except Exception as e:
                    raise ValueError()
        self._tst_output_directory = value

    @property
    def tst_output_suffix(self):
        """string: Suffix added to labeled test character images"""
        if not hasattr(self, "_tst_output_suffix"):
            self._tst_output_suffix = None
        return self._tst_output_suffix

    @tst_output_suffix.setter
    def tst_output_suffix(self, value):
        if not isinstance(value, str) and value is not None:
            raise ValueError()
        self._tst_output_suffix = value

    # endregion

    # region Methods
    def load_unlabeled_data(self, directory):
        import numpy as np
        from glob import iglob
        from PIL import Image
        from os.path import basename

        infiles = sorted(iglob(f"{directory}/*/[0-9][0-9].png"))
        imgs = []
        for infile in infiles:
            img = Image.open(infile)
            raw = np.array(img)
            imgs += [np.append(np.logical_or(raw == 85, raw == 256).flatten(),
                               np.logical_or(raw == 170, raw == 256).flatten())]
        return np.stack(imgs), infiles

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    TestDataCollector.main()
