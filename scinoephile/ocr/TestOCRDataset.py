#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.TestOCRDataset,py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile.ocr import OCRDataset
from IPython import embed


################################### CLASSES ###################################
class TestOCRDataset(OCRDataset):
    """
    A collection of labeled character images for testing
    """

    # region Builtins

    def __init__(self, model=None, sub_ds=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if model is not None:
            self.model = model
        if sub_ds is not None:
            self.sub_ds = sub_ds

    # endregion

    # region Public Properties

    @property
    def model(self):
        """scinoephile.ocr.Model: model"""
        if not hasattr(self, "_model"):
            self._model = None
        return self._model

    @model.setter
    def model(self, value):
        from scinoephile.ocr import Model

        if value is not None:
            if not isinstance(value, Model):
                raise ValueError(self._generate_setter_exception(value))
        self._model = value

    @property
    def spec_cols(self):
        """list(str): Character image specification columns"""
        return ["char", "source", "indexes"]

    @property
    def spec_dtypes(self):
        """list(str): Character image specification dtypes"""
        return {"char": str, "source": str, "sub index": int,
                "char index": int}

    @property
    def sub_ds(self):
        """scinoephile.ocr.ImageSubtitleSeries: Source subtitles"""
        if not hasattr(self, "_sub_ds"):
            self._sub_ds = None
        return self._sub_ds

    @sub_ds.setter
    def sub_ds(self, value):
        from scinoephile.ocr import ImageSubtitleSeries

        if value is not None:
            if not isinstance(value, ImageSubtitleSeries):
                raise ValueError(self._generate_setter_exception(value))
        self._sub_ds = value

    # endregion

    # region Public Methods

    def calculate_diff(self, trn_ds):
        raise NotImplementedError()

        # import numpy as np
        #
        # for char in self.get_present_chars()[:self.n_chars]:
        #     print(char)
        #     tst_spec = self.get_present_specs_of_char(char)
        #     trn_spec = trn_ds.get_present_specs_of_char(char)
        #     tst_data = self.data[tst_spec.index.values]
        #     trn_data = trn_ds.data[trn_spec.index.values]
        #     diff = trn_data.astype(np.float32) - tst_data
        #     diff = np.power(diff, 2)
        #     trn_spec["rmse"] = np.sqrt(np.mean(diff, axis=(1, 2)))
        #     diff = np.sqrt(diff)
        #     trn_spec["mae"] = np.mean(diff, axis=(1, 2))
        #
        #     embed(**self.embed_kw)

    def get_present_chars(self):
        return sorted(list(self.get_present_chars_set()),
                      key=self.get_labels_of_chars)

    def get_present_chars_set(self):
        return set(self.spec["char"])

    def get_present_specs_of_char(self, char, source=None):
        if source is None:
            return self.spec.loc[
                self.spec["char"] == char].drop("char", axis=1)
        else:
            return self.spec.loc[
                self.spec["char"] == char].drop("char", axis=1)[
                self.spec["source"] == source].drop("source", axis=1)

    def get_present_specs_of_char_set(self, char, **kwargs):
        return set(map(tuple,
                       self.get_present_specs_of_char(char, **kwargs).values))

    def label_test_data(self, sub_ds=None, model=None):
        import numpy as np
        import pandas as pd
        from PIL import Image
        from scinoephile.ocr import draw_text_on_img, generate_char_datum

        # Process arguments
        if sub_ds is None:
            sub_ds = self.sub_ds
        if model is None:
            model = self.model
        source = sub_ds.infile

        spec = []
        indexes = []
        to_dict = lambda x: {k: v for k, v in zip(self.spec_cols, (char, *x))}

        predictions = model.model.predict(sub_ds.char_data)
        for char in self.chars[:self.n_chars]:

            if len(self.get_present_specs_of_char_set(char, source)) > 0:
                continue

            # Identify best matches for this char
            scores = predictions[:, self.get_labels_of_chars(char)]
            best_match_indexes = np.argsort(scores)[::-1][:10]

            # Generate prompt
            if self.mode == "8 bit":
                full_img = Image.new("L", (1000, 250), 255)
                target_img = Image.fromarray(
                    generate_char_datum(char=char, fig=self.figure,
                                        mode=self.mode))
            elif self.mode == "1 bit":
                full_img = Image.new("1", (1000, 250), 1)
                target_img = Image.fromarray(
                    generate_char_datum(char=char, fig=self.figure,
                                        mode=self.mode).astype(np.uint8) * 255)
            full_img.paste(target_img, (10, 10, 90, 90))
            for i, index in enumerate(best_match_indexes, 1):
                if self.mode == "8 bit":
                    match_image = Image.fromarray(sub_ds.char_data[index])
                elif self.mode == "1 bit":
                    match_image = Image.fromarray(
                        sub_ds.char_data[index].astype(np.uint8) * 255)
                full_img.paste(match_image, (10 + 100 * (i - 1), 110,
                                             90 + 100 * (i - 1), 190))
                draw_text_on_img(full_img, str(i % 10),
                                 50 + 100 * (i - 1), 220)

            # Prompt user for match
            full_img.show()
            while True:
                match = input(f"Enter index of image matching {char}, "
                              "or Enter to continue:")
                if match == "":
                    break
                else:
                    try:
                        if int(match) == 0:
                            index = best_match_indexes[9]
                        elif int(match) <= 9:
                            index = best_match_indexes[int(match) - 1]
                        else:
                            raise ValueError()

                        spec.append(to_dict(
                            (source, *sub_ds.get_subchar_indexes_of_char_indexes(index))))
                        indexes.append(index)
                        break
                    except ValueError as e:
                        print(e)
                        continue

        if self.verbosity >= 1:
            print(f"Adding {len(indexes)} new test images")
        spec = pd.DataFrame(spec)
        data = self.sub_ds.char_data[indexes]
        self.add_img(spec, data)

    # endregion

    # region Private Methods

    def _load_hdf5(self, fp, **kwargs):
        import pandas as pd
        import numpy as np

        decode = lambda x: x.decode("utf8")

        # Load image mode
        if "mode" not in fp.attrs:
            return
        self.mode = fp.attrs["mode"]

        # Load image specs
        if "spec" not in fp:
            raise ValueError()  # Weird to have mode but no specs or data
        spec = np.array(fp["spec"])
        spec = pd.DataFrame(data=spec, index=range(spec.size), columns=spec.dtype.names)
        spec["char"] = spec["char"].apply(decode)
        spec["source"] = spec["source"].apply(decode)

        # Load image data
        if "data" not in fp:
            raise ValueError()  # Weirder to have mode and specs but no data
        data = np.array(fp["data"])

        self.add_img(spec, data)

    def _save_hdf5(self, fp, **kwargs):
        import numpy as np

        dtypes = [("char", "S3"),
                  ("source", "S255"),
                  ("sub index", "i2"),
                  ("char index", "i2")]
        encode = lambda x: x.encode("utf8")

        # Save image mode
        fp.attrs["mode"] = self.mode

        # Save image specs
        if "spec" in fp:
            del fp["spec"]
        encoded = self.spec.copy()
        encoded["char"] = encoded["char"].apply(encode)
        encoded["source"] = encoded["source"].apply(encode)
        encoded = np.array(list(map(tuple, list(encoded.values))), dtype=dtypes)
        fp.create_dataset("spec",
                          data=encoded,
                          dtype=dtypes,
                          chunks=True,
                          compression="gzip")

        # Save image data
        if "data" in fp:
            del fp["data"]
        fp.create_dataset("data",
                          data=self.data,
                          dtype=self.data_dtype,
                          chunks=True,
                          compression="gzip")

    # endregion
