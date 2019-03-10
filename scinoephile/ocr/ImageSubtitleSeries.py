#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.ImageSubtitleSeries.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import numpy as np
import pandas as pd
from scinoephile import SubtitleSeries
from scinoephile.ocr import ImageSubtitleEvent, OCRBase
from IPython import embed


################################### CLASSES ###################################
class ImageSubtitleSeries(SubtitleSeries, OCRBase):
    """
    A series of image-based subtitles
    """

    # region Class Attributes

    event_class = ImageSubtitleEvent

    # endregion

    # region Public Properties

    @property
    def char_predictions(self):
        """ndarray(float): Predicted confidence that each character image is
        each matchable character"""
        if not hasattr(self, "_char_predictions"):
            self._char_predictions = None
        return self._char_predictions

    @char_predictions.setter
    def char_predictions(self, value):
        if not isinstance(value, np.ndarray):
            raise ValueError(self._generate_setter_exception(value))
        if value.shape[0] != self.data.shape[0]:
            raise ValueError(self._generate_setter_exception(value))
        self._char_predictions = value

    @property
    def data(self):
        """ndarray: Dedupulicated character image data collected from all
        subtitles"""
        if not hasattr(self, "_data"):
            self._initialize_char_data()
        return self._data

    @property
    def spec(self):
        """DataFrame: Specifications describing each character image"""
        if not hasattr(self, "_spec"):
            self._initialize_char_data()
        return self._spec

    @property
    def data_dtype(self):
        """type: dtype of image data"""
        if self.mode == "8 bit":
            return np.uint8
        elif self.mode == "1 bit":
            return np.bool
        else:
            raise NotImplementedError()

    @property
    def spec_dtypes(self):
        """list(str): dtypes of columns in spec"""
        from collections import OrderedDict

        return OrderedDict(char=str, indexes=object)

    # endregion

    # region Public Methods

    def assign_char(self, index, char):
        if self.spec.loc[index].char != char:
            if self.verbosity >= 2:
                print(f"Assigning character {index} as '{char}'")
            self.spec.loc[index].char = char

    def calculate_accuracy(self, infile, n_chars, assign=True):
        """
        Calculates accuracy of predicted text relative to known standard

        Arguments:
            infile (str): Path to standard infile
            n_chars (int): Number of matchable characters
        """
        standard = SubtitleSeries.load(infile)
        n_correct = 0
        n_total = 0
        n_correct_matchable = 0
        n_total_matchable = 0

        # Loop over events
        event_pairs = zip([e.text for e in self.events[:len(standard.events)]],
                          [e.text for e in standard.events])
        for i, (pred_text, true_text) in enumerate(event_pairs):
            pred_text = pred_text.replace("　", "").replace(" ", "")
            true_text = true_text.replace("　", "").replace(" ", "")
            true_text = true_text.replace("…", "...")

            # Determine labels of true characters
            try:
                true_labels = self.get_labels_of_chars(true_text)
            except IndexError:
                true_labels = []
                for true_char in true_text:
                    try:
                        true_labels.append(self.get_labels_of_chars(true_char))
                    except:
                        true_labels.append(-1)

            # Loop over characters
            char_pairs = zip(pred_text, true_text, true_labels)
            for j, (pred_char, true_char, true_label) in enumerate(char_pairs):
                n_total += 1
                if pred_char == true_char:
                    n_correct += 1
                    if assign:
                        self.assign_char(self.events[i].char_indexes[j],
                                         pred_char)
                if 0 <= true_label and true_label < n_chars:
                    n_total_matchable += 1
                    if pred_char == true_char:
                        n_correct_matchable += 1
        print(f"{n_correct} out of {n_total} characters correct "
              f"(accuracy = {n_correct / n_total:6.4})")
        print(f"{n_correct_matchable} out of {n_total_matchable} matchable "
              f"characters correct "
              f"(accuracy = {n_correct_matchable / n_total_matchable:6.4f})")

    def get_char_index_of_subchar_index(self, sub_index, char_index):
        return None

    def get_subchar_indexes_of_char_index(self, index):
        return self.spec.loc[index].indexes

    def manually_assign_chars(self, start_index=0):
        from pypinyin import pinyin

        predictions = self.get_chars_of_labels(
            np.argsort(self.char_predictions, axis=1)[:, -1])

        if self.verbosity >= 1:
            print("Assigning characters")
            print("  Press Enter to accept predicted character")
            print("  or type another character and press Enter to correct")
            print("  or press CTRL-D to skip character")
            print("  or press CTRL-C to stop assigning")
            print()
        for i, spec in self.spec.iterrows():
            if spec.char != "":
                print(f"Character {i} previously assigned as '{spec.char}' "
                      f"({pinyin(spec.char)[0][0]})")
                continue
            if i <= start_index:
                print(f"Skipping assignment of character {i}")
                continue

            self.show(indexes=i)

            try:
                match = input(f"'{predictions[i]}' "
                              f"({pinyin(predictions[i])[0][0]}): ")
            except EOFError:
                print(f"\nSkipping assignment of character {i}")
                continue
            except KeyboardInterrupt:
                print("\nQuitting character assignment")
                break
            if match == "":
                self.assign_char(i, predictions[i])
            else:
                self.assign_char(i, match)

        embed(**self.embed_kw)

    def predict(self, model):
        """
        Predicts confidence that each character image is each matchable
        chararcter

        Stores results in both this series' char_predictions and in each
        event's char_predictions

        Arguments:
            model(model?): TensorFlow model with which to predict characters
        """
        dtypes = [("series char index", "i8"),
                  ("subtitle index", "i8"),
                  ("subtitle char index", "i8")]

        # Make predictions
        self.char_predictions = model.model.predict(self.data)

        # Store predictions in each event
        # TODO: Confirm that char_predictions are references
        char_indexes = pd.DataFrame([(i, j, k)
                                     for i, s in self.spec.iterrows()
                                     for j, k in s["indexes"]],
                                    columns=[d[0] for d in dtypes])
        for i, event in enumerate(self.events):
            event_indexes = char_indexes[
                char_indexes["subtitle index"] == i].sort_values(
                "subtitle char index")["series char index"].values
            event.char_predictions = self.char_predictions[event_indexes]

    def reconstruct_text(self):
        """
        Reconstructs text for each subtitle
        """
        for event in self.events:
            event.reconstruct_text()

    def save(self, outfile, format=None, **kwargs):
        """
        Saves subtitles to an output file

        pysubs2.SSAFile.save expects an open text file, so we open the hdf5
        file here for consistency.
        """
        from pysubs2 import SSAFile
        from os.path import expandvars

        # Process arguments
        if outfile is not None:
            outfile = expandvars(outfile)
        elif self.outfile is not None:
            outfile = self.outfile
        else:
            raise ValueError()
        if self.verbosity >= 1:
            print(f"Writing subtitles to '{outfile}'")

        # Check if hdf5
        if (format == "hdf5" or outfile.endswith(".hdf5")
                or outfile.endswith(".h5")):
            import h5py

            with h5py.File(outfile) as fp:
                self._save_hdf5(fp, **kwargs)
        # Check if directory
        elif (format == "png" or outfile.endswith("/")):
            self._save_png(outfile, **kwargs)
        # Otherwise, continue as superclass SSAFile
        else:
            SSAFile.save(self, outfile, format_=format, **kwargs)

    def show(self, data=None, indexes=None, cols=20):
        from imgcat import imgcat
        from PIL import Image

        # Process arguments
        if data is None and indexes is None:
            data = self.data
            indexes = range(self.data.shape[0])
        elif data is None and indexes is not None:
            data = self.data
        elif data is not None and indexes is None:
            indexes = range(data.shape[0])
        if isinstance(indexes, int):
            indexes = [indexes]
        indexes = np.array(indexes, np.int)
        if np.any(indexes >= data.shape[0]):
            raise ValueError()
        if cols is None:
            cols = indexes.size
            rows = 1
        else:
            rows = int(np.ceil(indexes.size / cols))
        cols = min(cols, indexes.size)

        # Draw image
        if self.mode == "8 bit":
            img = Image.new("L", (cols * 100, rows * 100), 255)
        elif self.mode == "1 bit":
            img = Image.new("1", (cols * 100, rows * 100), 1)
        for i, index in enumerate(indexes):
            column = (i // cols)
            row = i - (column * cols)
            if self.mode == "8 bit":
                char_img = Image.fromarray(data[index])
            elif self.mode == "1 bit":
                char_img = Image.fromarray(
                    data[index].astype(np.uint8) * 255)
            img.paste(char_img, (100 * row + 10,
                                 100 * column + 10,
                                 100 * (row + 1) - 10,
                                 100 * (column + 1) - 10))
        imgcat(img)

    # endregion

    # region Public Class Methods

    @classmethod
    def load(cls, infile, encoding="utf-8", mode="8 bit", verbosity=1,
             **kwargs):
        """
        SSAFile.from_file expects an open text file, so we open hdf5 here
        """
        from os.path import expandvars

        # Process arguments
        if infile is not None:
            infile = expandvars(infile)
        else:
            raise ValueError()
        if verbosity >= 1:
            print(f"Reading subtitles from '{infile}'")

        # Check if hdf5
        if (encoding == "hdf5" or infile.endswith(".hdf5")
                or infile.endswith(".h5")):
            import h5py

            with h5py.File(infile) as fp:
                return cls._load_hdf5(fp, mode=mode, verbosity=verbosity,
                                      **kwargs)
        # Check if sup
        if encoding == "sup" or infile.endswith("sup"):
            with open(infile, "rb") as fp:
                return cls._load_sup(fp, mode=mode, verbosity=verbosity,
                                     **kwargs)
        # Other formats not supported for this class
        else:
            raise ValueError()

    # endregion

    # region Private Methods

    def _initialize_char_data(self):
        """
        Initializes deduplicated character image data structure
        """
        if self.verbosity >= 1:
            print("Initializing character data structures")

        n_total_chars = sum([e.char_count for e in self.events])
        n_checked_chars = 0
        n_unique_chars = 0
        data = np.zeros((n_total_chars, 80, 80), np.uint8)
        subchar_indexes = []

        # Loop over events, then over chars within event, and skip duplicates
        for i, event in enumerate(self.events):
            if self.verbosity >= 2:
                print(f"Analyzing characters for event "
                      f"{i + 1}/{len(self.events)}")
            n_checked_chars += event.char_count
            char_indexes = []
            for j, char in enumerate(event.char_data):
                match = (data[:n_unique_chars] == char).all(axis=(1, 2))
                if match.any():
                    # TODO: Can probably just calculate this once
                    index = np.where(match)[0][0]
                    subchar_indexes[index].append((i, j))
                    char_indexes.append(index)
                else:
                    index = n_unique_chars
                    data[index] = char
                    subchar_indexes.append([(i, j)])
                    char_indexes.append(index)
                    n_unique_chars += 1
            event.char_indexes = char_indexes
        self._data = data[:n_unique_chars]
        self._spec = pd.DataFrame.from_dict({"char": [""] * n_unique_chars,
                                             "indexes": subchar_indexes})

    def _save_hdf5(self, fp, **kwargs):
        """
        Saves subtitles to an output hdf5 file

        .. todo::
          - [ ] Save project info
        """
        dtypes = [("series char index", "i8"),
                  ("char", "S3"),
                  ("subtitle index", "i8"),
                  ("subtitle char index", "i8")]
        encode = lambda x: x.encode("utf8")

        # Save info, styles and subtitles
        SubtitleSeries._save_hdf5(self, fp, **kwargs)

        # Save image mode
        fp.attrs["mode"] = self.mode

        # Save subtitle image data
        if "full_data" in fp:
            del fp["full_data"]
        fp.create_group("full_data")
        for i, event in enumerate(self.events):
            if hasattr(event, "full_data"):
                fp["full_data"].create_dataset(f"{i:04d}",
                                               data=event.full_data,
                                               dtype=self.data_dtype,
                                               chunks=True,
                                               compression="gzip")

        # Save char image specs
        if "spec" in fp:
            del fp["spec"]
        fp.create_dataset("spec",
                          data=np.array(list(map(tuple, list(pd.DataFrame(
                              [(i, encode(s["char"]), j, k)
                               for i, s in self.spec.iterrows()
                               for j, k in s["indexes"]],
                              columns=[d[0] for d in dtypes]).values))),
                                        dtype=dtypes),
                          dtype=dtypes,
                          chunks=True)  # ,
        #                   compression="gzip")

        # Save char image data
        if "data" in fp:
            del fp["data"]
        fp.create_dataset("data",
                          data=self.data,
                          dtype=self.data_dtype,
                          chunks=True)  # ,
        #                   compression="gzip")

    def _save_png(self, fp, **kwargs):
        from os import makedirs
        from os.path import isdir

        # todo: Also save SRT file in folder using pysubs2 code

        if not isdir(fp):
            makedirs(fp)
        for i, event in enumerate(self.events):
            event.save(f"{fp}/{i:04d}.png")

    # endregion

    # region Private Class Methods

    @classmethod
    def _load_hdf5(cls, fp, mode=None, verbosity=1, **kwargs):
        """
        Loads subtitles from an hdf5 file into a nascent SubtitleSeries

        .. todo::
          - [ ] Load project info
        """
        decode = lambda x: x.decode("utf8")

        # Load info, styles, and events
        subs = super()._load_hdf5(fp=fp, verbosity=verbosity, **kwargs)

        # Load images
        if "full_data" in fp and "events" in fp:
            if mode is not None and fp.attrs["mode"] != mode:
                raise ValueError()
            # TODO: Support converting from one image mode to another on load
            subs.mode = fp.attrs["mode"]

            for i, event in enumerate(subs.events):
                event.mode = subs.mode
                event.full_data = np.array(fp["full_data"][f"{i:04d}"],
                                           subs.data_dtype)
                event.char_indexes = np.zeros(event.char_count, np.int)

            # Load char image specs
            if "spec" in fp:
                encoded = np.array(fp["spec"])
                encoded = pd.DataFrame(data=encoded,
                                       index=range(encoded.size),
                                       columns=encoded.dtype.names)
                n_unique_chars = encoded["series char index"].max() + 1
                # empty and tolist are used to create unique empty lists
                spec = pd.DataFrame(
                    {"char": [""] * n_unique_chars,
                     "indexes": np.empty((n_unique_chars, 0)).tolist()})
                for i, char, j, k in encoded.values:
                    spec["char"].loc[i] = decode(char)
                    spec["indexes"].loc[i] += [(j, k)]
                    subs.events[j].char_indexes[k] = i

                subs._spec = spec

            # Load char image data
            if "data" in fp:
                subs._data = np.array(fp["data"])

        return subs

    @classmethod
    def _load_sup(cls, fp, mode=None, verbosity=1, **kwargs):
        from pysubs2.time import make_time

        def read_palette(bytes):
            palette = np.zeros((256, 4), np.uint8)
            bytes_index = 0
            while bytes_index < len(bytes):
                color_index = bytes[bytes_index]
                y = bytes[bytes_index + 1]
                cb = bytes[bytes_index + 2]
                cr = bytes[bytes_index + 3]
                palette[color_index, 0] = y + 1.402 * (cr - 128)
                palette[color_index, 1] = y - .34414 * (cb - 128) - .71414 * (cr - 128)
                palette[color_index, 2] = y + 1.772 * (cb - 128)
                palette[color_index, 3] = bytes[bytes_index + 4]
                bytes_index += 5
            palette[255] = [16, 128, 128, 0]

            return palette

        def read_image(bytes, width, height):
            img = np.zeros((width * height), np.uint8)
            bytes_index = 0
            pixel_index = 0
            while bytes_index < len(bytes):
                byte_1 = bytes[bytes_index]
                if byte_1 == 0x00:  # 00 | Special behaviors
                    byte_2 = bytes[bytes_index + 1]
                    if byte_2 == 0x00:  # 00 00 | New line
                        bytes_index += 2
                    elif (byte_2 & 0xC0) == 0x40:  # 00 4X XX | 0 X times
                        byte_3 = bytes[bytes_index + 2]
                        n_pixels = ((byte_2 - 0x40) << 8) + byte_3
                        color = 0
                        img[pixel_index:pixel_index + n_pixels] = color
                        pixel_index += n_pixels
                        bytes_index += 3
                    elif (byte_2 & 0xC0) == 0x80:  # 00 8Y XX | X Y times
                        byte_3 = bytes[bytes_index + 2]
                        n_pixels = byte_2 - 0x80
                        color = byte_3
                        img[pixel_index:pixel_index + n_pixels] = color
                        pixel_index += n_pixels
                        bytes_index += 3
                    elif (byte_2 & 0xC0) != 0x00:  # 00 CY YY XX | X Y times
                        byte_3 = bytes[bytes_index + 2]
                        byte_4 = bytes[bytes_index + 3]
                        n_pixels = ((byte_2 - 0xC0) << 8) + byte_3
                        color = byte_4
                        img[pixel_index:pixel_index + n_pixels] = color
                        pixel_index += n_pixels
                        bytes_index += 4
                    else:  # 00 XX | 0 X times
                        n_pixels = byte_2
                        color = 0
                        img[pixel_index:pixel_index + n_pixels] = color
                        pixel_index += n_pixels
                        bytes_index += 2
                else:  # XX | X once
                    color = byte_1
                    img[pixel_index] = color
                    pixel_index += 1
                    bytes_index += 1
            img.resize((height, width))

            return img

        bytes2int = lambda x: int.from_bytes(x, byteorder="big")
        segment_kinds = {0x14: "PDS", 0x15: "ODS", 0x16: "PCS",
                         0x17: "WDS", 0x80: "END"}

        # initialize
        subs = cls(mode=mode, verbosity=verbosity)
        subs.format = "sup"

        # Parse infile
        sup_bytes = fp.read()
        byte_offset = 0
        start_time = None
        data = None
        palette = None
        compressed_img = None
        if verbosity >= 2:
            print(f"KIND   :     START      TIME      SIZE    OFFSET")
        while True:
            if bytes2int(sup_bytes[byte_offset:byte_offset + 2]) != 0x5047:
                raise ValueError()

            header_offset = byte_offset
            timestamp = bytes2int(sup_bytes[header_offset + 2:header_offset + 6])
            segment_kind = sup_bytes[header_offset + 10]
            content_size = bytes2int(sup_bytes[header_offset + 11: header_offset + 13])
            content_offset = header_offset + 13

            if segment_kind == 0x14:  # Palette
                palette_bytes = sup_bytes[content_offset + 2:content_offset + content_size]
                palette = read_palette(palette_bytes)
            elif segment_kind == 0x15:  # Image
                image_bytes = sup_bytes[content_offset + 11:content_offset + content_size]
                width = bytes2int(sup_bytes[content_offset + 7:content_offset + 9])
                height = bytes2int(sup_bytes[content_offset + 9:content_offset + 11])
                compressed_img = read_image(image_bytes, width, height)
            elif segment_kind == 0x80:  # End
                if start_time is None:
                    start_time = timestamp / 90000
                    data = np.zeros((*compressed_img.shape, 4), np.uint8)
                    for color_index, color in enumerate(palette):
                        data[np.where(compressed_img == color_index)] = color
                else:
                    end_time = timestamp / 90000
                    subs.events.append(cls.event_class(
                        start=make_time(s=start_time),
                        end=make_time(s=end_time),
                        mode=mode,
                        data=data))

                    start_time = None
                    palette = None
                    compressed_img = None

            if verbosity >= 2:
                print(f"{segment_kinds.get(segment_kind, 'UNKNOWN'):<8s} "
                      f"{hex(segment_kind)}: "
                      f"{header_offset:>9d} "
                      f"{timestamp:>9d} "
                      f"{content_size:>9d} "
                      f"{content_offset:>9d} ")

            byte_offset += 13 + content_size
            if byte_offset >= len(sup_bytes):
                break

        return subs

    # endregion
