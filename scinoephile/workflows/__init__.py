#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reusable workflows that coordinate operations across package domains.

Package hierarchy (modules may import from any above):
* cache_registry / helpers / ocr_fusion / ocr_validation / prompt_catalog
  / subtitle_extraction
* clean / flatten / review / romanize / transcription / transcription_alignment
  / translation
* multisource_transcription / ocr_processing
* transcription_pipeline
"""
