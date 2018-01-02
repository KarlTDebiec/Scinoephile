Introduction
============

Script for adding romanization below Chinese subtitles. Presently only
supports the Yale romanization of Cantonese. This is really only useful for old
Hong Kong movies (1980s to early 1990s) whose Chinese subtitles match the
spoken Cantonese 1:1 (that is, using 係, 喺, and 唔 rather than 是, 在, and 不,
etc.). In the future may support Hanyu Pinyin for Mandarin films, and possibly
the side-by-side display of Chinese and English subtitles.

Example Onput:::

    206
    00:12:14,234 --> 00:12:16,277
    係咪係咯！我係嚟…

Example Output:::

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

Installation
============

Not currently possible or necessary. Just run the script from the folder within
which the script is located. Writes output directly to the terminal; just
redirect it to a file.

Authorship
==========

ZYSYZM is developed by Karl T. Debiec.

License
=======

Released under a 3-clause BSD license.
