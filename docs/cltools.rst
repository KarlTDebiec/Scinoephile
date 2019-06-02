:github_url: https://github.com/KarlTDebiec/scinoephile

Command-Line Tools
------------------

Compositor
__________

.. code-block:: text

    usage: Compositor.py [-h] [-v | -q] [-b [FILE]] [-c [FILE]] [-e [FILE]]
                         [-p [FILE]] [-s] [-m] [-y]

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
      -b [FILE], --bilingual [FILE]
                            Bilingual subtitles
      -c [FILE], --chinese [FILE], --hanzi [FILE]
                            Chinese Hanzi subtitles
      -e [FILE], --english [FILE]
                            English subtitles
      -p [FILE], --pinyin [FILE]
                            Chinese Pinyin subtitles

    operation arguments:
      -s, --simplify        convert traditional characters to simplified
      -m, --mandarin        add Mandarin Hanyu pinyin (汉语拼音)
      -y, --yue             add Cantonese Yale pinyin (耶鲁粤语拼音)

.. autoclass:: scinoephile.Compositor.Compositor()
