.. |build| image:: docs/static/build.svg

.. |coverage| image:: docs/static/coverage.svg

.. |docs| image:: docs/static/docs.svg

.. |license| image:: docs/static/license.svg

|build| |coverage| |docs| |license|

.. github_header_end

Introduction
------------

Python package for working with Chinese/English bilingual subtitles. Useful
for converting image-based Chinese subtitles into text using OCR, and for
combining separate Chinese and English subtitles into synchronized bilingual
subtitles. May optionally add romanization below Chinese subtitles using
Mandarin Hanyu Pinyin or the Yale romanization of Cantonese.

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

Derasterizer
____________

.. code-block:: text
    :name: derasterizer_usage

    usage: Derasterizer.py [-h] [-v | -q] -if FILE [-rm FILE] [-sf FILE] [-t]
                           [-of FILE] [-o]

    Converts image-based subtitles into text using a deep neural network-based
    optical character recognition model.

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         enable verbose output, may be specified more than once
      -q, --quiet           disable verbose output

    input arguments:
      -if FILE, --infile FILE
                            image-based subtitle infile
      -rm FILE, --recognition_model FILE
                            character recognition model infile
      -sf FILE, --standard FILE
                            standard subtitles infile against which to compare
                            results
      -of FILE, --outfile FILE
                            text-based subtitle outfile

    operation arguments:
      -t, --tesseract       use tesseract library for OCR rather than scinoephile

    output arguments:
      -o, --overwrite       overwrite outfiles if they exist

Compositor
__________

.. code-block:: text
    :name: compositor_usage

    usage: Compositor.py [-h] [-v | -q] [-bif FILE] [-cif FILE] [-eif FILE]
                         [-pif FILE] [-c] [-m] [-s] [-bof FILE] [-cof FILE]
                         [-eof FILE] [-pof FILE] [-o]

    Compiles Chinese and English subtitles into a single file, optionally adding
    Mandarin or Cantonese pinyin, converting traditional characters to simplified,
    or adding machine translation.

    Operations are inferred from provided infiles and outfiles, e.g.:

      Merge Chinese and English:
        Compositor.py -cif /chinese/infile
                      -eif /english/infile
                      -bof /bilingual/outfile

      Convert Chinese Hanzi to Cantonese Yale pinyin:
        Compositor.py -cif /chinese/infile
                      -pof /chinese/outfile
                      --cantonese

      Translate Chinese Hanzi to English, overwriting if necessary:
        Compositor.py -cif /chinese/infile
                      -eof /english/outfile
                      -o

      Convert traditional Chinese to simplified, translate to English, and merge:
        Compositor.py -cif /chinese/infile
                      -bof /bilingual/outfile
                      --simplify

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         enable verbose output, may be specified more than once
      -q, --quiet           disable verbose output

    input arguments:
      -bif FILE, --bilingual_infile FILE
                            bilingual subtitle infile
      -cif FILE, --chinese_infile FILE
                            Chinese Hanzi subtitle infile
      -eif FILE, --english_infile FILE
                            English subtitle infile
      -pif FILE, --pinyin_infile FILE
                            Chinese pinyin subtitle infile

    operation arguments:
      -c, --cantonese       add Cantonese Yale pinyin (耶鲁粤语拼音); mainly useful for
                            older Hong Kong movies (1980s to early 1990s) whose
                            Chinese subtitles are in 粤文 (i.e. using 係, 喺, and 唔
                            rather than 是, 在, and 不, etc.)
      -m, --mandarin        add Mandarin Hanyu pinyin (汉语拼音)
      -s, --simplify        convert traditional Hanzi characters to simplified

    output arguments:
      -bof FILE, --bilingual_outfile FILE
                            bilingual subtitle outfile
      -cof FILE, --chinese_outfile FILE
                            Chinese Hanzi subtitle outfile
      -eof FILE, --english_outfile FILE
                            English subtitle outfile
      -pof FILE, --pinyin_outfile FILE
                            Chinese pinyin subtitle outfile
      -o, --overwrite       overwrite outfiles if they exist

Authorship
----------

Scinoephile is developed by Karl T. Debiec.

License
-------

Released under a 3-clause BSD license.
