Introduction
============

Script for adding romanization below Chinese subtitles, and combining Chinese
and English subtitles. Supports Mandarin Hanyu Pinyin and the Yale romanization
of Cantonese. Cantonese romanization is really only useful for older Hong Kong
movies (1980s to early 1990s) whose Chinese subtitles match the spoken
Cantonese 1:1 (that is, using 係, 喺, and 唔 rather than 是, 在, and 不, etc.). 

Example Mandarin Output::

      2
      00:01:04,397 --> 00:01:06,149
      喲！李爺來啦
      yō! lǐ yé lái la
      Master Li is here!

Example Cantonese Output::

    207
    00:12:13,274 --> 00:12:14,109
    係咪话我呀？　﹣係！
    haih maih wah ngóh àh?- haih!
    - You mean me?    - Yes!

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

    usage: zysyzm.py [-h] [-v | -q] [-i] [-s] [-m] [-c] [-o [OUTFILE]]
                 chinese_infile [english_infile]

    Script to add romanization and optionally English translation to Chinese
    subtitles.

    positional arguments:
      chinese_infile        Chinese subtitles in SRT format
      english_infile        English subtitles in SRT format (optional)

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         enable verbose output, may be specified more than once
      -q, --quiet           disable verbose output
      -i, --interactive     present IPython prompt after loading and processing
      -s, --simplified      convert traditional character to simplified
      -m, --mandarin        add Mandarin/Putonghua pinyin (汉语拼音)
      -c, --cantonese       add Cantonese/Guangdonghua Yale-style pinyin (耶鲁广东话拼音)
      -o [OUTFILE], --outfile [OUTFILE]
                            Output file (optional)

Authorship
==========

ZYSYZM is developed by Karl T. Debiec.

License
=======

Released under a 3-clause BSD license.
