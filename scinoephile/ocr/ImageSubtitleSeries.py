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
from IPython import embed
from scinoephile import SubtitleSeries
from scinoephile.ocr import ImageSubtitleEvent


################################### CLASSES ###################################
class ImageSubtitleSeries(SubtitleSeries):
    """
    A series of image-based subtitles
    """

    # region Class Attributes

    event_class = ImageSubtitleEvent
    """Class of individual subtitle events"""

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
    def spec_dtypes(self):
        """OrderedDict(str, type): names and dtypes of columns in spec"""
        from collections import OrderedDict

        return OrderedDict(char=str, indexes=object)

    # endregion

    # region Public Methods

    def assign_char(self, index, char):
        """
        Assigns a character to a character image

        Args:
            index (int): Index of character image to assign
            char (str): Character to assign to image
        """
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
            assign (boot): Copy character assignments from standard
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
                if 0 <= true_label < n_chars:
                    n_total_matchable += 1
                    if pred_char == true_char:
                        n_correct_matchable += 1
        print(f"{n_correct} out of {n_total} characters correct "
              f"(accuracy = {n_correct / n_total:6.4})")
        print(f"{n_correct_matchable} out of {n_total_matchable} matchable "
              f"characters correct "
              f"(accuracy = {n_correct_matchable / n_total_matchable:6.4f})")

    def get_char_index_of_subchar_indexes(self, sub_index, char_index):
        raise NotImplementedError()

    def get_subchar_indexes_of_char_index(self, index):
        """
        Converts the index of a deduplicated character into a list of indexes
        of that character's appearances within subtitles

        Args:
            index (int): Index of deduplicated character

        Returns:
            list(tuple(int, int)): Indexes of character within subtitles in the
              form of (subtitle index within series, character index within
              subtitle)
        """
        return self.spec.loc[index].indexes

    def manually_assign_chars(self, start_index=0):
        """
        Interactively confirm character assignments

        Args:
            start_index (index): Character index at which to start interactive
              character assignment
        """
        from pypinyin import pinyin

        if self.char_predictions is not None:
            predictions = self.get_chars_of_labels(
                np.argsort(self.char_predictions, axis=1)[:, -1])
        else:
            predictions = None

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
                if predictions is not None:
                    match = input(f"'{predictions[i]}' "
                                  f"({pinyin(predictions[i])[0][0]}): ")
                else:
                    match = input(f"'' (): ")
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
        for i, event in enumerate(self.events):
            if self.verbosity >= 1:
                print(f"Reconstructing text for subtitle {i}")
            event.reconstruct_text()

    def save(self, path, format_=None, **kwargs):
        """
        Saves subtitles to an output file

        Note:
            pysubs2.SSAFile.save expects an open text file, so we open the
            hdf5 file here for consistency.

        Args:
            path (str): Path to output file
            format_ (str, optional): Output file format
            **kwargs: Additional keyword arguments
        """
        from os.path import expandvars, isdir
        from pysubs2 import SSAFile

        # Process arguments
        path = expandvars(path).replace("//", "/")
        if self.verbosity >= 1:
            print(f"Writing subtitles to '{path}'")

        # Check if hdf5
        if format_ == "hdf5" or path.endswith(".hdf5") or path.endswith(".h5"):
            import h5py

            with h5py.File(path) as fp:
                self._save_hdf5(fp, **kwargs)
        # Check if directory
        elif format_ == "png" or path.endswith("/") or isdir(path):
            self._save_png(path, **kwargs)
        # Otherwise, continue as superclass SSAFile
        else:
            SSAFile.save(self, path, format_=format_, **kwargs)

    def show(self, indexes=None, data=None, cols=20):
        """
        Shows images of selected characters

        If called from within Jupyter notebook, shows inline. If imgcat module
        is available, shows inline in terminal. Otherwise opens a new window.

        Args:
            indexes (int, list, ndarray, optional): Indexes of characters to
              show
            data (ndarray, optional): Character data to show
            cols (int, optional): Number of columns of characters
        """
        from PIL import Image
        from scinoephile import in_ipython

        # Process arguments
        if data is None:
            data = self.data
        if indexes is None:
            indexes = range(data.shape[0])
        elif isinstance(indexes, int):
            indexes = [indexes]
        indexes = np.array(indexes, np.int)
        if np.any(indexes >= data.shape[0]):
            embed(**self.embed_kw)
            raise ValueError()
        if cols is None:
            cols = indexes.size
            rows = 1
        else:
            rows = int(np.ceil(indexes.size / cols))
        cols = min(cols, indexes.size)

        # Prepare image
        img = Image.new("L", (cols * 100, rows * 100), 255)
        for i, index in enumerate(indexes):
            column = (i // cols)
            row = i - (column * cols)
            char_img = Image.fromarray(data[index])
            img.paste(char_img, (100 * row + 10,
                                 100 * column + 10,
                                 100 * (row + 1) - 10,
                                 100 * (column + 1) - 10))

        # Show image
        if in_ipython() == "ZMQInteractiveShell":
            from io import BytesIO
            from IPython.display import display, Image

            bytes = BytesIO()
            img.save(bytes, "png")
            display(Image(data=bytes.getvalue()))
        elif in_ipython() == "InteractiveShellEmbed":
            img.show()
        else:
            try:
                from imgcat import imgcat

                imgcat(img)
            except ImportError:
                img.show()

    # endregion

    # region Public Class Methods

    @classmethod
    def load(cls, path, format_=None, verbosity=1, **kwargs):
        """
        Loads subtitles from an input file

        Notes:
            pysubs2.SSAFile.from_file expects an open text file, so we open
             the hdf5 file here for consistency

        Args:
            path (str): Path to input file
            format_ (str, optional): Input file format
            verbosity (int, optional): Level of verbose output
            **kwargs: Additional keyword arguments

        Returns:
            ImageSubtitleSeries: Loaded subtitles
        """
        from os.path import expandvars

        # Process arguments
        path = expandvars(path).replace("//", "/")
        if verbosity >= 1:
            print(f"Reading subtitles from '{path}'")

        # Check if hdf5
        if format_ == "hdf5" or path.endswith(".hdf5") or path.endswith(".h5"):
            import h5py

            with h5py.File(path) as fp:
                return cls._load_hdf5(fp, verbosity=verbosity, **kwargs)
        # Check if sup
        if format_ == "sup" or path.endswith(".sup"):
            with open(path, "rb") as fp:
                return cls._load_sup(fp, verbosity=verbosity, **kwargs)
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

        if (hasattr(self, "_data") and self._data is not None
                and hasattr(self, "_spec") and self._spec is not None):
            prior_data = self._data
            prior_spec = self._spec
            if self.verbosity >= 1:
                print("Retaining prior character assignments")
        else:
            prior_data = prior_spec = None

        n_total_chars = sum([e.char_count for e in self.events])
        n_checked_chars = 0
        n_unique_chars = 0
        data = np.zeros((n_total_chars, 80, 80), np.uint8)
        chars = []
        subchar_indexes = []

        # Loop over subtitles within this series
        for i, event in enumerate(self.events):
            if self.verbosity >= 2:
                print(f"Analyzing characters for event "
                      f"{i + 1}/{len(self.events)}")
            n_checked_chars += event.char_count

            # Loop over characters within this subtitle
            for j, datum in enumerate(event.char_data):

                # Check if character is already in nascent array
                match = np.where(
                    (data[:n_unique_chars] == datum).all(axis=(1, 2)))[0]
                if match.size > 0:
                    # Character previously seen, update index
                    subchar_indexes[match[0]].append((i, j))
                else:
                    # Character is new, add to nascent array
                    data[n_unique_chars] = datum
                    subchar_indexes.append([(i, j)])
                    n_unique_chars += 1

                    # Check prior data for assignment of this image
                    if prior_data is not None:
                        prior_match = np.where(
                            (prior_data == datum).all(axis=(1, 2)))[0]
                        if prior_match.size > 0:
                            # Copy over prior assignment
                            chars.append(
                                prior_spec.loc[prior_match[0]]["char"])
                        else:
                            chars.append("")
                    else:
                        chars.append("")
        self._data = data[:n_unique_chars]
        self._spec = pd.DataFrame.from_dict({"char": chars,
                                             "indexes": subchar_indexes})

    def _save_hdf5(self, fp, **kwargs):
        """
        Saves subtitles to an output hdf5 file

        Todo:
            * Save project info

        Args:
            fp (h5py._hl.files.File): Open hdf5 output file
            **kwargs: Additional keyword arguments
        """

        dtypes = [("series char index", "i8"),
                  ("char", "S3"),
                  ("subtitle index", "i8"),
                  ("subtitle char index", "i8")]
        encode = lambda x: x.encode("utf8")

        # Save info, styles and subtitles
        SubtitleSeries._save_hdf5(self, fp, **kwargs)

        # Save subtitle image data
        if "full_data" in fp:
            del fp["full_data"]
        fp.create_group("full_data")
        for i, event in enumerate(self.events):
            if hasattr(event, "full_data"):
                fp["full_data"].create_dataset(f"{i:04d}",
                                               data=event.full_data,
                                               dtype=np.uint8,
                                               chunks=True,
                                               compression="gzip")

        # Save char image specs
        if "spec" in fp:
            del fp["spec"]
        if hasattr(self, "_spec"):
            fp.create_dataset("spec",
                              data=np.array(list(map(tuple, list(pd.DataFrame(
                                  [(i, encode(s["char"]), j, k)
                                   for i, s in self.spec.iterrows()
                                   for j, k in s["indexes"]],
                                  columns=[d[0] for d in dtypes]).values))),
                                            dtype=dtypes),
                              dtype=dtypes,
                              chunks=True,
                              compression="gzip")

        # Save char image data
        if "data" in fp:
            del fp["data"]
        if hasattr(self, "_data"):
            fp.create_dataset("data",
                              data=self.data,
                              dtype=np.uint8,
                              chunks=True,
                              compression="gzip")

    def _save_png(self, fp, **kwargs):
        """
        Saves subtitles to directory of png files

        Todo:
            * Also save srt file in folder using pysubs2 code

        Args:
            fp (str): Directory path
            **kwargs: Additional keyword arguments
        """
        from os import makedirs
        from os.path import isdir

        if not isdir(fp):
            makedirs(fp)
        for i, event in enumerate(self.events):
            event.save(f"{fp}/{i:04d}.png")

    # endregion

    # region Private Class Methods

    @classmethod
    def _load_hdf5(cls, fp, verbosity=1, **kwargs):
        """
        Loads subtitles from an input hdf5 file

         Todo:
            * Load project info

        Args:
            fp (h5py._hl.files.File): Open hdf5 input file
            verbosity (int, optional): Level of verbose output
            **kwargs: Additional keyword arguments

        Returns:
            ImageSubtitleSeries: Loaded subtitles
        """
        decode = lambda x: x.decode("utf8")

        # Load info, styles, and events
        subs = super()._load_hdf5(fp=fp, verbosity=verbosity, **kwargs)

        # Load images
        if "full_data" in fp and "events" in fp:

            for i, event in enumerate(subs.events):
                event.full_data = np.array(fp["full_data"][f"{i:04d}"],
                                           np.uint8)

            # Load char image specs
            if "spec" in fp:
                encoded = np.array(fp["spec"])
                encoded = pd.DataFrame(data=encoded,
                                       index=range(encoded.size),
                                       columns=encoded.dtype.names)
                n_unique_chars = encoded["series char index"].max() + 1
                # np.empty and tolist are used to create unique empty lists
                spec = pd.DataFrame(
                    {"char": [""] * n_unique_chars,
                     "indexes": np.empty((n_unique_chars, 0)).tolist()})
                for i, char, j, k in encoded.values:
                    spec["char"].loc[i] = decode(char)
                    spec["indexes"].loc[i] += [(j, k)]

                subs._spec = spec

            # Load char image data
            if "data" in fp:
                subs._data = np.array(fp["data"])

        return subs

    @classmethod
    def _load_sup(cls, fp, verbosity=1, **kwargs):
        """
        Loads subtitles from an input sup file

        Args:
            fp (): Open binary file
            verbosity (int, optional): Level of verbose output
            **kwargs: Additional keyword arguments

        Returns:
            SubtitleSeries: Loaded subtitles
        """
        from pysubs2.time import make_time

        def read_palette(bytes_):
            palette_ = np.zeros((256, 4), np.uint8)
            bytes_index = 0
            while bytes_index < len(bytes_):
                color_index_ = bytes_[bytes_index]
                y = bytes_[bytes_index + 1]
                cb = bytes_[bytes_index + 2]
                cr = bytes_[bytes_index + 3]
                palette_[color_index_, 0] = y + 1.402 * (cr - 128)
                palette_[color_index_, 1] = y - .34414 * (
                        cb - 128) - .71414 * (cr - 128)
                palette_[color_index_, 2] = y + 1.772 * (cb - 128)
                palette_[color_index_, 3] = bytes_[bytes_index + 4]
                bytes_index += 5
            palette_[255] = [16, 128, 128, 0]

            return palette_

        def read_image(bytes_, width_, height_):
            img = np.zeros((width_ * height_), np.uint8)
            bytes_index = 0
            pixel_index = 0
            while bytes_index < len(bytes_):
                byte_1 = bytes_[bytes_index]
                if byte_1 == 0x00:  # 00 | Special behaviors
                    byte_2 = bytes_[bytes_index + 1]
                    if byte_2 == 0x00:  # 00 00 | New line
                        bytes_index += 2
                    elif (byte_2 & 0xC0) == 0x40:  # 00 4X XX | 0 X times
                        byte_3 = bytes_[bytes_index + 2]
                        n_pixels = ((byte_2 - 0x40) << 8) + byte_3
                        color_ = 0
                        img[pixel_index:pixel_index + n_pixels] = color_
                        pixel_index += n_pixels
                        bytes_index += 3
                    elif (byte_2 & 0xC0) == 0x80:  # 00 8Y XX | X Y times
                        byte_3 = bytes_[bytes_index + 2]
                        n_pixels = byte_2 - 0x80
                        color_ = byte_3
                        img[pixel_index:pixel_index + n_pixels] = color_
                        pixel_index += n_pixels
                        bytes_index += 3
                    elif (byte_2 & 0xC0) != 0x00:  # 00 CY YY XX | X Y times
                        byte_3 = bytes_[bytes_index + 2]
                        byte_4 = bytes_[bytes_index + 3]
                        n_pixels = ((byte_2 - 0xC0) << 8) + byte_3
                        color_ = byte_4
                        img[pixel_index:pixel_index + n_pixels] = color_
                        pixel_index += n_pixels
                        bytes_index += 4
                    else:  # 00 XX | 0 X times
                        n_pixels = byte_2
                        color_ = 0
                        img[pixel_index:pixel_index + n_pixels] = color_
                        pixel_index += n_pixels
                        bytes_index += 2
                else:  # XX | X once
                    color_ = byte_1
                    img[pixel_index] = color_
                    pixel_index += 1
                    bytes_index += 1
            img.resize((height_, width_))

            return img

        bytes2int = lambda x: int.from_bytes(x, byteorder="big")
        segment_kinds = {0x14: "PDS", 0x15: "ODS", 0x16: "PCS",
                         0x17: "WDS", 0x80: "END"}

        # initialize
        subs = cls(verbosity=verbosity)
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
            timestamp = bytes2int(
                sup_bytes[header_offset + 2:header_offset + 6])
            segment_kind = sup_bytes[header_offset + 10]
            content_size = bytes2int(
                sup_bytes[header_offset + 11: header_offset + 13])
            content_offset = header_offset + 13

            if segment_kind == 0x14:  # Palette
                palette_bytes = sup_bytes[content_offset + 2:
                                          content_offset + content_size]
                palette = read_palette(palette_bytes)
            elif segment_kind == 0x15:  # Image
                image_bytes = sup_bytes[content_offset + 11:
                                        content_offset + content_size]
                width = bytes2int(
                    sup_bytes[content_offset + 7:content_offset + 9])
                height = bytes2int(
                    sup_bytes[content_offset + 9:content_offset + 11])
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
