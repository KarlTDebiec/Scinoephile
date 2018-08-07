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
from zysyzm.ocr import OCRCLToolBase


################################### CLASSES ###################################
class ModelTrainer(OCRCLToolBase):
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
        import tensorflow as tf
        from tensorflow import keras

        self.trn_input_directory = "/Users/kdebiec/Desktop/docs/subtitles/trn"
        self.val_input_directory = "/Users/kdebiec/Desktop/docs/subtitles/val"
        self.tst_input_directory = "/Users/kdebiec/Desktop/docs/subtitles/tst"

        # Load and organize data
        trn_img, trn_lbl = self.load_data(self.trn_input_directory)
        val_img, val_lbl = self.load_data(self.val_input_directory)
        tst_img, tst_lbl = self.load_data(self.tst_input_directory)
        n_possible_chars = trn_lbl.max() + 1

        # Define model
        # keras.layers.Flatten(input_shape=(80, 80)),
        model = keras.Sequential([
            keras.layers.Dense(128, activation=tf.nn.relu),
            keras.layers.Dense(128, activation=tf.nn.relu),
            keras.layers.Dense(n_possible_chars, activation=tf.nn.softmax)
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
        print(f"Training    Count:{trn_lbl.size:5d} Loss:{trn_loss:7.5f} Accuracy:{trn_acc:7.5f}")
        print(f"Validation  Count:{val_lbl.size:5d} Loss:{val_loss:7.5f} Accuracy:{val_acc:7.5f}")
        print(f"Test        Count:{tst_lbl.size:5d} Loss:{tst_loss:7.5f} Accuracy:{tst_acc:7.5f}")
        for i, char in enumerate(self.labels_to_chars(tst_lbl)):
            tst_poss = np.where(tst_pred[i] > 0.1)[0]
            tst_poss_char = self.labels_to_chars(tst_poss)
            if char == tst_poss_char[0] and tst_poss.size == 1:
                continue
            tst_poss_char = self.labels_to_chars(tst_poss)
            tst_poss_prob = np.round(tst_pred[i][tst_poss], 2)
            print(f"{char} | {' '.join([f'{a}:{b:4.2f}' for a, b in zip(tst_poss_char, tst_poss_prob)])}")

        # Interactive prompt
        if self.interactive:
            from IPython import embed
            embed()

    # endregion

    # region Properties
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
            # imgs += [np.array(img, np.float32) / 255]
            raw = np.array(img)
            imgs += [np.append(np.logical_or(raw == 85, raw == 256).flatten(),
                               np.logical_or(raw == 170, raw == 256).flatten())]
            lbls += [np.argwhere(self.chars == basename(infile)[0])[0, 0]]

        return np.stack(imgs), np.array(lbls, np.int16)

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    ModelTrainer.main()
