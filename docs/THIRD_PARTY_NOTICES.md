# Third-Party Notices

## jyut-dict (source inspiration and adapted logic)

Scinoephile's CUHK and GZZJ dictionary ingestion code is informed by and
partially adapted from the `jyut-dict` project:

- Project: https://github.com/aaronhktan/jyut-dict
- License: MIT
- Copyright: Copyright (c) 2025 Aaron Tan

The `jyut-dict` license permits use, modification, and distribution, provided the
copyright and permission notice are included in copies or substantial portions
of the software.

For the complete license text used by `jyut-dict`, see:

- https://github.com/aaronhktan/jyut-dict/blob/main/LICENSE

MIT license text (from `jyut-dict`):

```text
MIT License

Copyright (c) 2025 Aaron Tan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## SubtitleEdit (adapted OCR preprocessing and grouping logic)

Scinoephile's PaddleOCR preprocessing and text grouping code is informed by and
partially adapted from the `SubtitleEdit` project:

- Project: https://github.com/SubtitleEdit/subtitleedit
- License: MIT
- Copyright: Copyright (c) 2026 Nikolaj Olsson

The `SubtitleEdit` license permits use, modification, and distribution, provided
the copyright and permission notice are included in copies or substantial
portions of the software.

For the complete license text used by `SubtitleEdit`, see:

- https://github.com/SubtitleEdit/subtitleedit/blob/master/LICENSE

MIT license text (from `SubtitleEdit`):

```text
MIT License

Copyright (c) 2026 Nikolaj Olsson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## CUHK dictionary data source

The CUHK data source used by the scraper is:

- 現代標準漢語與粵語對照資料庫
- https://apps.itsc.cuhk.edu.hk/hanyu/Page/Cover.aspx

The CUHK site states copyright ownership by the Chinese University of Hong Kong.
Scinoephile does not distribute CUHK dictionary data in-repository; users build
local caches from the source site.

## GZZJ dictionary data source

The GZZJ data source used by the local parser is:

- 廣州話正音字典
- https://github.com/jyutnet/cantonese-books-data/tree/master/2004_%E5%BB%A3%E5%B7%9E%E8%A9%B1%E6%AD%A3%E9%9F%B3%E5%AD%97%E5%85%B8

Scinoephile does not distribute the upstream `B01_資料.json` file in-repository.
Users must download it themselves before running `dictionary build gzzj`.

## Kaifangcidian dictionary data source

The Kaifangcidian source used by the local parser is:

- 開放粵語詞典
- https://www.kaifangcidian.com/han/yue
- Data endpoints:
  - https://www.kaifangcidian.com/yue/js/hzsg.js
  - https://www.kaifangcidian.com/yue/js/jpsg.js
  - https://www.kaifangcidian.com/yue/js/lg.js

Kaifangcidian's copyright page states that site resources are licensed under
Creative Commons Attribution 3.0 unless otherwise noted:

- https://www.kaifangcidian.com/yue/cc/

Scinoephile can build from local canonical CSV snapshots under
`scinoephile/data/dictionaries/kaifangcidian/`, or by downloading the upstream
website payloads during `dictionary build kaifangcidian`.

## Unihan dictionary data source

The Unihan source used by the local parser is:

- Unihan Database
- https://www.unicode.org/charts/unihan.html
- Archive endpoint:
  - https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip

Unicode data and software are provided under the Unicode License Agreement and
Terms of Use:

- https://www.unicode.org/license.html
- https://www.unicode.org/copyright.html

Scinoephile can build from local Unihan source snapshots under
`scinoephile/data/dictionaries/unihan/`, or by downloading and extracting
`Unihan.zip` during `dictionary build unihan`.

## Wiktionary (Kaikki) dictionary data source

The Wiktionary source used by the local parser is:

- Wiktionary
- https://en.wiktionary.org/wiki/Wiktionary:Main_Page
- Kaikki Chinese dump index:
  - https://kaikki.org/dictionary/Chinese/

Wiktionary text is available under Creative Commons Attribution-ShareAlike
licensing:

- https://en.wiktionary.org/wiki/Wiktionary:Copyrights#Creative_Commons_Attribution-ShareAlike_4.0_International_License

Scinoephile can build from local Kaikki JSONL snapshots under
`scinoephile/data/dictionaries/wiktionary/`, or from an explicit
`--source-jsonl-path` during `dictionary build wiktionary`.
