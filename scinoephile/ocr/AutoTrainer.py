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
from scinoephile.ocr import OCRBase
from IPython import embed


################################### CLASSES ###################################
class AutoTrainer(OCRBase):
    """
    Automated machine learning model trainer
    """

    # region Builtins

    def __init__(self, n_chars=None, model=None, trn_ds=None, val_portion=None,
                 tst_ds=None, batch_size=None, epochs=None, callbacks=None,
                 **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if n_chars is not None:
            self.n_chars = n_chars

        if model is not None:
            self.model = model
        if trn_ds is not None:
            self.trn_ds = trn_ds
        if val_portion is not None:
            self.val_portion = val_portion
        if tst_ds is not None:
            self.tst_ds = tst_ds

        if batch_size is not None:
            self.batch_size = batch_size
        if epochs is not None:
            self.epochs = epochs
        if callbacks is not None:
            self.callbacks = callbacks

    def __call__(self):

        # Prepare training and validation data
        trn_img, trn_lbl, val_img, val_lbl = self.trn_ds.get_training_data(
            val_portion=self.val_portion)

        # Train model
        history = self.model.model.fit(trn_img, trn_lbl,
                                       validation_data=(val_img, val_lbl),
                                       epochs=self.epochs,
                                       batch_size=self.batch_size,
                                       callbacks=self.callbacks)

        # Evaluate model
        trn_loss, trn_acc = self.model.analyze_predictions(trn_img, trn_lbl, "Training")
        val_loss, val_acc = self.model.analyze_predictions(val_img, val_lbl, "Validation")

        # Save model
        if self.model.outfile is not None:
            self.model.save()

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
            self._callbacks = []
        return self._callbacks

    @callbacks.setter
    def callbacks(self, value):
        # TODO: Validate
        self._callbacks = value

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
    def trn_ds(self):
        """scinoephile.ocr.GeneratedOCRDataset: Training/validation dataset"""
        if not hasattr(self, "_trn_ds"):
            self._trn_ds = None
        return self._trn_ds

    @trn_ds.setter
    def trn_ds(self, value):
        from scinoephile.ocr import TrainOCRDataset

        if value is not None:
            if not isinstance(value, TrainOCRDataset):
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
        from scinoephile.ocr import TestOCRDataset

        if value is not None:
            if not isinstance(value, TestOCRDataset):
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
