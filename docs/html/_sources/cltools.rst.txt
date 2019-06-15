:github_url: https://github.com/KarlTDebiec/scinoephile

Command-Line Tools
------------------

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
                            bilingual subtitles
      -c FILE [overwrite ...], --chinese FILE [overwrite ...]
                            Chinese Hanzi subtitles
      -e FILE [overwrite ...], --english FILE [overwrite ...]
                            English subtitles
      -p FILE [overwrite ...], --pinyin FILE [overwrite ...]
                            Chinese pinyin subtitles

    operation arguments:
      -s, --simplify        convert traditional characters to simplified
      -m, --mandarin        add Mandarin Hanyu pinyin (汉语拼音)
      -y, --yue             add Cantonese Yale pinyin (耶鲁粤语拼音); mainly useful for
                            older Hong Kong movies (1980s to early 1990s) whose
                            Chinese subtitles are in 粤文 (i.e. using 係, 喺, and 唔
                            rather than 是, 在, and 不, etc.)

.. autoclass:: scinoephile.Compositor.Compositor()
