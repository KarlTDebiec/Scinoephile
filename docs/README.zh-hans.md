[![Python: =3.13](https://img.shields.io/badge/python-3.13-green.svg)](https://docs.python.org/3/whatsnew/3.13.html)
[![Build](https://github.com/KarlTDebiec/Scinoephile/actions/workflows/build.yml/badge.svg)](https://github.com/KarlTDebiec/Scinoephile/actions/workflows/build.yml)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: BSD 3-Clause](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

[English](/README.md) | [繁體中文](/docs/README.zh-hant.md) | [简体中文](/docs/README.zh-hans.md)

Scinoephile 是一个用于处理中英文双语字幕的套件，重点在于将分开的中文和英文字幕合并为同步的双语字幕。

## 功能

- **双语字幕同步**：将两条字幕序列（例如中文 + 英文）合并为同一条上下行对齐的字幕
- **时间轴调整**：平移与拉伸一条字幕序列的时间轴以匹配另一条
- **按语言的工具**：
  - **英文**：英文字幕的后处理与编辑流程
  - **标准中文**：标准中文字幕的后处理与编辑流程
  - **书面粤语**：书面粤语字幕的处理流程（必要时可结合标准中文）
- **词典工具**：构建与查询中文词典资源，以支持下游处理

## 安装

Scinoephile 目标 Python 3.13，并使用 `uv` 进行开发与安装。

```bash
git clone https://github.com/KarlTDebiec/Scinoephile
cd Scinoephile
uv sync
```

## 使用方法

通过 `uv run` 运行命令行：

```bash
uv run scinoephile --help
```

子命令：

- `analysis`：分析字幕
- `dictionary`：构建或查询中文词典
- `eng`：修改英文字幕
- `sync`：将两条字幕合并为上下行同步字幕
- `timewarp`：平移并拉伸时间轴以匹配另一条字幕
- `yue`：修改书面粤语字幕
- `zho`：修改标准中文字幕

查看某个子命令的帮助：

```bash
uv run scinoephile sync --help
```

## 开发

运行测试：

```bash
cd test
uv run pytest
```
