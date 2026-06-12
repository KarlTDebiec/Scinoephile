#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to interactions with LLMs.

This module may import from: common, core

Hierarchy within module, where lower entries may import from higher entries:
* default_test_cases / dual_1_to_1 / dual_2_to_2 / dual_n_minus_m_to_n
  / dual_n_to_1 / dual_n_to_m / dual_n_to_n / mono_n / providers

LLM shapes:

| Tracks | T1    | T2   | Name                  | Prefix         | Description        |
| ------ | ----- | ---- | --------------------- | -------------- | ------------------ |
| 1      | n     | none | mono_n                | MonoN          | One track.         |
| 2      | 1     | 1    | dual_1_to_1           | Dual1To1       | Paired subs.       |
| 2      | n     | 1    | dual_n_to_1           | DualNTo1       | n to one.          |
| 2      | 2     | 2    | dual_2_to_2           | Dual2To2       | Two pairs.         |
| 2      | n     | n    | dual_n_to_n           | DualNToN       | Matched blocks.    |
| 2      | n - m | n    | dual_n_minus_m_to_n   | DualNMinusMToN | Fill gaps.         |
| 2      | n     | m    | dual_n_to_m           | DualNToM       | Independent sizes. |
"""
