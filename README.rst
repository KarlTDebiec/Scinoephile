Introduction
============

Python package for working with Chinese/English bilingual subtitles. Mainly
useful for combining separate Chinese and English subtitle files into single
synchronized bilingual subtitles. May optionally add romanization below Chinese
subtitles using Mandarin Hanyu Pinyin or the Yale romanization of Cantonese.
Cantonese romanization is really only useful for older Hong Kong movies (1980s
to early 1990s) whose Chinese subtitles `match the spoken Cantonese 1:1
<https://en.wikipedia.org/wiki/Written_Cantonese>`_ (that is, using 係, 喺, and
唔 rather than 是, 在, and 不, etc.). Optical Character Recognition functions
are currently under development to allow the conversion of image-based Blu-Ray
subtitles to text format.

Example Mandarin/English Output::

      2
      00:01:04,397 --> 00:01:06,149
      喲！李爺來啦
      yō! lǐ yé lái la
      Master Li is here!

Example Cantonese/English Output::

    207
    00:12:13,274 --> 00:12:14,109
    係咪话我呀？　﹣係！
    haih maih wah ngóh àh?- haih!
    - You mean me?    - Yes!

Dependencies
============

- `hanziconv <https://github.com/berniey/hanziconv>`_
- `nltk <https://github.com/nltk/nltk>`_
- `numpy <https://github.com/numpy/numpy>`_
- `pandas <https://github.com/pandas-dev/pandas>`_
- `pycantonese <https://github.com/pycantonese/pycantonese>`_
  (recent version from from GitHub rather than pypi)
- `pypinyin <https://github.com/mozillazg/python-pinyin>`_
- `snownlp <https://github.com/isnowfy/snownlp>`_

Installation
============

``python setup.py install``

Usage
=====

::

    usage: CompilationManager.py [-h] [-v | -q] [-I] [-c [INFILE]] [-e [INFILE]]
                                 [--c_offset C_OFFSET] [-s] [-m] [-y] [-t]
                                 [--e_offset E_OFFSET] [--truecase] [-o [OUTFILE]]

    Compiles Chinese and English subtitles into a single file, optionally adding
    Mandarin or Cantonese romanization, converting traditional characters to
    simplified, or adding machine translation.

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         enable verbose output, may be specified more than once
      -q, --quiet           disable verbose output
      -I, --interactive     present IPython prompt

    input arguments (at least one required):
      -c [INFILE], --chinese_infile [INFILE]
                            Chinese subtitles in SRT or VTT format
      -e [INFILE], --english_infile [INFILE]
                            English subtitles in SRT or VTT format

    operation arguments:
      --c_offset C_OFFSET   apply offset to Chinese subtitle timings
      -s, --simplified      convert traditional characters to simplified
      -m, --mandarin        add Mandarin Hanyu pinyin (汉语拼音)
      -y, --yue             add Cantonese Yale pinyin (耶鲁粤语拼音)
      -t, --translate       add English machine translation generated using Google
                            Translate; requires key for Google Cloud Platform
      --e_offset E_OFFSET   apply offset to English subtitle timings
      --truecase            apply standard capitalization to English subtitles

    output arguments:
      -o [OUTFILE], --outfile [OUTFILE]
                            output file

Authorship
==========

ZYSYZM is developed by Karl T. Debiec.

License
=======

Released under a 3-clause BSD license.
