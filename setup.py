#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name="scinoephile",
    version="0.1",
    include_package_data=True,
    package_data={"scinoephile": ["data/ocr/characters.txt",
                                  "data/romanization/unmatched.cha"]},
    packages=find_packages())

