#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.TestDataCollector.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile.ocr import (OCRCLToolBase, draw_text_on_image,
                             generate_char_img)


################################### CLASSES ###################################
class TestDataCollector(OCRCLToolBase):
    """
    Collects test data based on interim model

    .. todo::
      - [ ] Refactor with new dataset classes
      - [ ] Implement CL arguments
      - [ ] Decide whether or not to move load_unlabeled_data out of class
      - [ ] Move logic out of __call__
    """

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
        # self.src_input_directory = \
        #     "/Users/kdebiec/Desktop/docs/subtitles/mcdull_kung_fu_ding_ding_dong"
        # self.tst_output_suffix = "01"
        self.src_input_directory = \
            "/Users/kdebiec/Desktop/docs/subtitles/mcdull_prince_de_la_bun"
        self.tst_output_suffix = "02"

        self.n_chars = 1000
        self.tst_output_directory = \
            "/Users/kdebiec/Desktop/docs/subtitles/tst"
        self.model_infile = "/Users/kdebiec/Desktop/docs/subtitles/model.h5"
        self.n_matches = 10
        self.min_weight = 0.9

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
        src_img, src_infiles = self.load_unlabeled_data(
            self.src_input_directory)
        src_pred = model.predict(src_img)

        # Gather missing test images
        for char in self.chars[:self.n_chars]:
            tstfile = f"{self.tst_output_directory}/" \
                      f"{char}_{self.tst_output_suffix}.png"
            if char in self.skip_chars:
                if self.verbosity >= 1:
                    print(f"skipping {char}")
                continue
            elif isfile(tstfile):
                if self.verbosity >= 1:
                    print(f"'{tstfile}' already exists")
                continue

            # Identify matches
            scores = src_pred[:, self.chars_to_labels(char)]
            match_indexes = np.argsort(scores)[::-1][:self.n_matches]
            match_indexes = match_indexes[
                scores[match_indexes] > self.min_weight]
            if match_indexes.size == 0:
                if self.verbosity >= 1:
                    print(f"No matches found for {char}"
                          f"above minimum weight {self.min_weight}")
                continue

            # Generate image prompt
            image = Image.new("L", (match_indexes.size * 100, 300), 255)
            char_image = generate_char_img(char)
            image.paste(char_image, (10, 10, 90, 90))
            for i, index in enumerate(match_indexes):
                match_image = Image.open(src_infiles[index])
                image.paste(match_image, (10 + 100 * i, 110,
                                          90 + 100 * i, 190))
                draw_text_on_image(image, f"{int(scores[index]*100):2d}%",
                                   50 + 100 * i, 220)
                draw_text_on_image(image, str(i),
                                   50 + 100 * i, 270)

            # Prompt user for match
            image.show()
            while True:
                match = input(f"Enter index of image matching {char}, "
                              "or Enter to continue:")
                if match == "":
                    break
                else:
                    try:
                        if int(match) <= i:
                            infile = src_infiles[match_indexes[int(match)]]
                            if self.verbosity >= 1:
                                print(f"copying '{infile}' to '{tstfile}'")
                            copyfile(infile, tstfile)
                            break
                    except ValueError as e:
                        print(e)
                        continue

        # Interactive prompt
        if self.interactive:
            from IPython import embed

            embed()

    # endregion

    # region Properties
    @property
    def min_weight(self):
        """float: Minimum weight of matches to propose"""
        if not hasattr(self, "_min_weight"):
            self._min_weight = 0
        return self._min_weight

    @min_weight.setter
    def min_weight(self, value):
        if value is None:
            value = 0
        elif not isinstance(value, float):
            try:
                value = float(value)
            except Exception as e:
                raise ValueError()
        if not 0 <= value <= 1:
            raise ValueError()
        self._min_weight = value

    @property
    def n_matches(self):
        """int: Maximum number of matches to propose"""
        if not hasattr(self, "_n_matches"):
            self._n_matches = 10
        return self._n_matches

    @n_matches.setter
    def n_matches(self, value):
        if not isinstance(value, int) and value is not None:
            try:
                value = int(value)
            except Exception as e:
                raise ValueError()
        if value < 1 and value is not None:
            raise ValueError()
        self._n_matches = value

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
        """

        .. todo::
          - [ ] Implement caching

        Args:
            directory (str): Directory from which to load image infiles

        Returns (np.array(bool), list(str)): Images in 2-bit grayscale, infile
          paths

        """
        import numpy as np
        from glob import iglob
        from PIL import Image

        infiles = sorted(iglob(f"{directory}/*/[0-9][0-9].png"))
        imgs = []
        for infile in infiles:
            img = Image.open(infile)
            raw = np.array(img)
            imgs += [np.append(np.logical_or(raw == 85,
                                             raw == 256).flatten(),
                               np.logical_or(raw == 170,
                                             raw == 256).flatten())]
        return np.stack(imgs), infiles

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    TestDataCollector.main()
