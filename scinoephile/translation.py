#!/usr/bin/env python3
#   scinoephile.translation.__init__.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from google.cloud import translate_v2

################################## VARIABLES ##################################

translate_client = translate_v2.Client()
