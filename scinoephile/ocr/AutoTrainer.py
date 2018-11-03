#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.AutoTrainer.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile.ocr import OCRCLToolBase
from IPython import embed
from sys import exit


################################### CLASSES ###################################
class AutoTrainer(OCRCLToolBase):
    """
    Automated machine learning model trainer
    """

    # region Builtins

    def __init__(self, n_chars=None, model_infile=None, trn_ds=None,
                 val_portion=None, tst_ds=None, shape=None, batch_size=None,
                 epochs=None, model_outfile=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if n_chars is not None:
            self.n_chars = n_chars

        if model_infile is not None:
            self.model_infile = model_infile

        if trn_ds is not None:
            self.trn_ds = trn_ds
        if val_portion is not None:
            self.val_portion = val_portion
        if tst_ds is not None:
            self.tst_ds = tst_ds

        if shape is not None:
            self.shape = shape
        if batch_size is not None:
            self.batch_size = batch_size
        if epochs is not None:
            self.epochs = epochs

        if model_outfile is not None:
            self.model_outfile = model_outfile

    def __call__(self):
        from tensorflow import keras

        # Prepare model
        if self.model_infile is not None:
            self.model = keras.models.load_model(self.model_infile)
        self.prepare_model()

        # Prepare training and validation data
        trn_img, trn_lbl, val_img, val_lbl = self.trn_ds.get_training_data(
            val_portion=self.val_portion)

        # Training Loop
        round = 1
        while True:
            if self.verbosity >= 1:
                print(f"Round {round}")

            # Train model
            history = self.model.fit(trn_img, trn_lbl,
                                     validation_data=(val_img, val_lbl),
                                     epochs=self.epochs,
                                     batch_size=self.batch_size,
                                     callbacks=self.callbacks)
            round += 1

            # Evaluate model
            self.analyze_image_predictions("Training", trn_img, trn_lbl)
            self.analyze_image_predictions("Validation", val_img, val_lbl)

            # Save model
            if self.model_outfile is not None:
                if self.verbosity >= 1:
                    print(f"Saving model to {self.model_outfile}")
                self.model.save(self.model_outfile)

            # Quit
            if round > 10:
                break

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
    def model_infile(self):
        """str: Path to input model file"""
        if not hasattr(self, "_model_infile"):
            self._model_infile = None
        return self._model_infile

    @model_infile.setter
    def model_infile(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._model_infile = value

    @property
    def model_outfile(self):
        """str: Path to output model file"""
        if not hasattr(self, "_model_outfile"):
            self._model_outfile = None
        return self._model_outfile

    @model_outfile.setter
    def model_outfile(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._model_outfile = value

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

    @property
    def trn_ds(self):
        """scinoephile.ocr.GeneratedOCRDataset: Training/validation dataset"""
        if not hasattr(self, "_trn_ds"):
            self._trn_ds = None
        return self._trn_ds

    @trn_ds.setter
    def trn_ds(self, value):
        from scinoephile.ocr import GeneratedOCRDataset

        if value is not None:
            if not isinstance(value, GeneratedOCRDataset):
                raise ValueError(self._generate_setter_exception(value))
        self._trn_ds = value

    @property
    def tst_ds(self):
        """scinoephile.ocr.GeneratedOCRDataset: Test dataset"""
        if not hasattr(self, "_tst_ds"):
            self._tst_ds = None
        return self._tst_ds

    @tst_ds.setter
    def tst_ds(self, value):
        from scinoephile.ocr import LabeledOCRDataset

        if value is not None:
            if not isinstance(value, LabeledOCRDataset):
                raise ValueError(self._generate_setter_exception(value))
        self._tst_ds = value

    @property
    def val_portion(self):
        """float: Portion of training image to set aside for validation"""
        if not hasattr(self, "_val_portion"):
            self._val_portion = 0.1
        return self._val_portion

    @val_portion.setter
    def val_portion(self, value):
        if value is not None:
            if not isinstance(value, float):
                try:
                    value = float(value)
                except Exception as e:
                    raise ValueError(self._generate_setter_exception(value))
            if value == 0:
                value = None
            elif not 0 < value < 1:
                raise ValueError(self._generate_setter_exception(value))
        self._val_portion = value

    # endregion

    # region Public Methods

    def analyze_image_predictions(self, title, img, lbl):
        import numpy as np

        pred = self.model.predict(img)
        loss, acc = self.model.evaluate(img, lbl)
        if self.verbosity >= 1:
            print(f"{title:10s}  Count:{lbl.size:5d}  Loss:{loss:7.5f} "
                  f"Accuracy:{acc:7.5f}")
        for i, char in enumerate(self.labels_to_chars(lbl)):
            poss_lbls = np.argsort(pred[i])[::-1]
            poss_chars = self.labels_to_chars(poss_lbls)
            poss_probs = np.round(pred[i][poss_lbls], 2)
            if char != poss_chars[0]:
                if self.verbosity >= 2:
                    matches = [f"{a}:{b:4.2f}" for a, b in
                               zip(poss_chars[:10], poss_probs[:10])]
                    print(f"{char} | {' '.join(matches)}")

    def prepare_model(self):
        from tensorflow.keras.optimizers import Adam, RMSprop

        if self.model is None:
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import Dense, Dropout, Flatten

            self.model = Sequential()
            self.model.add(Flatten())
            self.model.add(Dense(96, input_shape=(6400,), activation="relu"))
            self.model.add(Dropout(0.2))
            # self.model.add(Dense(32, activation="relu"))
            # self.model.add(Dropout(0.2))
            self.model.add(Dense(self.n_chars, activation="softmax"))
        self.model.compile(
            optimizer=Adam(),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"])
        #   optimizer=tf.train.AdamOptimizer(),
        #   loss="sparse_categorical_crossentropy",

    # endregion
