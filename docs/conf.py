#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.Compositor.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import sphinx_rtd_theme
################################ CONFIGURATION ################################

project = "scinoephile"
copyright = "2017-2018, Karl T Debiec"
author = "Karl T Debiec"
version = "0.1.0"
release = "0.1.0"

source_suffix = [".rst", ".md"]
master_doc = "index"
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "default"

html_theme = "sphinx_rtd_theme"
htmlhelp_basename = "scinoephile"
html_show_sphinx = False
html_show_sourcelink = False
html_context = dict(
    display_github = True,
    github_user    = "KarlTDebiec",
    github_repo    = "scinoephile",
    github_version = "master",
    conf_py_path  = "/docs/",
)

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
]
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": None,
    "show-inheritance": None,
}
todo_include_todos = False
