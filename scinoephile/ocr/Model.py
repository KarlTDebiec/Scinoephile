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
from scinoephile.ocr import OCRCLToolBase
from IPython import embed


################################### CLASSES ###################################
class Model(OCRCLToolBase):
    """
    Machine learning model
    """

    # region Builtins

    def __init__(self, n_chars=None, infile=None, shape=None, batch_size=None,
                 epochs=None, outfile=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if n_chars is not None:
            self.n_chars = n_chars

        if infile is not None:
            self.infile = infile

        if shape is not None:
            self.shape = shape
        if batch_size is not None:
            self.batch_size = batch_size
        if epochs is not None:
            self.epochs = epochs

        if outfile is not None:
            self.outfile = outfile

    def __call__(self):

        # Input and preparation
        if self.infile is not None:
            self.load()
        self.prepare_model()

        # Output
        if self.outfile is not None:
            self.save()

        # Present IPython prompt
        if self.interactive:
            embed(**self.embed_kw)

    # endregion

    # region Public Properties

    @property
    def batch_size(self):
        """int: Training batch size"""
        if not hasattr(self, "_batch_size"):
            self._batch_size = 32
        return self._batch_size

    @batch_size.setter
    def batch_size(self, value):
        if value is not None:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except Exception as e:
                    raise ValueError(self._generate_setter_exception(value))
            if value < 1 and value is not None:
                raise ValueError(self._generate_setter_exception(value))
        self._batch_size = value

    @property
    def callbacks(self):
        if not hasattr(self, "_callbacks"):
            from tensorflow.keras.callbacks import (EarlyStopping,
                                                    ReduceLROnPlateau)

            self._callbacks = []
            # keras.callbacks.EarlyStopping(monitor="val_loss",
            #                               min_delta=0.001,
            #                               patience=10),
            # keras.callbacks.ReduceLROnPlateau(monitor="acc",
            #                                   patience=3,
            #                                   verbose=1,
            #                                   factor=0.1,
            #                                   min_lr=0.000000001)]
        return self._callbacks

    @property
    def epochs(self):
        """int: Number of epochs to train for"""
        if not hasattr(self, "_epochs"):
            self._epochs = 100
        return self._epochs

    @epochs.setter
    def epochs(self, value):
        if value is not None:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except Exception as e:
                    raise ValueError(self._generate_setter_exception(value))
            if value < 1 and value is not None:
                raise ValueError(self._generate_setter_exception(value))
        self._epochs = value

    @property
    def model(self):
        if not hasattr(self, "_model"):
            self._model = None
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @property
    def infile(self):
        """str: Path to input model file"""
        if not hasattr(self, "_infile"):
            self._infile = None
        return self._infile

    @infile.setter
    def infile(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._infile = value

    @property
    def outfile(self):
        """str: Path to output model file"""
        if not hasattr(self, "_outfile"):
            self._outfile = None
        return self._outfile

    @outfile.setter
    def outfile(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._outfile = value

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

    @property
    def shape(self):
        """list(int): Shape of model"""
        if not hasattr(self, "_shape"):
            self._shape = [128, 128, 128]
        return self._shape

    @shape.setter
    def shape(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise ValueError(self._generate_setter_exception(value))
            elif isinstance(value, list):
                for i, v in enumerate(value):
                    try:
                        value[i] = int(v)
                    except Exception as e:
                        raise ValueError(self._generate_setter_exception(value))
        self._shape = value

    # endregion

    # region Public Methods

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

    def prepare_model(self):
        from tensorflow.keras.optimizers import Adam, RMSprop

        if self.model is None:
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import Dense, Dropout, Flatten

            self.model = Sequential()
            self.model.add(Flatten())
            self.model.add(Dense(512, input_shape=(6400,), activation="relu"))
            self.model.add(Dropout(0.2))
            self.model.add(Dense(512, activation="relu"))
            self.model.add(Dropout(0.2))
            self.model.add(Dense(self.n_chars, activation="softmax"))
        self.model.compile(
            optimizer=Adam(),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"])
        #   optimizer=tf.train.AdamOptimizer(),
        #   loss="sparse_categorical_crossentropy",

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
            print(f"Saving model to {self.model_outfile}")
        self.model.save(self.model_outfile)

    # endregion
