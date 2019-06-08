Introduction
------------

Python package for working with Chinese/English bilingual subtitles. Mainly
useful for combining separate Chinese and English subtitle files into single
synchronized bilingual subtitles. May optionally add romanization below Chinese
subtitles using Mandarin Hanyu Pinyin or the Yale romanization of Cantonese.
Cantonese romanization is really only useful for older Hong Kong movies (1980s
to early 1990s) whose Chinese subtitles `match the spoken Cantonese 1:1
<https://en.wikipedia.org/wiki/Written_Cantonese>`_ (that is, using 係, 喺,
and 唔 rather than 是, 在, and 不, etc.). Optical Character Recognition
functions are currently under development to allow the conversion of
image-based Blu-Ray subtitles to text format.

Dependencies
------------

All features require the following modules:

- `IPython <https://github.com/ipython/ipython>`_
- `numpy <https://github.com/numpy/numpy>`_
- `pandas <https://github.com/pandas-dev/pandas>`_
- `pysubs2 <https://github.com/tkarabela/pysubs2>`_

Selected features may also require:

- `google-cloud-translate <https://pypi.org/project/google-cloud-translate/>`_
- `h5py <https://github.com/h5py/h5py>`_
- `hanziconv <https://github.com/berniey/hanziconv>`_
- `imgcat <https://github.com/wookayin/python-imgcat>`_
- `matplotlib <https://github.com/matplotlib/matplotlib>`_
- `nltk <https://github.com/nltk/nltk>`_
- `numba <https://github.com/numba/numba>`_
- `pillow <https://github.com/python-pillow/Pillow>`_
- `pycantonese <https://github.com/pycantonese/pycantonese>`_
  (recent version from from GitHub rather than pypi)
- `pypinyin <https://github.com/mozillazg/python-pinyin>`_
- `snownlp <https://github.com/isnowfy/snownlp>`_
- `tensorflow <https://github.com/tensorflow/tensorflow>`_

Installation
------------

.. code-block:: text

    python setup.py install

Usage
-----

Compositor
__________

.. code-block:: text

    usage: Compositor.py [-h] [-v | -q] [-b FILE [overwrite ...]]
                     [-c FILE [overwrite ...]] [-e FILE [overwrite ...]]
                     [-p FILE [overwrite ...]] [-s] [-m] [-y]

    Compiles Chinese and English subtitles into a single file, optionally adding
    Mandarin or Cantonese pinyin, converting traditional characters to simplified,
    or adding machine translation.

    Operations are inferred from provided arguments, e.g.:

      Translate Chinese to English:
        Compositor.py -e /nonexisting/english/outfile
                      -c /existing/chinese/infile

      Translate English to Chinese:
        Compositor.py -e /existing/english/infile
                      -c /nonexisting/chinese/outfile

      Merge Chinese and English:
        Compositor.py -e /existing/english/infile
                      -c /existing/chinese/infile
                      -b /nonexisting/bilingual/outfile

      Convert traditional Chinese to simplified, translate to English, and merge:
        Compositor.py -c /existing/chinese/infile
                      -b /nonexisting/bilingual/outfile
                      --simplify

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         enable verbose output, may be specified more than once
      -q, --quiet           disable verbose output

    file arguments:
      -b FILE [overwrite ...], --bilingual FILE [overwrite ...]
                            Bilingual subtitles
      -c FILE [overwrite ...], --chinese FILE [overwrite ...]
                            Chinese Hanzi subtitles
      -e FILE [overwrite ...], --english FILE [overwrite ...]
                            English subtitles
      -p FILE [overwrite ...], --pinyin FILE [overwrite ...]
                            Chinese Pinyin subtitles

    operation arguments:
      -s, --simplify        convert traditional characters to simplified
      -m, --mandarin        add Mandarin Hanyu pinyin (汉语拼音)
      -y, --yue             add Cantonese Yale pinyin (耶鲁粤语拼音)


Authorship
----------

Scinoephile is developed by Karl T. Debiec.

License
-------

Released under a 3-clause BSD license.
