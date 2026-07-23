#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interfaces for subtitle audits.

Package hierarchy (modules may import from any above):
* audit_cli_base
* audit_delineation_cli / audit_ocr_fusion_cli / audit_punctuation_cli
/ audit_translation_cli / utils
* audit_review_cli / audit_review_dual_cli
/ audit_review_trad_cli
* audit_cli
"""

from .audit_cli import AuditCli

__all__ = ["AuditCli"]
