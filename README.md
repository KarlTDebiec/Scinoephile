[![Python: =3.13](https://img.shields.io/badge/python-3.13-green.svg)](https://docs.python.org/3/whatsnew/3.13.html)
[![Build](https://github.com/KarlTDebiec/Scinoephile/actions/workflows/build.yml/badge.svg)](https://github.com/KarlTDebiec/Scinoephile/actions/workflows/build.yml)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: BSD 3-Clause](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

[English](/README.md) | [繁體中文](/docs/README.zh-hant.md) | [简体中文](/docs/README.zh-hans.md) | [繁體粵文](/docs/README.yue-hant.md) | [简体粤文](/docs/README.yue-hans.md)

Scinoephile is a package for working with Chinese/English bilingual subtitles, with a 
focus on combining separate Chinese and English subtitles into synchronized bilingual
subtitles.

## Dictionaries

Scinoephile's dictionary CLI can now build and search local CUHK and GZZJ
SQLite dictionaries.

- `dictionary build cuhk` scrapes the CUHK source site into a local database.
- `dictionary build gzzj --source-json-path /path/to/B01_資料.json` builds GZZJ
  from a manually downloaded upstream JSON file.
- `dictionary search QUERY` searches all locally available dictionaries by
  default. Use `--dictionary-name` to limit the search to one source.

## Notices

Third-party license and data-source acknowledgements are listed in
`docs/THIRD_PARTY_NOTICES.md`.
