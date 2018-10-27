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

#templates_path = ["_templates"]
source_suffix = [".rst", ".md"]
master_doc = "index"
language = None
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"
#html_theme = "alabaster"
html_theme        = "sphinx_rtd_theme"
#html_static_path = ["_static"]
htmlhelp_basename = "scinoephile"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
]
#intersphinx_mapping = {"https://docs.python.org/": None}
