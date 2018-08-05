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
        import tensorflow as tf
        from tensorflow import keras
        from IPython import embed

        self.trn_input_directory = "/Users/kdebiec/Desktop/docs/subtitles/trn"
        self.val_input_directory = "/Users/kdebiec/Desktop/docs/subtitles/val"
        self.tst_input_directory = "/Users/kdebiec/Desktop/docs/subtitles/tst"

        # Load and organize data
        trn_img, trn_lbl = self.load_data(self.trn_input_directory)
        val_img, val_lbl = self.load_data(self.val_input_directory)
        tst_img, tst_lbl = self.load_data(self.tst_input_directory)

        # Define model
        model = keras.Sequential([
            keras.layers.Flatten(input_shape=(80, 80)),
            keras.layers.Dense(128, activation=tf.nn.relu),
            keras.layers.Dense(128, activation=tf.nn.relu),
            keras.layers.Dense(21, activation=tf.nn.softmax)
        ])
        model.compile(optimizer=tf.train.AdamOptimizer(),
                      loss='sparse_categorical_crossentropy',
                      metrics=['accuracy'])

        # Train model
        model.fit(trn_img, trn_lbl, epochs=10)

        # Evaluate model
        trn_pred = model.predict(trn_img)
        trn_loss, trn_acc = model.evaluate(trn_img, trn_lbl)
        val_pred = model.predict(tst_img)
        val_loss, val_acc = model.evaluate(val_img, val_lbl)
        tst_pred = model.predict(tst_img)
        tst_loss, tst_acc = model.evaluate(tst_img, tst_lbl)
        print(f"Training    Loss:{trn_loss:7.5f} Accuracy:{trn_acc:7.5f}:")
        print(f"Validation  Loss:{val_loss:7.5f} Accuracy:{val_acc:7.5f}:")
        print(f"Test        Loss:{tst_loss:7.5f} Accuracy:{tst_acc:7.5f}:")

        embed()

    # endregion

    # region Properties
    @property
    def chars(self):
        """pandas.core.frame.DataFrame: Characters"""
        if not hasattr(self, "_chars"):
            import numpy as np

            self._chars = np.array(self.char_frequency_table["character"],
                                   np.str)
        return self._chars

    @property
    def char_frequency_table(self):
        """pandas.core.frame.DataFrame: Character frequency table"""
        if not hasattr(self, "_char_frequency_table"):
            import pandas as pd

            self._char_frequency_table = pd.read_csv(
                f"{self.directory}/data/ocr/characters.txt", sep="\t",
                names=["character", "frequency", "cumulative frequency"])
        return self._char_frequency_table

    @property
    def trn_input_directory(self):
        """str: Path to directory containing training character images"""
        if not hasattr(self, "_trn_input_directory"):
            self._trn_input_directory = None
        return self._trn_input_directory

    @trn_input_directory.setter
    def trn_input_directory(self, value):
        from os.path import expandvars, isdir

        if not isinstance(value, str) and value is not None:
            raise ValueError()
        elif isinstance(value, str):
            value = expandvars(value)
            if not isdir(value):
                raise ValueError()
        self._trn_input_directory = value

    @property
    def tst_input_directory(self):
        """str: Path to directory containing test character images"""
        if not hasattr(self, "_trn_input_directory"):
            self._tst_input_directory = None
        return self._tst_input_directory

    @tst_input_directory.setter
    def tst_input_directory(self, value):
        from os.path import expandvars, isdir

        if not isinstance(value, str) and value is not None:
            raise ValueError()
        elif isinstance(value, str):
            value = expandvars(value)
            if not isdir(value):
                raise ValueError()
        self._tst_input_directory = value

    @property
    def val_input_directory(self):
        """str: Path to directory containing validation character images"""
        if not hasattr(self, "_val_input_directory"):
            self._val_input_directory = None
        return self._val_input_directory

    @val_input_directory.setter
    def val_input_directory(self, value):
        from os.path import expandvars, isdir

        if not isinstance(value, str) and value is not None:
            raise ValueError()
        elif isinstance(value, str):
            value = expandvars(value)
            if not isdir(value):
                raise ValueError()
        self._val_input_directory = value

    # endregion

    # region Methods
    def load_data(self, directory):
        import numpy as np
        from glob import iglob
        from PIL import Image
        from os.path import basename

        imgs, lbls = [], []
        for infile in iglob(f"{directory}/*.png"):
            img = Image.open(infile)
            imgs += [np.array(img, np.float32) / 255]
            lbls += [np.argwhere(self.chars == basename(infile)[0])[0]]

        return np.stack(imgs), np.array(lbls, np.int16)
    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    Trainer.main()
