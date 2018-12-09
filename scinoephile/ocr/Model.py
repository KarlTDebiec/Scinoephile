#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.Model.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile import DatasetBase
from scinoephile.ocr import OCRBase
from IPython import embed


################################### CLASSES ###################################
class Model(OCRBase, DatasetBase):
    """
    Machine learning model
    """

    # region Builtins

    def __init__(self, n_chars=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if n_chars is not None:
            self.n_chars = n_chars

    # endregion

    # region Public Properties

    @property
    def model(self):
        if not hasattr(self, "_model"):
            self._model = None
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @property
    def n_chars(self):
        """int: Number of unique characters to support"""
        if not hasattr(self, "_n_chars"):
            self._n_chars = 25
        return self._n_chars

    @n_chars.setter
    def n_chars(self, value):
        if value is not None:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except Exception as e:
                    raise ValueError(self._generate_setter_exception(value))
            if value < 1:
                raise ValueError(self._generate_setter_exception(value))
        self._n_chars = value

    # endregion

    # region Public Methods

    def analyze_predictions(self, img, lbl, title=""):
        import numpy as np

        pred = self.model.predict(img)
        loss, acc = self.model.evaluate(img, lbl)
        if self.verbosity >= 1:
            print(f"{title:10s}  Count:{lbl.size:5d}  Loss:{loss:7.5f} "
                  f"Accuracy:{acc:7.5f}")
        for i, char in enumerate(self.get_chars_of_labels(lbl)):
            poss_lbls = np.argsort(pred[i])[::-1]
            poss_chars = self.get_chars_of_labels(poss_lbls)
            poss_probs = np.round(pred[i][poss_lbls], 2)
            if char != poss_chars[0]:
                if self.verbosity >= 2:
                    matches = [f"{a}:{b:4.2f}" for a, b in
                               zip(poss_chars[:10], poss_probs[:10])]
                    print(f"{char} | {' '.join(matches)}")

        return loss, acc

    def build(self):
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Dense, Dropout, Flatten

        self.model = Sequential()
        self.model.add(Flatten())
        self.model.add(Dense(512, input_shape=(6400,), activation="relu"))
        self.model.add(Dropout(0.2))
        self.model.add(Dense(512, activation="relu"))
        self.model.add(Dropout(0.2))
        self.model.add(Dense(self.n_chars, activation="softmax"))

    def compile(self):
        from tensorflow.keras.optimizers import Adam, RMSprop

        self.model.compile(
            optimizer=Adam(),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"])

    def load(self, infile=None):
        from os.path import expandvars
        from tensorflow import keras

        # Process arguments
        if infile is not None:
            infile = expandvars(infile)
        elif self.infile is not None:
            infile = self.infile
        else:
            raise ValueError()

        # Read infile
        if self.verbosity >= 1:
            print(f"Reading model from '{infile}'")
        self.model = keras.models.load_model(infile)

    def save(self, outfile=None):
        from os.path import expandvars

        # Process arguments
        if outfile is not None:
            outfile = expandvars(outfile)
        elif self.outfile is not None:
            outfile = self.outfile
        else:
            raise ValueError()

        # Write outfile
        if self.verbosity >= 1:
            print(f"Saving model to {outfile}")
        self.model.save(outfile)

    # endregion
