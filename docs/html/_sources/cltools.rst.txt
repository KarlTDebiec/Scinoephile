:github_url: https://github.com/KarlTDebiec/scinoephile

Command-Line Tools
------------------

Derasterizer
____________

.. code-block:: text
    :name: derasterizer_helptext

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
                            image-based Chinese Hanzi subtitle infile
      -rm FILE, --recognition_model FILE
                            character recognition model infile
      -sf FILE, --standard FILE
                            known accurate text-based Chinese Hanzi subtitle
                            infile for validation of OCR results

    operation arguments:
      -t, --tesseract       use tesseract library for OCR rather than scinoephile

    output arguments:
      -of FILE, --outfile FILE
                            text-based Chinese Hanzi subtitle outfile
      -o, --overwrite       overwrite outfile if it exists

.. autoclass:: scinoephile.Derasterizer.Derasterizer()

Compositor
__________

.. code-block:: text
    :name: compositor_helptext

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

.. autoclass:: scinoephile.Compositor.Compositor()
