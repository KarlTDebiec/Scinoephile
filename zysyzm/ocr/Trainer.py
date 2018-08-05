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
        import numpy as np
        import matplotlib.pyplot as plt
        import tensorflow as tf
        from tensorflow import keras
        from IPython import embed
        print(tf.__version__)

        self.trn_input_directory = "/Users/kdebiec/Desktop/docs/subtitles/trn"
        self.tst_input_directory = "/Users/kdebiec/Desktop/docs/subtitles/tst"

        # Load and organize data
        trn_img, trn_lbl = self.load_data(self.trn_input_directory)
        tst_img, tst_lbl = self.load_data(self.tst_input_directory)

        # Define model
        model = keras.Sequential([
            keras.layers.Flatten(input_shape=(80, 80)),
            keras.layers.Dense(128, activation=tf.nn.relu),
            keras.layers.Dense(128, activation=tf.nn.relu),
            keras.layers.Dense(6, activation=tf.nn.softmax)
        ])
        model.compile(optimizer=tf.train.AdamOptimizer(),
                      loss='sparse_categorical_crossentropy',
                      metrics=['accuracy'])

        # Train model
        model.fit(trn_img, trn_lbl, epochs=10)

        # Evaluate model
        predictions = model.predict(tst_img)
        test_loss, test_acc = model.evaluate(tst_img, tst_lbl)
        print('Test accuracy:', test_acc)

        embed()

    # endregion

    # region Properties
    @property
    def chars(self):
        """List(str): List of characters"""
        return ["的", "一", "是", "不", "了", "在"]

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
            lbls += [self.chars.index(basename(infile)[0])]

        return np.stack(imgs), np.array(lbls, np.int8)

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    Trainer.main()
