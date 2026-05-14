[![Python: =3.13](https://img.shields.io/badge/python-3.13-green.svg)](https://docs.python.org/3/whatsnew/3.13.html)
[![Build](https://github.com/KarlTDebiec/Scinoephile/actions/workflows/build.yml/badge.svg)](https://github.com/KarlTDebiec/Scinoephile/actions/workflows/build.yml)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: BSD 3-Clause](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

[English](/README.md) | [繁體中文](/docs/README.zh-hant.md) | [简体中文](/docs/README.zh-hans.md) | [繁體粵文](/docs/README.yue-hant.md) | [简体粤文](/docs/README.yue-hans.md)

Scinoephile 是一个用于处理中英文双语字幕的套件，重点在于将分开的中文和英文字幕合并为同步的双语字幕。

## 安装

默认安装不包含较重的 ML 和 API 运行时依赖。按需要安装功能 extras：

```bash
pip install scinoephile
pip install 'scinoephile[ocr]'
pip install 'scinoephile[llm]'
pip install 'scinoephile[transcription]'
pip install 'scinoephile[transcription,demucs]'
```
