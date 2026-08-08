# Third-Party Notices

## pyannote speaker-diarization-3.0 (speaker diarization model)

Scinoephile can download and run the `speaker-diarization-3.0` speaker diarization
pipeline locally after the user accepts its Hugging Face access conditions. The
model is not bundled with Scinoephile.

- Model: https://huggingface.co/pyannote/speaker-diarization-3.0
- Pinned revision:
  https://huggingface.co/pyannote/speaker-diarization-3.0/tree/61bc5e801239695154ba03562a72e1d6254ed4e4
- License: MIT
- Project: https://github.com/pyannote/pyannote-audio

The model license permits use, modification, and distribution, provided the
copyright and permission notice are included in copies or substantial portions
of the software. For the complete license terms, see:

- https://huggingface.co/pyannote/speaker-diarization-3.0/blob/61bc5e801239695154ba03562a72e1d6254ed4e4/LICENSE

## pyannote speaker-diarization-community-1 (PLDA assets)

When Scinoephile runs `speaker-diarization-3.0` through pyannote.audio 4, it
downloads the PLDA clustering assets from `speaker-diarization-community-1`.
Scinoephile pins the asset revision and does not bundle the files. Users must
separately accept the repository's Hugging Face access conditions.

- Model: https://huggingface.co/pyannote/speaker-diarization-community-1
- Pinned revision:
  https://huggingface.co/pyannote/speaker-diarization-community-1/tree/3533c8cf8e369892e6b79ff1bf80f7b0286a54ee
- License: Creative Commons Attribution 4.0 International (CC BY 4.0)

The model license permits sharing and adaptation with attribution. For the
complete license terms, see:

- https://creativecommons.org/licenses/by/4.0/legalcode

## WeSpeaker VoxCeleb ResNet34-LM (speaker embedding model)

The pinned `speaker-diarization-3.0` configuration uses the WeSpeaker
VoxCeleb ResNet34-LM model to generate speaker embeddings. Scinoephile pins the
model revision and does not bundle its files.

- Model: https://huggingface.co/hbredin/wespeaker-voxceleb-resnet34-LM
- Pinned revision:
  https://huggingface.co/hbredin/wespeaker-voxceleb-resnet34-LM/tree/0ae88dcaf48cacdf741275d6d1a8101f45eee220
- License: Apache License 2.0

For the complete license terms, see:

- https://huggingface.co/hbredin/wespeaker-voxceleb-resnet34-LM/blob/0ae88dcaf48cacdf741275d6d1a8101f45eee220/LICENCE.md

## TEN VAD (optional user-installed voice activity detector)

Scinoephile can use the official TEN VAD Python runtime when users install it
separately. Scinoephile does not distribute TEN VAD source, native libraries, or
model artifacts and does not install them through an optional dependency.

- Project: https://github.com/TEN-framework/ten-vad
- License: Apache License 2.0 with additional conditions
- Copyright: Copyright © 2025 Agora

The additional conditions restrict deployments that compete with Agora's
offerings and limit deployment to applications for the user's and their direct
end users' benefit. Review the complete upstream terms before installing or
using TEN VAD:

- https://github.com/TEN-framework/ten-vad/blob/main/LICENSE

After accepting those terms, install the tested upstream revision separately:

```shell
uv pip install "ten-vad @ git+https://github.com/TEN-framework/ten-vad.git@22a3bcd4509d0faaa8eef4881e8af5f39c178950"
```

Select it with `--vad on --vad-implementation ten` (or use `--vad auto` to
retain the non-VAD fallback).

TEN VAD cache identities record the installed distribution version, installed
runtime artifact digest, and the PEP 610 source URL and Git commit when available.
Silero uses the Whisper Timestamped-compatible `v6.2` model tag and records both
the installed adapter and cached model artifact digests. When an exact runtime
or model artifact cannot be identified, Scinoephile disables cross-process VAD
cache reuse rather than risk reusing stale output.

## pyannote segmentation-3.0 (voice activity detection model)

Scinoephile can download and run the `segmentation-3.0` model locally as an
optional voice activity detector after the user accepts its Hugging Face access
conditions. The model is not bundled with Scinoephile.

- Model: https://huggingface.co/pyannote/segmentation-3.0
- Pinned revision:
  https://huggingface.co/pyannote/segmentation-3.0/tree/e66f3d3b9eb0873085418a7b813d3b369bf160bb
- License: MIT
- Project: https://github.com/pyannote/pyannote-audio

The model license permits use, modification, and distribution, provided the
copyright and permission notice are included in copies or substantial portions
of the software. For the complete license terms, see:

- https://huggingface.co/pyannote/segmentation-3.0/blob/e66f3d3b9eb0873085418a7b813d3b369bf160bb/LICENSE

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

## MLX-Audio (speech-to-text inference runtime)

Scinoephile's optional transcription dependencies install MLX-Audio from a pinned
source revision. The dependency is enabled only on Apple Silicon, which is the
platform supported by Scinoephile's MLX-Audio runtime.

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
