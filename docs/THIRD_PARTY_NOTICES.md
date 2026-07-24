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

## SubtitleEdit (adapted OCR preprocessing, grouping, and cleanup logic)

Scinoephile's PaddleOCR preprocessing and text grouping code, selected Google
Lens OCR text cleanup behavior, and Tesseract OCR preprocessing and hOCR parsing
code are informed by and partially adapted from the `SubtitleEdit` project:

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

## vs_align (adapted video alignment logic)

Scinoephile's visual video offset detection code is informed by and partially
adapted from the `vs_align` project:

- Project: https://github.com/pifroggi/vs_align
- License: MIT
- Copyright: Copyright (c) 2024, pifroggi

The `vs_align` license permits use, modification, and distribution, provided the
copyright and permission notice are included in copies or substantial portions
of the software.

For the complete license text used by `vs_align`, see:

- https://github.com/pifroggi/vs_align/blob/main/LICENSE

MIT license text (from `vs_align`):

```text
MIT License

Copyright (c) 2024, pifroggi

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

## MLX-Audio (MiMo inference runtime)

Scinoephile's optional transcription dependencies install MLX-Audio's MiMo
support from a pinned source revision. The dependency is enabled only on Apple
Silicon, which is the platform supported by Scinoephile's MiMo runtime.

- Upstream project: https://github.com/Blaizzy/mlx-audio
- MiMo source revision:
  https://github.com/ailuntx/mlx-audio/tree/ff0197c0ae9f9fd02072904c696f2533e329c06e
- License: MIT
- Copyright: Copyright (c) 2024 Prince Canuma

The `MLX-Audio` license permits use, modification, and distribution, provided
the copyright and permission notice are included in copies or substantial
portions of the software.

For the complete license text used by the pinned `MLX-Audio` revision, see:

- https://github.com/ailuntx/mlx-audio/blob/ff0197c0ae9f9fd02072904c696f2533e329c06e/LICENSE

MIT license text (from `MLX-Audio`):

```text
MIT License

Copyright (c) 2024 Prince Canuma

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

## WhisperX (forced-alignment reference interface and result handling)

Scinoephile's MiMo forced-alignment adapter and optional alignment worker use
WhisperX's alignment API and alignment-result schema as the reference interface.
The Scinoephile conversion and validation code is in-house, but it intentionally
accepts WhisperX-style segment and word payloads.

- Project: https://github.com/m-bain/whisperX
- License: BSD 2-Clause
- Copyright: Copyright (c) 2024, Max Bain

The `WhisperX` license permits use, modification, and distribution, provided the
copyright notice, license conditions, and disclaimer are retained or reproduced
as required by the license.

For the complete license text used by `WhisperX`, see:

- https://github.com/m-bain/whisperX/blob/main/LICENSE

BSD 2-Clause license text (from `WhisperX`):

```text
BSD 2-Clause License

Copyright (c) 2024, Max Bain

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

## TorchAudio forced-alignment tutorial (adapted CTC trellis logic)

Scinoephile's in-house CTC aligner is informed by and partially adapted from the
TorchAudio forced-alignment tutorial's trellis construction, backtracking, and
repeat-merge flow. Scinoephile rewrites that logic around NumPy arrays, Hugging
Face CTC models, Cantonese character tokenization, punctuation fallback, and the
project's `TranscribedSegment` / `TranscribedWord` data model.

- Project: https://github.com/pytorch/audio
- Tutorial source:
  https://github.com/pytorch/audio/blob/main/examples/tutorials/forced_alignment_tutorial.py
- License: BSD 2-Clause
- Copyright: Copyright (c) 2017 Facebook Inc. (Soumith Chintala), All rights
  reserved.
- Tutorial author: Moto Hira

The `TorchAudio` license permits use, modification, and distribution, provided
the copyright notice, license conditions, and disclaimer are retained or
reproduced as required by the license.

For the complete license text used by `TorchAudio`, see:

- https://github.com/pytorch/audio/blob/main/LICENSE

BSD 2-Clause license text (from `TorchAudio`):

```text
BSD 2-Clause License

Copyright (c) 2017 Facebook Inc. (Soumith Chintala),
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

## htmx (vendored web UI runtime)

Scinoephile vendors the HTMX runtime for the OCR validation web UI:

- Project: https://github.com/bigskysoftware/htmx
- Package: https://www.npmjs.com/package/htmx.org/v/2.0.4
- Vendored file: `scinoephile/web/ocr_validation/static/htmx.min.js`
- License: 0BSD

The HTMX package metadata for version 2.0.4 identifies the package license as
0BSD.

For the complete license text used by HTMX, see:

- https://unpkg.com/htmx.org@2.0.4/LICENSE

0BSD license text (from HTMX 2.0.4):

```text
Zero-Clause BSD
=============

Permission to use, copy, modify, and/or distribute this software for
any purpose with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE
FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY
DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
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
