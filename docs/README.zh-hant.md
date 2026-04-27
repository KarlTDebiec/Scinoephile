[![Python: =3.13](https://img.shields.io/badge/python-3.13-green.svg)](https://docs.python.org/3/whatsnew/3.13.html)
[![Build](https://github.com/KarlTDebiec/Scinoephile/actions/workflows/build.yml/badge.svg)](https://github.com/KarlTDebiec/Scinoephile/actions/workflows/build.yml)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: BSD 3-Clause](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

[English](/README.md) | [繁體中文](/docs/README.zh-hant.md) | [简体中文](/docs/README.zh-hans.md)

Scinoephile 是一個用於處理中英文雙語字幕的套件，重點在於將分開的中文和英文字幕合併為同步的雙語字幕。

## 功能

- **雙語字幕同步**：將兩條字幕序列（例如中文 + 英文）合併為同一條上下行對齊的字幕
- **時間軸調整**：平移與拉伸一條字幕序列的時間軸以匹配另一條
- **按語言的工具**：
  - **英文**：英文字幕的後處理與編輯流程
  - **標準中文**：標準中文字幕的後處理與編輯流程
  - **書面粵語**：書面粵語字幕的處理流程（必要時可結合標準中文）
- **詞典工具**：建置與查詢中文詞典資源，以支援下游處理

## 安裝

Scinoephile 目標 Python 3.13，並使用 `uv` 進行開發與安裝。

```bash
git clone https://github.com/KarlTDebiec/Scinoephile
cd Scinoephile
uv sync
```

## 使用方法

透過 `uv run` 執行命令列：

```bash
uv run scinoephile --help
```

子命令：

- `analysis`：分析字幕
- `dictionary`：建置或查詢中文詞典
- `eng`：修改英文字幕
- `sync`：將兩條字幕合併為上下行同步字幕
- `timewarp`：平移並拉伸時間軸以匹配另一條字幕
- `yue`：修改書面粵語字幕
- `zho`：修改標準中文字幕

查看某個子命令的說明：

```bash
uv run scinoephile sync --help
```

## 開發

執行測試：

```bash
cd test
uv run pytest
```
