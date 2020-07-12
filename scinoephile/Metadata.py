#!python
#   scinoephile.Metadata.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Adds Apple/iTunes-compatible metadata to MP4 files."""
################################### MODULES ###################################
import re
from argparse import ArgumentParser
from glob import glob
from os import rename
from os.path import expandvars, getctime, isfile
from shlex import quote
from subprocess import Popen
from typing import Any

import dateutil
import lxml.etree as etree
from scinoephile.core import (CLToolBase, date_argument,
                              get_list_formatted_for_display,
                              infile_argument, outfile_argument)


################################### CLASSES ###################################
class Metadata(CLToolBase):
    """
    Adds Metadata
    """
    genres = {"Action & Adventure": 4401, "Anime": 4402, "Classics": 4403,
              "Comedy": 4404, "Documentary": 4405, "Drama": 4406,
              "Foreign": 4407, "Horror": 4408, "Independent": 4409,
              "Kids & Family": 4410, "Musicals": 4411, "Romance": 4412,
              "Sci-Fi & Fantasy": 4413, "Short Films": 4414,
              "Special Interest": 4415, "Thriller": 4416, "Sports": 4417,
              "Western": 4418, "Urban": 4419, "Holiday": 4420,
              "Made for TV": 4421, "Concert Films": 4422,
              "Music Documentaries": 4423, "Music Feature Films": 4424,
              "Japanese Cinema": 4425, "Jidaigeki": 4426, "Tokusatsu": 4427,
              "Korean Cinema": 4428}
    ratings = ["Unrated", "NC-17", "R", "PG-13", "PG", "G"]

    # region Builtins

    def __init__(self, infile, outfile, cast=None, catalog_id=None, date=None,
                 description=None, director=None, language=None, genre=None,
                 overwrite=False, producer=None, rating=None, studio=None,
                 title=None, writer=None, **kwargs: Any) -> None:
        """
        Initializes command-line tool and compiles list of operations

        Args:
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # TODO: Document
        # TODO: Move xml lists into static function

        # Compile input operations
        self.args.insert(0, quote(infile))

        # Compile metadata operations
        if title:
            self.args.append(f"--title {quote(title)}")
        if date:
            self.args.append(f"--year {quote(date.strftime('%Y-%m-%d'))}")
        if description:
            self.args.append(f"--longdesc {quote(description)}")
            self.args.append(f"--storedesc {quote(description)}")
        if genre:
            if genre in self.genres:
                self.args.append(f"--genre {quote(genre)}")
                self.args.append(f"--geID {self.genres[genre]}")
            else:
                raise ValueError(f"Genre must be one of "
                                 f"{get_list_formatted_for_display(self.genres, 'or')}; "
                                 f"'{genre}' provided")
        if language:
            if isinstance(language, list):
                grouping = get_list_formatted_for_display(language, "", "")
                self.args.append(f"--grouping  {quote(grouping)}")
            else:
                raise ValueError(
                    f"language must be a list of strings; "
                    f"'{language}' provided")
            # TODO: Is there some other tag? VLC does not seem to recognize yue
        if rating:
            if isinstance(rating, str):
                if rating in self.ratings:
                    self.args.append(f"--contentRating {quote(rating)}")
                else:
                    raise ValueError(f"Rating must be one of "
                                     f"{get_list_formatted_for_display(self.ratings, 'or')}; "
                                     f"'{rating}' provided")
            else:
                raise ValueError(
                    f"rating must be a string; '{rating}' provided")
        if catalog_id:
            if isinstance(catalog_id, int):
                self.args.append(f"--cnID {catalog_id}")
            else:
                raise ValueError(f"catalog_id must be an integer; "
                                 f"'{catalog_id}' provided")
        if cast or director or producer or writer or studio:
            xmlroot = etree.Element("plist", {"version": "1.0"})
            xmldict = etree.SubElement(xmlroot, "dict")
        if cast:
            if isinstance(cast, list):
                etree.SubElement(xmldict, "key").text = "cast"
                xmlarray = etree.SubElement(xmldict, "array")
                for name in cast:
                    xmldict2 = etree.SubElement(xmlarray, "dict")
                    etree.SubElement(xmldict2, "key").text = "name"
                    etree.SubElement(xmldict2, "string").text = name
            else:
                raise ValueError(
                    f"cast must be a list of strings; "
                    f"'{cast}' provided")
        if director:
            if isinstance(director, list):
                artist = get_list_formatted_for_display(director, "and", "")
                self.args.append(f"--artist {quote(artist)}")

                etree.SubElement(xmldict, "key").text = "directors"
                xmlarray = etree.SubElement(xmldict, "array")
                for name in director:
                    xmldict2 = etree.SubElement(xmlarray, "dict")
                    etree.SubElement(xmldict2, "key").text = "name"
                    etree.SubElement(xmldict2, "string").text = name
            else:
                raise ValueError(
                    f"director must be a list of strings; "
                    f"'{director}' provided")
        if producer:
            if isinstance(producer, list):
                etree.SubElement(xmldict, "key").text = "producers"
                xmlarray = etree.SubElement(xmldict, "array")
                for name in producer:
                    xmldict2 = etree.SubElement(xmlarray, "dict")
                    etree.SubElement(xmldict2, "key").text = "name"
                    etree.SubElement(xmldict2, "string").text = name
            else:
                raise ValueError(
                    f"Producer must be a list of strings; "
                    f"'{producer}' provided")
        if writer:
            if isinstance(writer, list):
                etree.SubElement(xmldict, "key").text = "screenwriters"
                xmlarray = etree.SubElement(xmldict, "array")
                for name in writer:
                    xmldict2 = etree.SubElement(xmlarray, "dict")
                    etree.SubElement(xmldict2, "key").text = "name"
                    etree.SubElement(xmldict2, "string").text = name
            else:
                raise ValueError(
                    f"writer must be a list of strings; "
                    f"'{writer}' provided")
        if studio:
            if isinstance(studio, list):
                etree.SubElement(xmldict, "key").text = "studio"
                etree.SubElement(xmldict, "string").text = \
                    get_list_formatted_for_display(studio, "and", "")
            else:
                raise ValueError(
                    f"studio must be a list of strings; "
                    f"'{studio}' provided")
        if cast or director or producer or writer or studio:
            rDNSatom = etree.tostring(xmlroot, encoding='UTF-8',
                                      xml_declaration=True).decode()
            self.args.append(f"--rDNSatom {quote(rDNSatom)} "
                             f"name=iTunMOVI "
                             f"domain=com.apple.iTunes")
        self.args = ["AtomicParsley"] + self.args

        # Compile output operations
        if not outfile:
            if overwrite:
                # AtomicParsley will not overwrite its infile with its outfile,
                # it will write to a temporary file. Here the desired outfile
                # is saved so the temporary file may be moved into place
                # afterwards
                outfile = infile
                self.outfile = outfile
            else:
                raise ValueError(f"outfile must be provided, or overwrite "
                                 f"must be true to overwrite infile")
        outfile = expandvars(str(outfile))
        if not isfile(outfile) or overwrite:
            self.args.append(f"-o {quote(outfile)}")
        else:
            raise ValueError(f"MP4 outfile '{outfile}' already exists")

    def __call__(self):
        """
        Performs operations
        """
        # Run AtomicParsley
        cmd = " ".join(self.args)
        if self.verbosity >= 1:
            print(cmd)
        p = Popen(cmd, shell=True)
        p_status = p.wait()

        # Move temporary file to final location, if necessary
        if self.outfile is not None:
            temp_file = max(glob(f"{self.outfile.rstrip('.mp4')}-temp-*.mp4"),
                            key=getctime)
            rename(temp_file, self.outfile)

    # endregion

    # region Public Properties

    @property
    def args(self):
        """list: Command line arguments"""
        if not hasattr(self, "_args"):
            self._args = ["--stik value=9", "--hdvideo true"]
        return self._args

    @args.setter
    def args(self, value):
        # TODO: Validate
        self._args = value

    @property
    def outfile(self):
        """list: Outfile"""
        if not hasattr(self, "_outfile"):
            self._outfile = None
        return self._outfile

    @outfile.setter
    def outfile(self, value):
        # TODO: Validate
        self._outfile = value

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser

        Returns:
            parser (ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__, **kwargs)

        # Input
        parser_input = parser.add_argument_group("input arguments")
        parser_input.add_argument(
            "-if", "--infile",
            help="MP4 infile",
            metavar="FILE",
            type=infile_argument,
            required=True)

        # Metadata
        parser_metadata = parser.add_argument_group("metadata arguments")
        parser_metadata.add_argument(
            "--title",
            type=str,
            help="Title")
        parser_metadata.add_argument(
            "--date",
            type=date_argument,
            help="Date of release")
        parser_metadata.add_argument(
            "--description",
            type=str,
            help="Description")
        parser_metadata.add_argument(
            "--genre",
            type=str,
            help="Genre")
        parser_metadata.add_argument(
            "--language",
            action="append",
            type=str,
            help="Language")
        parser_metadata.add_argument(
            "--rating",
            default="Unrated",
            type=str,
            help="MPAA Rating")
        parser_metadata.add_argument(
            "--catalog_id",
            help="Apple Catalog ID",
            type=int)
        parser_metadata.add_argument(
            "--studio",
            action="append",
            help="Production Studio")
        parser_metadata.add_argument(
            "--cast",
            action="append",
            help="Cast member")
        parser_metadata.add_argument(
            "--director",
            action="append",
            help="Director")
        parser_metadata.add_argument(
            "--producer",
            action="append",
            help="Producer")
        parser_metadata.add_argument(
            "--writer",
            action="append",
            help="Writer")

        # Output
        parser_output = parser.add_argument_group("output arguments")
        parser_output.add_argument(
            "-of", "--outfile",
            help="MP4 outfile",
            type=outfile_argument,
            metavar="FILE")
        parser_output.add_argument(
            "-o", "--overwrite",
            action="store_true",
            help="overwrite outfiles if they exist")

        return parser

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    Metadata.main()
