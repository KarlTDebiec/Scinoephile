#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interfaces for proofreading audits.

Package hierarchy (modules may import from any above):
* audit_review_report_cli / audit_review_run_cli / audit_review_serve_cli
* audit_review_cli
"""

from __future__ import annotations

from .audit_review_cli import AuditReviewCli

__all__ = ["AuditReviewCli"]
