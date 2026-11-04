[![Python: =3.14](https://img.shields.io/badge/python-3.14-green.svg)](https://docs.python.org/3/whatsnew/3.14.html)
[![Build](https://github.com/KarlTDebiec/Scinoephile/actions/workflows/build.yml/badge.svg)](https://github.com/KarlTDebiec/Scinoephile/actions/workflows/build.yml)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: BSD 3-Clause](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

[English](/README.md) | [繁體中文](/docs/README.zh-hant.md) | [简体中文](/docs/README.zh-hans.md) | [繁體粵文](/docs/README.yue-hant.md) | [简体粤文](/docs/README.yue-hans.md)

Scinoephile 是一個用於處理中英文雙語字幕的套件，重點在於將分開的中文和英文字幕合併為同步的雙語字幕。

## 安裝

使用 Python 3.14 和 uv。OCR 需要從原始碼編譯 Paddle；CPU 與 Windows CUDA 環境的設定請參閱
[Paddle 原始碼編譯指南](PADDLE_SOURCE.md)。
