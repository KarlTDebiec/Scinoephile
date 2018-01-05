Introduction
============

Script for adding romanization below Chinese subtitles. Supports Mandarin Hanyu
Pinyin and the Yale romanization of Cantonese. Cantonese romanization is really
only useful for older Hong Kong movies (1980s to early 1990s) whose Chinese
subtitles match the spoken Cantonese 1:1 (that is, using 係, 喺, and 唔 rather
than 是, 在, and 不, etc.). In the future may support simultaneous display of
Chinese and English subtitles.

Example Mandarin Input::
    1021
    01:54:17,982 --> 01:54:19,818
    一起回新疆！

Example Mandarin Output::
    1021
    01:54:17,982 --> 01:54:19,818
    一起回新疆！
    yìqǐ huí xīnjiāng!

Example Cantonese Input::

    206
    00:12:14,234 --> 00:12:16,277
    係咪係咯！我係嚟…

Example Cantonese Output::

    206
    00:12:14,234 --> 00:12:16,277
    係咪係咯！我係嚟…
    haih maih haih lok! ngóh haih lèih...

Dependencies
============

- `hanziconv <https://github.com/berniey/hanziconv>`_
- `pandas <https://github.com/pandas-dev/pandas>`_
- `pycantonese <https://github.com/pycantonese/pycantonese>`_
  (Recent version from from GitHub rather than pypi)
- `pypinyin <https://github.com/mozillazg/python-pinyin>`_
- `snownlp <https://github.com/isnowfy/snownlp>`_

Installation
============

Not currently possible or necessary. Just run the script from the folder within
which the script is located. Writes output directly to the terminal; just
redirect it to a file.

Usage
=====

::
    usage: zysyzm.py [-h] [-v | -q] [-m | -c] chinese_infile

    Adds romanization below Chinese subtitles.

    positional arguments:
      chinese_infile   Chinese subtitles in SRT format

    optional arguments:
      -h, --help       show this help message and exit
      -v, --verbose    enable verbose output, may be specified more than once
      -q, --quiet      disable verbose output
      -m, --mandarin   add Mandarin/Putonghua pinyin (汉语拼音)
      -c, --cantonese  add Cantonese/Guangdonghua Yale-style pinyin (耶鲁广东话拼音)

Authorship
==========

ZYSYZM is developed by Karl T. Debiec.

License
=======

Released under a 3-clause BSD license.
